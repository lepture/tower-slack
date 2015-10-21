# coding: utf-8

from towerslack import TowerSlack
try:
    from leancloud import Engine
except ImportError:
    Engine = None

application = TowerSlack()

if Engine:
    from werkzeug.contrib.fixers import ProxyFix
    application = ProxyFix(application)
    application = Engine(application)


if __name__ == '__main__':
    try:
        from gevent.pywsgi import WSGIServer as make_server
    except ImportError:
        from wsgiref.simple_server import make_server

    server = make_server('', 8000, application)
    server.serve_forever()
