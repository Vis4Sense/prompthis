import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

import modules
from modules.processors import processors

app_logger = logging.getLogger(__name__)

define("port", default=5707, help = "run on the given port", type = int)
define("show", default=False, help = "run on the given port", type = bool)


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get_argument(self, arg, required=True, arg_type=str):
        data = tornado.escape.json_decode(self.request.body)
        if arg in data:
            return data[arg]
        elif not required:
            return None
        raise tornado.web.HTTPError(400, f"Missing argument: {arg}")


def get_preprocess_handlers():
    handlers = []

    def register_handler(name):
        def decorator(cls):
            handlers.append((f"/{name}", cls))
            return cls
        return decorator

    def register_preprocess_handler(name, processor):
        @register_handler(name)
        class PreprocessHandler(BaseHandler):
            def post(self):
                input_data = self.get_argument("input", required=True)
                config = self.get_argument("config", required=True)
                preprocessor = processor(input_data, config)
                output_data = preprocessor.process()
                response = {
                    "output": output_data,
                    "config": config
                }
                self.write(response)

    for processor_name, processor in processors.items():
        register_preprocess_handler(processor_name, processor)

    return handlers


class Application(tornado.web.Application):
    """This is a Tornado application class.

    It handles the routing of URLs to request handlers and sets up various settings.
    """
    def __init__ (self):
        handlers = get_preprocess_handlers()
        settings = {
            "debug": True
        }
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    print("server running at server:%d ..."%(tornado.options.options.port))
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
