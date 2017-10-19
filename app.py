#!/usr/bin/env python3
import os
import urllib.parse as urllib_parse
import functools

import tornado.ioloop
import tornado.web
import tornado.log
# For login with OAuth
import tornado.auth
from tornado import httpclient

from dotenv import load_dotenv
from jinja2 import \
    Environment, PackageLoader, select_autoescape

<<<<<<< HEAD
# Access variables from the .env file
load_dotenv('.env')

=======
>>>>>>> 676bb8dccf1656af053206b45b56d142461dfbfa
ENV = Environment(
    loader=PackageLoader('dashboard', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
PORT = int(os.environ.get('PORT', '1337'))

class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))


class MainHandler(TemplateHandler):
    def get(self):
        self.render_template("index.html", {})


<<<<<<< HEAD
class PageHandler(TemplateHandler):
    def get(self, page):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        self.render_template(page + '.html', {})
=======
# class PageHandler(TemplateHandler):
#       def get(self, page):
#         self.set_header(
#           'Cache-Control',
#           'no-store, no-cache, must-revalidate, max-age=0')
#         self.render_template(page + '.html', {})
>>>>>>> 676bb8dccf1656af053206b45b56d142461dfbfa


class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        # This portion gets triggered second apon a person's first login
        # The authorization `code` in the URL that was returned from Google
        # allows for this statement to be true
        # Example URL:
        # http://example.com/login?code=4/GdQlpUVhfTvV6tReFLG6q9czdTd32NWn3wzC90dwlTc 
        if self.get_argument('code', False):
            # Exchanges the authorization `code` for an access token
            access = yield self.get_authenticated_user(
                redirect_uri='http://localhost:1337/login',
                code=self.get_argument('code'))
            # After obtaining an access token, that token can be used to gain access to user info 
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])

            # Retrieve user information
            email = user["email"]
            name = user["name"]
            picture = user["picture"]
            # Check if user already exists in Users table

            # If user does not exist, insert user into Users table


            # Signs and timestamps a cookie so it cannot be forged
            # User will not have to login again as long as cookie is not tampered with or deleted 
            self.set_secure_cookie('crypto_user', user['email']) 
            self.redirect('/')
            return

        elif self.get_secure_cookie('crypto_user'):
            self.redirect('/')
            return

        # This portion actually gets triggered first apon a person's first login
        # An authorization `code` is returned from Google
        # A redirect is made to this same Loginhandler with that authorization code
        else:
            yield self.authorize_redirect(
                redirect_uri="http://localhost:1337/login",
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


settings = {
    "autoreload": True,
    "google_oauth": {"key": os.environ["CLIENT_ID"], "secret": os.environ["CLIENT_SECRET"]},
    "cookie_secret": os.environ["COOKIE_SECRET"],
}

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
<<<<<<< HEAD
        (r"/login", LoginHandler),
        (r"/page/(.*)", PageHandler),
=======
        # (r"/page/(.*)", PageHandler),
>>>>>>> 676bb8dccf1656af053206b45b56d142461dfbfa
        (r"/static/(.*)",
         tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)


<<<<<<< HEAD
PORT = int(os.environ.get('PORT', '1337'))

=======
>>>>>>> 676bb8dccf1656af053206b45b56d142461dfbfa
if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
    tornado.ioloop.IOLoop.current().start()
