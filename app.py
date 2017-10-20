#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log
import requests


from jinja2 import \
    Environment, PackageLoader, select_autoescape

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


    def post(self):
        url = "https://bittrex.com/api/v1.1/public/getmarketsummary"
        coin = self.get_body_argument('ticker_symbol')
        querystring = {"market": "btc-" + coin}

        response = requests.post(url, params=querystring)

        print(response.json())
        self.render_template("index.html", {'data': response.json()})



# class PageHandler(TemplateHandler):
#       def get(self, page):
#         self.set_header(
#           'Cache-Control',
#           'no-store, no-cache, must-revalidate, max-age=0')
#         self.render_template(page + '.html', {})


class ParsedDataHandler(TemplateHandler):
        def get(self, page):
                self.set_header(
                  'Cache-Control',
                  'no-store, no-cache, must-revalidate, max-age=0')
                self.render_template('data_parser.html', {})

        def orderbook(self):
            url = "https://bittrex.com/api/v1.1/public/getorderbook"

            querystring = {"market": "BTC-LTC", "type": "both"}

            headers = {
                'cache-control': "no-cache",
                'postman-token': "1700863e-c007-79df-6a9b-bc985f2ff94d"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)

            self.render_template('data_parser.html', {})


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        # (r"/page/(.*)", PageHandler),
        (r"/data_parser(.*)", ParsedDataHandler),
        (r"/static/(.*)",
         tornado.web.StaticFileHandler, {'path': 'static'}),
    ], autoreload=True)

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()

app = make_app()
app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
tornado.ioloop.IOLoop.current().start()