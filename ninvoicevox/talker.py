from typing import Callable, Any, Optional, List, Tuple
from threading import Thread
import urllib.parse
import urllib.request
import json
HEADER_JSON = {"Content-Type": "application/json"}

def dict2post(data: dict) -> bytes:
    return json.dumps(data).encode()

def dict2get(data: dict) -> str:
    return urllib.parse.urlencode(data)


class Talker:
    '''
    Class to talk with server.
    It is just a wrapper of urllib, which is standard
    library of python.
    This class was made because I am not good at web.

    It was useful in this case because name of method
    must be 'POST' however I send by 'GET'.
    '''
    def __init__(self, url: str, api: str):
        '''
        If you want to use api of
        'http://hoge.org/fuga'

        [url] should be 'http://hoge.org'
        and [api] should be 'fuga'

        url: str
            URL to talk.
        api: str
            API of url.
        '''
        self.url: str = url
        self.api: str = api
        self.method: str = 'GET'
        self.running: bool = False
        self.get_data: Optional[str] = None
        self.post_data: Optional[bytes] = None
        self.header: dict = {}
        self.fix_method = False

    def set_post(self, data: bytes) -> 'Talker':
        '''
        Set post to send.

        data: bytes
            It should be bytes.
            If you have object like dict, dict2post may be useful
            Like below.

        >>> Talker().set_post(dict2post({'hoge': 'fuga'}))
        '''
        self.post_data = data
        if not self.fix_method:
            self.method = 'POST'
        return self

    def set_get(self, data: str) -> 'Talker':
        '''
        Set get options to send.

        data: str
            It should be str.
            If you have object like dict, dict2post may be useful
            Like below.

        >>> Talker().set_get(dict2get({'hoge': 'fuga'}))
        '''
        self.get_data = data
        if not self.fix_method:
            self.method = 'GET'
        return self

    def set_header(self, data: dict) -> 'Talker':
        '''
        Set header.
        data: dict
            Header to use.
        '''
        self.header = data
        return self

    def set_method(self, method: str) -> 'Talker':
        '''
        Set method like GET or POST.
        '''
        self.fix_method = True
        self.method = method
        return self

    def _make_url(self) -> str:
        '''
        Make url from raw url, api and get data.
        '''
        if self.get_data is None:
            return '/'.join((self.url, self.api))
        else:
            return '?'.join(['/'.join([self.url, self.api]),
                             str(self.get_data)])

    def _make_request(self) -> None:
        '''
        Make urllib.request.Request object.
        '''
        self.request = urllib.request.Request(
            self._make_url(),
            data=self.post_data,
            method=self.method,
            headers=self.header
            )

    def _get(self) -> bytes:
        '''
        Get something from server.
        '''
        with urllib.request.urlopen(self.request) as f:
            data = f.read()
        self.result = data
        return data

    def send(self) -> 'Talker':
        '''
        Send something to url and api and makes thread to wait for them.
        This method should be called because it makes a
        new thread and the thread makes whole procedure asynchronously.
        '''
        self._make_request()
        self.running = True
        self.runner = Thread(target=self._get)
        self.runner.start()
        return self

    def get(self) -> bytes:
        '''
        Get something from server.
        '''
        if self.running:
            self.running = False
            self.runner.join()
            return self.result
        self._make_request()
        return self._get()
