# coding: utf-8

import json
import requests
from werkzeug.wrappers import BaseRequest
try:
    import gevent
except ImportError:
    gevent = None

DEFAULT_HEADERS = {'Content-Type': 'application/json'}
TOWER_ICON = (
    'https://tower.im/assets/mobile/icon/'
    'icon@512-84fa5f6ced2a1bd53a409013f739b7ba.png'
)

MESSAGES = {
    'created': u'创建了',
    'updated': u'更新了',
    'deleted': u'删除了',
    'commented': u'评论了',

    'archived': u'归档了',
    'unarchived': u'激活了',

    'started': u'开始处理',
    'paused': u'暂停处理',
    'reopen': u'重新打开了',
    'completed': u'完成了',
    'deadline_changed': u'更新截止时间',

    'sticked': u'置顶了',
    'unsticked': u'取消置顶',

    'recovered': u'恢复了',

    # special
    'assigned': u'指派',
    'unassigned': u'取消指派',

    'docs': u'文档',
    'topics': u'讨论',
    'todos': u'任务',
    'todolists': u'任务清单',
    'attachments': u'文件',
}

ACTION_COLORS = {
    'updated': 'good',
    'completed': 'good',
}


class TowerSlack(object):
    def __init__(self, slack_url, tower_secret=None, name='Tower',
                 icon=TOWER_ICON, channel=None):
        self.slack_url = slack_url
        self.tower_secret = tower_secret
        self.name = name
        self.icon = icon
        self.channel = channel

    def send_payload(self, payload):
        if self.name:
            payload['username'] = self.name
        if self.icon:
            payload['icon_url'] = self.icon
        if self.channel:
            payload['channel'] = self.channel

        requests.post(
            self.slack_url,
            data=json.dumps(payload),
            headers=DEFAULT_HEADERS,
            timeout=2,
        )

    @staticmethod
    def create_payload(body, event):
        action = body['action']
        data = body['data']

        attachment = {}
        color = ACTION_COLORS.get(action)
        if color:
            attachment['color'] = color

        project = data.pop('project')
        project_url = 'https://tower.im/projects/%s/' % project['guid']

        keys = data.keys()
        if len(keys) == 1:
            subject = data.pop(keys[0])
        else:
            subject = data.pop(event[:-1])
        subject_url = '%s%s/%s/' % (project_url, event, subject['guid'])

        author = subject.get('handler')
        if author:
            attachment['author_name'] = author['nickname']
            author_link = 'https://tower.im/members/%s/' % (author['guid'])
            attachment['author_link'] = author_link

        action_text = u'%s%s' % (
            MESSAGES.get(action, action),
            MESSAGES.get(event, event),
        )

        text = u'[<%s|%s>]: %s <%s|%s>' % (
            project_url, project['name'],
            action_text,
            subject_url, subject['title'],
        )
        if action in ['assigned', 'unassigned']:
            assignee = subject.get('assignee')
            if assignee:
                text = u'%s 给 %s' % (text, assignee['nickname'])

        attachment['text'] = text
        return {'attachments': [attachment]}

    def parse_request(self, headers, body):
        if self.tower_secret:
            secret = headers.get('X-Tower-Signature')
            if self.tower_secret != secret:
                return None

        event = headers.get('X-Tower-Event')
        return self.create_payload(body, event)

    def application(self, environ, start_response):
        req = BaseRequest(environ)

        if req.method == 'POST':
            data = json.load(req.stream)
            payload = self.parse_request(req.headers, data)
            if gevent:
                gevent.spawn(self.send_payload, payload)
            else:
                self.send_payload(payload)

        body = 'ok'
        headers = [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))),
        ]
        start_response('200 OK', headers)
        return [body]
