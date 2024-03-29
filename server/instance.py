from flask import Flask

class Server(object):
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.app.run(
            debug = True,
            host = '0.0.0.0',
            port = 5000
        )

server = Server()
