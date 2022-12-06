import os

from flask import Flask, render_template, redirect, session, g, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import connect_db, User, db
from forms import NewUserForm, LoginForm, EditUserForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///investor'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
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
    return redirect('/about')


@app.route('/about')
def about():
    render_template('/base.html')
    return render_template('/about.html')


###################################################################################################
# User Profile

@app.route('/user/<user_id>')
def user_profile(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = ''.join(filter(str.isdigit, user_id))
    user_id = int(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('/users/profile.html', user=user)

@app.route('/user/edit/<int:user_id>', methods=["GET", "POST"])
def edit_profile(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = int(user_id)
    user = User.query.get_or_404(user_id)

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        try:
            User.authenticate(form.username.data,form.password.data)
            user.id=user_id
            user.email=form.email.data
            user.username=form.username.data
            user.image_url=form.image_url.data
            user.bio=form.bio.data
            db.session.commit()
            return redirect('/')

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
