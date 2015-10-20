# coding: utf-8

from towerslack import TowerSlack

application = TowerSlack()


if __name__ == '__main__':
    try:
        from gevent.pywsgi import WSGIServer as make_server
    except ImportError:
        from wsgiref.simple_server import make_server

    server = make_server('', 8000, application)
    server.serve_forever()
