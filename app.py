#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log
# For login with OAuth
import tornado.auth
import requests
from models import User, Currency, UserCurrency, Market

from dotenv import load_dotenv
from jinja2 import \
    Environment, PackageLoader, select_autoescape

# Access variables from the .env file
load_dotenv('.env')

ENV = Environment(
    loader=PackageLoader('dashboard', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
PORT = int(os.environ.get('PORT', '8080'))




class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

    def get_current_user(self):
        # Returns user's cookie, which is their unique id number
        return self.get_secure_cookie("crypto_user")


class MainHandler(TemplateHandler):
    def get(self):
        loggedInUser = False
        if self.current_user:
            loggedInUser = int(self.current_user)
        bitcoin = Currency.select().where(Currency.coin_pair == "USDT-BTC").get()
        # set bitcoin as variable in order to render the price on the index page.
        markets = Market.select().join(Currency).where(Currency.id == Market.currency_id).order_by(Currency.volume.desc()).limit(6)
        return self.render_template("index.html", {'markets': markets, "bitcoin": bitcoin, "loggedInUser": loggedInUser})

    def post(self):
        url = "https://bittrex.com/api/v1.1/public/getmarketsummary"
        coin = self.get_body_argument('ticker_symbol')
        querystring = {"market": "btc-" + coin}
        response = requests.post(url, params=querystring)
        self.render_template("index.html", {'data': response.json()})




class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        # This portion gets triggered second upon a person's first login
        # The authorization `code` in the URL that was returned from Google
        # allows for this statement to be true
        # Example URL:
        # http://example.com/login?code=4/GdQlpUVhfTvV6tReFLG6q9czdTd32NWn3wzC90dwlTc
        if self.get_argument('code', False):
            # Exchanges the authorization `code` for an access token
            access = yield self.get_authenticated_user(
                redirect_uri='http://localhost:8080/login',
                code=self.get_argument('code'))
            # After obtaining an access token, that token can be used to gain access to user info
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            # Retrieve user information
            email = user["email"]
            fname = user["given_name"]
            lname = user["family_name"]
            picture = user["picture"]
            # Check if user already exists in Users table
            user = User.select().where(User.email == email)
            # If user does not exist, insert user into Users table
            if not user:
                User.create(email=email,
                            fname=fname,
                            lname=lname,
                            picture=picture).save()
            # Get the user that is signing in
            user = User.select().where(User.email == email).get()
            # Signs and timestamps a cookie so it cannot be forged
            # User will not have to login again as long as cookie is not tampered with or deleted
            # Using user's unique id number as their cookie
            self.set_secure_cookie('crypto_user', str(user.id))
            # Redirect to user's dashbaord
            return self.redirect('/dashboard/{}'.format(user.id))

        # This portion actually gets triggered first upon a person's first login
        # An authorization `code` is returned from Google
        # A redirect is made to this same Loginhandler with that authorization code
        else:
            yield self.authorize_redirect(
                redirect_uri="http://localhost:8080/login",
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class LogoutHandler(TemplateHandler):
    """Logout handler"""
    def get(self):
        self.clear_cookie('crypto_user')
        return self.redirect('/')

# Create user dashboard handler
class DashboardHandler(TemplateHandler):
    # If a request goes to a method with this decorator,
    # and the user is not logged in, they will be
    # redirected to login_url in application setting
    @tornado.web.authenticated
    def get(self, slug):
        # get user's portfolio based off of slug in url
        # the slug in the URL is their unique ID number

        # Check UserCurrency table for all user_id that is same as slug

        # If UseCurrency has any results, display their preferences

        # if UserCurrency has no results, display random currencies at first
        bitcoin = Currency.select().where(Currency.coin_pair == "USDT-BTC").get()
        # set bitcoin as variable in order to render the price on the index page.
        markets = Market.select().join(Currency).where(Currency.id == Market.currency_id).order_by(
            Currency.volume.desc()).limit(6)
        self.render_template("dashboard.html", {'markets': markets, "bitcoin": bitcoin})

    def post(self):
        url = "https://bittrex.com/api/v1.1/public/getmarketsummary"
        coin = self.get_body_argument('ticker_symbol')
        if ticker_symbol =
        querystring = {"market": "btc-" + coin}
        response = requests.post(url, params=querystring)
        self.render_template("dashboard.html", {'data': response.json()})
        return self.render_template("dashboard.html", {})





class TableHandler (TemplateHandler):
    def get (self, ticker):
        response = requests.get('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-{}&type=both'.format(ticker))

        results = response.json()['result']
        return self.render_template("table.html", {'buy': results['buy'], 'sell': results['sell']})

settings = {
    "autoreload": True,
    "google_oauth": {"key": os.environ["CLIENT_ID"], "secret": os.environ["CLIENT_SECRET"]},
    "cookie_secret": os.environ["COOKIE_SECRET"],
    "login_url": "/"
    }


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/dashboard/(.*)", DashboardHandler),
        (r"/table/(.*)", TableHandler),
        (r"/static/(.*)",
         tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT, print('Creating app on port: ' + str(PORT)))
    tornado.ioloop.IOLoop.current().start()
