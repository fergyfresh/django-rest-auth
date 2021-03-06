import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client, MULTIPART_CONTENT
from django.utils.encoding import force_text

from rest_framework import status


class APIClient(Client):

    def patch(self, path, data='', content_type=MULTIPART_CONTENT, follow=False, **extra):
        return self.generic('PATCH', path, data, content_type, **extra)

    def options(self, path, data='', content_type=MULTIPART_CONTENT, follow=False, **extra):
        return self.generic('OPTIONS', path, data, content_type, **extra)


class BaseAPITestCase(object):

    """
    base for API tests:
        * easy request calls, f.e.: self.post(url, data), self.get(url)
        * easy status check, f.e.: self.post(url, data, status_code=200)
    """
    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None
        if 'content_type' not in kwargs and request_method != 'get':
            kwargs['content_type'] = 'application/json'
        if 'data' in kwargs and request_method != 'get' and kwargs['content_type'] == 'application/json':
            data = kwargs.get('data', '')
            kwargs['data'] = json.dumps(data)  # , cls=CustomJSONEncoder
        if 'status_code' in kwargs:
            status_code = kwargs.pop('status_code')

        # check_headers = kwargs.pop('check_headers', True)
        if hasattr(self, 'token'):
            kwargs['HTTP_AUTHORIZATION'] = 'Token %s' % self.token

        self.response = request_func(*args, **kwargs)
        is_json = bool(
            [x for x in self.response._headers['content-type'] if 'json' in x])
        if is_json and self.response.content:
            self.response.json = json.loads(force_text(self.response.content))
        else:
            self.response.json = {}
        if status_code:
            self.assertEqual(self.response.status_code, status_code)
        return self.response

    def post(self, *args, **kwargs):
        return self.send_request('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.send_request('get', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.send_request('patch', *args, **kwargs)

    # def put(self, *args, **kwargs):
    #     return self.send_request('put', *args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     return self.send_request('delete', *args, **kwargs)

    # def options(self, *args, **kwargs):
    #     return self.send_request('options', *args, **kwargs)

    # def post_file(self, *args, **kwargs):
    #     kwargs['content_type'] = MULTIPART_CONTENT
    #     return self.send_request('post', *args, **kwargs)

    # def get_file(self, *args, **kwargs):
    #     content_type = None
    #     if 'content_type' in kwargs:
    #         content_type = kwargs.pop('content_type')
    #     response = self.send_request('get', *args, **kwargs)
    #     if content_type:
    #         self.assertEqual(
    #             bool(filter(lambda x: content_type in x, response._headers['content-type'])), True)
    #     return response

    def init(self):
        settings.DEBUG = True
        self.client = APIClient()

        self.login_url = reverse('rest_login')
        self.logout_url = reverse('rest_logout')
        self.password_change_url = reverse('rest_password_change')
        self.register_url = reverse('rest_register')
        self.password_reset_url = reverse('rest_password_reset')
        self.user_url = reverse('rest_user_details')
        self.veirfy_email_url = reverse('rest_verify_email')
        self.fb_login_url = reverse('fb_login')

    def _login(self):
        payload = {
            "username": self.USERNAME,
            "password": self.PASS
        }
        self.post(self.login_url, data=payload, status_code=status.HTTP_200_OK)

    def _logout(self):
        self.post(self.logout_url, status=status.HTTP_200_OK)
