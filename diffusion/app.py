import copy
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

import modules
from utils import request_scheduler
from utils.config_reader import read_configs
from modules.logger.creation_logger import CreationLogger
from modules.logger.session_logger import SessionLogger
from extension import Extension
import translators.extension_dsl2api as dsl2api
import translators.read_dsl2api as read_dsl2api
from modules.reader.readers import readers
from modules.logger.base_logger import BaseLogger
from modules.user.login import match_username_with_userid


app_logger = logging.getLogger(__name__)

define("port", default=5718, help = "run on the given port", type = int)
define("show", default=False, help = "run on the given port", type = bool)

model_config, extension_config = read_configs()
request_scheduler.initialize_request_queue(model_config["urls"])


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    @property
    def handler_name(self):
        return ""

    def get_argument(self, arg, required=True, arg_type=str):
        data = tornado.escape.json_decode(self.request.body)
        if arg in data:
            return data[arg]
        elif not required:
            return None
        raise tornado.web.HTTPError(400, f"Missing argument: {arg}")

    def register_extension(self, data):
        # filter the extensions to be registered
        handler_name = getattr(self, "handler_name", "")
        extensions = extension_config["extensions"]
        extensions = [copy.deepcopy(ext) for ext in extensions if ext["trigger"] == handler_name]
        for ext in extensions:
            ext["metaInfo"] = data
        return [Extension(ext) for ext in extensions]
        # print(f"handler_name: {handler_name}")
        # print(f"extensions: {extensions}")


class HelloWorld(BaseHandler):
    """Hello World"""

    def get(self):
        """get"""
        self.write("Hello, world")
        print("Hello, world")


class LogInHandler(BaseHandler):
    def post(self):
        username = self.get_argument("username")
        userid = match_username_with_userid(username)
        if userid == -1:
            status = 'failed'
        else:
            status = 'success'
        self.write({
            "status": status,
            "userId": userid
        })


class CreateSessionHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        session_logger = SessionLogger(user_id)
        sessions = session_logger.log_session()
        self.write({
            'status': 'success',
            'sessions': sessions
        })


class fetchSessionListHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        session_logger = SessionLogger(user_id)
        sessions = session_logger.fetch_session_list()
        self.write({
            'status': 'success',
            'sessions': sessions
        })


class Text2ImageCreationHandler(BaseHandler):
    @property
    def handler_name(self):
        return "text2image_creation"

    def post(self):
        """post"""
        # get arguments
        user_id = self.get_argument('user_id', required=False)
        thread_id = self.get_argument('thread_id', required=False)
        model = self.get_argument('model')
        settings = self.get_argument('settings')

        # register logger
        logger = CreationLogger(user_id, thread_id)

        # register extension
        extensions = self.register_extension({
            "object": "thread",
            "userId": user_id,
            "sessionId": thread_id
        })

        state, description = \
            request_scheduler.add_request(model, settings, logger, extensions=extensions)

        self.write({
            "status": "success" if state else "failed",
            "promptId": description if state else None,
            "message": description if not state else "succeed"
        })


class FetchLogHandler(BaseHandler):
    def post(self):
        dsl = self.get_argument("dsl")

        extensions = extension_config["extensions"]
        extensions = [copy.deepcopy(ext) for ext in extensions]
        for ext in extensions:
            ext["metaInfo"] = dsl['metaInfo']
        extensions = [Extension(ext) for ext in extensions]

        session_reader = readers['session']
        reader = session_reader(dsl, extensions)
        input_data = reader.read()

        self.write(input_data)


class FetchFullImageHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        thread_id = self.get_argument('sessionId', required=False)
        filename = self.get_argument('filename')

        mode = 'one'
        directory = f'./outputs/{user_id}/{thread_id}/data'
        filename = filename + '.png'

        reader = readers['base'](mode, directory, filename)
        data = reader.read()

        self.write({'data': data})


class FetchDataHandler(BaseHandler):
    def post(self):
        dsl = self.get_argument('dsl')
        session_reader = readers['session']
        reader = session_reader(dsl)
        reader.read()


class FetchNewGenerationHandler(BaseHandler):
    def post(self):
        dsl = self.get_argument("dsl")
        apis = read_dsl2api.read_new_generation(dsl)

        if apis is None:
            self.write({
                "status": "failed",
            })
            return

        base_reader = readers["base"]
        input_data = {}

        for api in apis:
            reader = base_reader(**api)
            data = reader.read(preview=True)
            input_data[api["dsl"]["attribute"]] = data

        self.write({
            "status": "success",
            "data": input_data
        })


class Application(tornado.web.Application):
    """This is a Tornado application class.

    It handles the routing of URLs to request handlers and sets up various settings.
    """
    def __init__ (self):
        handlers = [
            ("/hello_world", HelloWorld),
            ('/login', LogInHandler),
            ('/create/session', CreateSessionHandler),
            ("/create/txt2img", Text2ImageCreationHandler),
            ("/fetch/log", FetchLogHandler),
            ('/fetch/data', FetchDataHandler),
            ('/fetch/session_list', fetchSessionListHandler),
            ('/fetch/full_image', FetchFullImageHandler),
            ("/fetch/new_generation", FetchNewGenerationHandler)
        ]
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
