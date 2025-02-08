import os
import copy
import json
import logging
import requests
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

from modules.text_comparison.compare import compare
from modules.cluster.cluster import image_cluster
from modules.edge_derivation.derive import derive

app_logger = logging.getLogger(__name__)

define("port", default=5709, help = "run on the given port", type = int)
define("show", default=False, help = "run on the given port", type = bool)

static_path = os.path.join('../client/dist')
static_path = os.path.abspath(static_path)

URL_HEAD = "http://localhost:5708"


def get_url_head(is_public=True):
    if is_public:
        return "http://localhost:5718"
    return "http://localhost:5708"

# define base handler
class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def data_received(self, chunk: bytes):
        return super().data_received(chunk)

    def get_argument(self, arg, required=True, arg_type=str):
        data = tornado.escape.json_decode(self.request.body)
        if arg in data:
            return data[arg]
        elif not required:
            return None
        raise tornado.web.HTTPError(400, f"Missing argument: {arg}")

# test handler
class HelloWorld(BaseHandler):
    """Hello World"""

    def get(self):
        """get"""
        self.write("Hello, world")

# log in
class LogInHandler(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        is_public = self.get_argument('isPublic', required=False)
        payload = { 'username': username }
        url = f'{get_url_head(is_public)}/login'
        data = requests.post(url, json=payload, timeout=10).json()
        print(data)
        self.write(data)


# fetch data
class FetchSessionListHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        is_public = self.get_argument('isPublic', required=False)
        payload = { 'userId': user_id }
        url = f'{get_url_head(is_public)}/fetch/session_list'
        data = requests.post(url, json=payload, timeout=10).json()
        self.write(data)


class FetchThreadDataHandler(BaseHandler):
    def post(self):
        # get arguments
        user_id = self.get_argument('userId', required=False)
        thread_id = self.get_argument('sessionId', required=False)
        is_public = self.get_argument('isPublic', required=False)

        payload = {
            "dsl": {
                "metaInfo": {
                    "userId": user_id,
                    "sessionId": thread_id,
                },
            }
        }

        url = f'{get_url_head(is_public)}/fetch/log'
        data = requests.post(url, json=payload, timeout=30).json()

        records = data['log/log']['data']
        images = { image['filename']: image['data'] for image in data['log/image']['data'] }

        image_projection = data['preprocess/image_projection']['data']
        text_projection = data['preprocess/text_projection']['data']

        if image_projection is None:
            image_projection = {}
        if text_projection is None:
            text_projection = {}

        image_projection = {key.rsplit('.', 1)[0] : value for key, value in \
                            image_projection.items()}

        response = {
            'records': records,
            'images': images,
            'image_projection': image_projection,
            'text_projection': text_projection,
        }

        self.write(response)


class FetchFullImageHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        thread_id = self.get_argument('sessionId', required=False)
        is_public = self.get_argument('isPublic', required=False)
        filename = self.get_argument('filename')

        payload = {
            'userId': user_id,
            'sessionId': thread_id,
            'filename': filename,
        }

        url = f'{get_url_head(is_public)}/fetch/full_image'
        data = requests.post(url, json=payload, timeout=10).json()

        self.write(data)

# create new sessions and images

class CreateSessionHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        is_public = self.get_argument('isPublic', required=False)
        payload = { 'userId': user_id }
        url = f'{get_url_head(is_public)}/create/session'
        data = requests.post(url, json=payload, timeout=10).json()
        self.write(data)


class RunGenerationHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        thread_id = self.get_argument('sessionId', required=False)
        is_public = self.get_argument('isPublic', required=False)
        prompt = self.get_argument('prompt')

        payload = {
            # "model": "stable-diffusion-webui",
            "model": "sdxl",
            'user_id': user_id,
            'thread_id': thread_id,
            "settings": {
                "prompt": prompt,
                "steps": 20,
                "batch_size": 4,
            }
        }

        url = f'{get_url_head(is_public)}/create/txt2img'
        data = requests.post(url, json=payload, timeout=10).json()
        self.write(data)


class FetchNewDataHandler(BaseHandler):
    def post(self):
        user_id = self.get_argument('userId', required=False)
        thread_id = self.get_argument('sessionId', required=False)
        prompt_id = self.get_argument('promptId')
        is_public = self.get_argument('isPublic', required=False)

        payload = {
            "dsl": {
                "data": {
                    "user_id": user_id,
                    "thread_id": thread_id,
                },
                "prompt_id": prompt_id,
            }
        }

        url = f'{get_url_head(is_public)}/fetch/new_generation'
        data = requests.post(url, json=payload, timeout=10).json()

        if data["status"] == "failed":
            self.write(data)
            return

        records = data["data"]["log/log"]
        images = { image["filename"]: image["data"] for image in data["data"]["log/image"] }
        image_projection = {key.rsplit('.', 1)[0] : value for key, value in \
                      data["data"]["preprocess/image_projection"].items()}
        text_projection = data['data']['preprocess/text_projection']

        response = {
            "status": "success",
            "data": {
                "records": records,
                "images": images,
                "image_projection": image_projection,
                "text_projection": text_projection,
            }
        }

        self.write(response)


# process and calculation

class PromptTokenizeHandler(BaseHandler):
    '''tokenize prompts'''
    def post(self):
        '''handle post request'''
        prompts = self.get_argument('prompts')
        result = compare(prompts)
        response = {
            'status': 'success',
            'data': {
                'prompts': result,
            }
        }
        self.write(response)


class ImageClusterHandler(BaseHandler):
    '''cluster images according to 2d embedding'''
    def post(self):
        '''handle post request'''
        embeddings = self.get_argument('embeddings')
        threshold = self.get_argument('threshold')
        clusters = image_cluster(embeddings, threshold)
        response = {
            'data': { 'clusters': clusters }
        }
        self.write(response)


class EdgeDeriveHandler(BaseHandler):
    '''derive edges'''
    def post(self):
        '''handle post request'''
        prompts = self.get_argument('prompts')
        prompt_pairs = self.get_argument('promptPairs')
        image_clusters = self.get_argument('imageClusters')
        image_indices = self.get_argument('imageIndices')

        edges, edge_groups = derive(prompts, prompt_pairs, image_clusters, image_indices)

        response = {
            'data': {
                'edges': edges,
                'edgeGroups': edge_groups,
            }
        }
        self.write(response)


class Application(tornado.web.Application):
    """This is a Tornado application class.

    It handles the routing of URLs to request handlers and sets up various settings.
    """
    def __init__ (self):
        print("static_path:", static_path)
        handlers = [
            ("/hello_world", HelloWorld),
            ('/login', LogInHandler),
            ('/create/session', CreateSessionHandler),
            ('/fetch/session_list', FetchSessionListHandler),
            ("/fetch/session_data", FetchThreadDataHandler),
            ("/fetch/new_data", FetchNewDataHandler),
            ('/fetch/full_image', FetchFullImageHandler),
            ("/generate", RunGenerationHandler),
            ('/prompt/tokenize', PromptTokenizeHandler),
            ('/image/cluster', ImageClusterHandler),
            ('/compute/edge_derive', EdgeDeriveHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, \
                {'path': static_path, 'default_filename': 'index.html'}),
        ]
        settings = {
            'static_path': static_path,
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
