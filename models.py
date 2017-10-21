import datetime
import os
import peewee
from playhouse.db_url import connect
import markdown2


DB = connect(
    os.environ.get(                                         #how to connect the blog database to the server
        'DATABASE_URL',
        'postgres://localhost:5432/crypto_database'
    )
)

class BaseModel(peewee.Model):
    """your base model will always stay the same. all the other tables will inhert from this."""
    class Meta:
        database = DB

class User(BaseModel):
    fname = peewee.CharField(max_length=60)
    lname = peewee.CharField(max_length=60)
    email = peewee.CharField(max_length=60)
    picture = peewee.CharField()

    def __str__(self):
        return self.name


class Currency(BaseModel):
    """This will create the currency table with its respective details"""
    coin_pair = peewee.CharField(max_length=10)
    day_high = peewee.DecimalField()
    day_low = peewee.DecimalField()
    volume = peewee.FloatField()
    last_price = peewee.FloatField()
    base_volume = peewee.FloatField()
    bid_price = peewee.FloatField()
    ask_price = peewee.FloatField()
    open_buy = peewee.FloatField()
    open_sell = peewee.FloatField()
    prev_day = peewee.FloatField()

    def __str__(self):
        return self.coin_name

class Market(BaseModel):
    coin_ticker = peewee.CharField(max_length=5)
    coin_base = peewee.CharField(max_length=5)
    coin_name = peewee.CharField(max_length= 15)
    coin_active = peewee.CharField(max_length=8)
    coin_created = peewee.DateTimeField()
    coin_logo = peewee.CharField()

    def __str__(self):
        return self.coin_ticker

class UserCurrency(BaseModel):
    """This table creates relations between user & currency classes"""
    user = peewee.ForeignKeyField(User, null=True)
    currency = peewee.ForeignKeyField(Currency, null=True)


