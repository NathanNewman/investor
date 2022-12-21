import datetime
import requests
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from key import api_key, api_url, api_query

bcrypt = Bcrypt()
db = SQLAlchemy()


class Stock(db.Model):

    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(
        db.Text
    )
    price = db.Column(
        db.Float,
        nullable=False,
        default=0.00
    )
    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    update_date = db.Column(
        db.Date,
        nullable=True
    )

    portfolio_id = db.Column(
        db.Integer,
        db.ForeignKey('portfolios.id', ondelete='cascade')
    )

    def update(self):
        symbol = self.symbol
        today = datetime.date.today()
        if self.update_date == today:
            return self.price
        url = api_url + symbol + api_query + api_key
        r = requests.get(url)
        data = r.json()
        gq = data["Global Quote"]
        price = gq["05. price"]
        stocks = Stock.query.filter_by(symbol=symbol)
        for stock in stocks:
            stock.price = price
            stock.update_date = today
        db.session.commit()
        return price

    @classmethod
    def updated_stocks(cls):
        today = datetime.date.today()
        stocks = cls.query.filter_by(update_date=today)
        symbols = []
        for stock in stocks:
            symbols.append(stock.symbol)
        symbols = set(symbols)
        updated_stocks = []
        for symbol in symbols:
            stock = cls.query.filter_by(symbol=symbol).limit(1)
            updated_stocks.append(stock[0])
        print(updated_stocks)
        return updated_stocks


class Portfolio(db.Model):

    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Text,
        unique=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now
    )
    cash = db.Column(
        db.Float,
        nullable=False,
        default=10000
    )

    net_worth = db.Column(
        db.Float,
        nullable=False,
        default=10000
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    stocks = db.relationship('Stock', backref='portfolios',
                             cascade='all, delete-orphan')

    def update_net_worth(self):
        cash = float(self.cash)
        for stock in self.stocks:
            stock.update()
            quantity = stock.quantity
            price = stock.price
            total = cash + (quantity * price)
        self.net_worth = round(total, 2)
        db.session.commit()
        return round(total, 2)

    def friendly_date(self):
        date = self.created_at
        friendly = date.strftime("%b %d, %Y")
        return friendly


class User(db.Model):
    """User in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True
                   )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png"
    )

    bio = db.Column(
        db.Text
    )

    portfolios = db.relationship(
        'Portfolio', backref='users', cascade='all, delete-orphan')

    @staticmethod
    def encrypt_password(password):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        return hashed_pwd

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):

    db.app = app
    db.init_app(app)
