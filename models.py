import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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
        nullable=False
    )
    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    portfolio_id = db.Column(
        db.Integer,
        db.ForeignKey('portfolios.id', ondelete='cascade')
    )


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
        db.Integer,
        nullable=False,
        default=10000
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    stocks = db.relationship('Stock', backref='portfolios',
                             cascade='all, delete-orphan')


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

    portfolios = db.relationship('Portfolio', backref='users', cascade='all, delete-orphan')

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
