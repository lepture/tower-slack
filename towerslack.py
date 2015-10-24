# coding: utf-8

import json
import requests
from werkzeug.wrappers import BaseRequest

try:
    import gevent
except ImportError:
    gevent = None

HOMEPAGE = 'https://github.com/lepture/tower-slack'

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

    'documents': u'文档',
    'topics': u'讨论',
    'todos': u'任务',
    'todolists': u'任务清单',
    'attachments': u'文件',
}

COLORS = {
    'created': '#439FE0',
    'updated': 'warning',
    'completed': 'good',
    'deleted': 'danger',
}


class TowerSlack(object):
    def __init__(self, name='Tower', icon=TOWER_ICON, timeout=2):
        self.name = name
        self.icon = icon
        self.timeout = timeout

    def send_payload(self, payload, url, channel=None):
        if self.name:
            payload['username'] = self.name
        if self.icon:
            payload['icon_url'] = self.icon
        if channel:
            payload['channel'] = channel

        kwargs = dict(
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout,
        )

        if gevent:
            gevent.spawn(http_post, url, **kwargs)
        else:
            http_post(url, **kwargs)

    @staticmethod
    def create_payload(body, event):
        action = body['action']
        data = body['data']

        attachment = {}
        color = COLORS.get(action)
        if color:
            attachment['color'] = color

        project = data.pop('project')
        project_url = 'https://tower.im/projects/%s/' % project['guid']

        keys = data.keys()
        if len(keys) == 1:
            subject = data.pop(keys[0])
        else:
            subject = data.pop(event[:-1])
        subject_url = get_subject_url(project_url, event, subject['guid'])

        author = subject.get('handler')
        if author:
            attachment['author_name'] = author['nickname']
            author_link = 'https://tower.im/members/%s/' % (author['guid'])
            attachment['author_link'] = author_link

        text = u'%s <%s|#%s> 的%s <%s|%s>' % (
            MESSAGES.get(action, action),
            project_url, project['name'],
            MESSAGES.get(event, event),
            subject_url, subject['title'],
        )
        if action in ['assigned', 'unassigned']:
            assignee = subject.get('assignee')
            if assignee:
                text = u'%s 给 *%s*' % (text, assignee['nickname'])

        comment = data.get('comment')
        if comment:
            content = comment['content']
            content = content.strip().replace('\n', '\n> ')
            text = u'%s\n> %s' % (text, content)

        attachment['text'] = text
        attachment['mrkdwn_in'] = ['text']
        return {'attachments': [attachment]}

    def __call__(self, environ, start_response):
        req = BaseRequest(environ)

        if req.method != 'POST':
            return redirect_homepage(start_response)

        event = req.headers.get('X-Tower-Event')
        if not event:
            return bad_request(start_response)

        signature = req.headers.get('X-Tower-Signature')
        if signature and signature[0] not in ('@', '#'):
            signature = None

        payload = self.create_payload(json.load(req.stream), event)
        url = 'https://hooks.slack.com/services/%s' % (req.path.lstrip('/'))
        self.send_payload(payload, url, signature)
        return response(start_response)


def get_subject_url(project_url, event, guid):
    if event == 'topics':
        event = 'messages'
    elif event == 'documents':
        event = 'docs'
    return '%s%s/%s/' % (project_url, event, guid)


def response(start_response, code='200 OK', body='ok', headers=None):
    if headers is None:
        headers = []
    headers.extend([
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(body))),
    ])
    start_response(code, headers)
    return [body]


def redirect_homepage(start_response):
    body = 'Redirect to %s' % HOMEPAGE
    headers = [('Location', HOMEPAGE)]
    code = '301 Moved Permanently'
    return response(start_response, code, body, headers)


def bad_request(start_response):
    return response(start_response, code='400 Bad Request', body='400')


def http_post(url, **kwargs):
    requests.post(url, **kwargs)
