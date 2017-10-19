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

# Access variables from the .env file
load_dotenv('.env')

ENV = Environment(
    loader=PackageLoader('dashboard', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))


class MainHandler(TemplateHandler):
    def get(self):
        self.render_template("base.html", {})


class PageHandler(TemplateHandler):
    def get(self, page):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        self.render_template(page + '.html', {})


class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    # Paul's source code hack to bypass SSL Certificate Validation
    # This portion can be removed once application is in production
    @tornado.auth._auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        http = self.get_auth_http_client()
        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
            "client_secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
            "grant_type": "authorization_code",
        })

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                   functools.partial(self._on_access_token, callback),
                   method="POST", headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=body, validate_cert = False)

    # Paul's source code hack to bypass SSL Certificate Validation
    # This portion can be removed once application is in production
    @tornado.auth._auth_return_future
    def oauth2_request(self, url, callback, access_token=None,
                       post_args=None, **args):
        all_args = {}
        if access_token:
            all_args["access_token"] = access_token
            all_args.update(args)

        if all_args:
            url += "?" + urllib_parse.urlencode(all_args)
        callback = functools.partial(self._on_oauth2_request, callback)
        http = self.get_auth_http_client()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib_parse.urlencode(post_args),
                       callback=callback, validate_cert = False)
        else:
            http.fetch(url, callback=callback, validate_cert = False)


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
        (r"/login", LoginHandler),
        (r"/page/(.*)", PageHandler),
        (r"/static/(.*)",
         tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)


PORT = int(os.environ.get('PORT', '1337'))

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
    tornado.ioloop.IOLoop.current().start()
