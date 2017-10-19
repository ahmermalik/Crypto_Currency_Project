#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log

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


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)",
         tornado.web.StaticFileHandler, {'path': 'static'}),
    ], autoreload=True)

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()

app = make_app()
app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
tornado.ioloop.IOLoop.current().start()
