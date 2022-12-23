import os
import requests
import datetime

from flask import Flask, render_template, redirect, session, g, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import connect_db, User, db, Portfolio, Stock
from forms import NewUserForm, LoginForm, EditUserForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///investor'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


@app.route('/logout')
def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    return redirect('/')


@app.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():

    form = NewUserForm()

    if form.validate_on_submit():
        try:
            password = User.encrypt_password(form.password.data)
            user = User(
                email=form.email.data,
                username=form.username.data,
                password=password
            )
            db.session.add(user)
            db.session.commit()
            do_login(user)
            return redirect('/')

        except IntegrityError:
            flash("Username already taken")
            return render_template('users/signup.html')

    else:
        return render_template('users/signup.html', form=form)

#################################################################################################
# homepage


@app.route('/')
def redirect_about():
    return redirect('/portfolios/leaderboard')


@app.route('/about')
def about():
    return render_template('/about.html')


###################################################################################################
# User Profiles

@app.route('/user/<user_id>')
def user_profile(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    portfolios = Portfolio.query.filter(Portfolio.user_id == user_id)
    return render_template('/users/profile.html', user=user, portfolios=portfolios)


@app.route('/user/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = int(user_id)
    user = User.query.get_or_404(user_id)

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.id = user_id
        user.email = form.email.data
        user.username = form.username.data
        user.image_url = form.image_url.data
        user.bio = form.bio.data
        try:
            User.authenticate(form.username.data, form.password.data)
            db.session.commit()
            return redirect(f'/user/{user_id}')

        except IntegrityError:
            flash("Username already taken")
            return render_template('users/signup.html')

    else:
        return render_template('users/edit.html', form=form, user=user)


@app.route('/search', methods=["POST"])
def search_users():

    search = request.form['query']

    if not search:
        users = User.query.limit(10)
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/search.html', users=users)


@app.route('/user/<int:user_id>/delete')
def delete_user(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    for portfolio in user.portfolios:
        for stock in portfolio.stocks:
            db.session.delete(stock)
        db.session.delete(portfolio)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

###############################################################################################################
# Portfolios and Stocks


@app.route('/user/create-portfolio', methods=["Post"])
def new_portfolio():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    name = request.form["portfolio-name"]
    userId = session[CURR_USER_KEY]

    portfolio = Portfolio(
        name=name,
        user_id=userId
    )
    db.session.add(portfolio)
    db.session.commit()

    return redirect(f"/user/{userId}")


@app.route('/portfolios/<int:port_id>')
def portfolio(port_id):

    portfolio = Portfolio.query.get_or_404(port_id)
    return render_template('/portfolios/portfolio.html', portfolio=portfolio)


@app.route('/portfolios/<int:port_id>/edit', methods=["GET", "POST"])
def edit_portfolio(port_id):

    if request.method == "POST":
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        portfolio = Portfolio.query.get_or_404(port_id)

        portfolio.cash = request.form["cash"]

        for stock in portfolio.stocks:
            quantity = request.form[f"{stock.symbol}"]
            quantity = int(quantity)
            if quantity == 0:
                db.session.delete(stock)
            else:
                stock.quantity = quantity

        portfolio.update_net_worth()
        db.session.commit()
        return redirect(f'/portfolios/{portfolio.id}/edit')

    else:
        portfolio = Portfolio.query.get_or_404(port_id)
        for stock in portfolio.stocks:
            stock.update()
        stocks = Stock.updated_stocks()
        return render_template('/portfolios/edit.html', portfolio=portfolio, stocks=stocks)


@app.route('/portfolios/get-stock', methods=["POST"])
def get_stock():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    symbol = request.form['stock-search']
    port_id = request.form['portfolio-id']
    stock = Stock(
        symbol=symbol,
        portfolio_id=port_id,
    )
    db.session.add(stock)
    db.session.commit()
    try:
        simStock = Stock.query.filter_by(symbol=symbol).first()
        today = datetime.date.today()
        if simStock.update_date == today:
            stock.price = simStock.price
            stock.update_date = today
            db.session.commit()
        else:
            stock.update()
        return redirect(f'/portfolios/{port_id}/edit')
    except:
        stock.update()
        return redirect(f'/portfolios/{port_id}/edit')
    finally:
        flash("stock symbol does not exist")
        return redirect(f'/portfolios/{port_id}/edit')


@app.route("/portfolios/leaderboard")
def leaderboard():
    portfolios = Portfolio.query.order_by(
        Portfolio.net_worth.desc()).limit(10)
    return render_template('/portfolios/leaders.html', portfolios=portfolios)


@app.route("/portfolios/<int:port_id>/delete")
def delete_portfolio(port_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    portfolio = Portfolio.query.get_or_404(port_id)

    for stock in portfolio.stocks:
        db.session.delete(stock)

    db.session.delete(portfolio)
    db.session.commit()
    return redirect(f"/user/{g.user.id}")
