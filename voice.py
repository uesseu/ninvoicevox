import urllib.parse
import urllib.request
import json
from typing import Callable, Any, Optional, List, Tuple
from threading import Thread
import time
from subprocess import PIPE, Popen
from queue import Queue
from collections import deque, namedtuple
import time
from abc import abstractmethod
import os

HEADER_JSON = {"Content-Type": "application/json"}
VOICE_TOKEN_API = 'audio_query'
VOICE_API = 'synthesis'
if os.name == 'posix':
    SOUND_PLAYER = ['aplay']
elif os.name == 'nt':
    SOUND_PLAYER = ['mshta.exe']



def dict2post(data: dict) -> bytes:
    return json.dumps(data).encode()

def dict2get(data: dict) -> str:
    return urllib.parse.urlencode(data)

class Talker:
    '''
    Class to talk with server.
    It is just a wrapper of urllib, which is standard
    library of python.
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


NameStyle = namedtuple('NameStyle', ('name', 'style'))
SpeakerInfo = namedtuple('SpeakerInfo', ('name', 'id'))
def speakerinfo2dict(loaded: List[dict]) -> SpeakerInfo:
    by_id = {}
    by_name = {}
    for data in loaded:
        name: str = data['name']
        uuid: str = data['speaker_uuid']
        by_name.update(
            {name:
             dict(zip((s['name'] for s in data['styles']),
                      (s['id'] for s in data['styles']),
                      ))
             }
        )
        for style in data['styles']:
            by_id.update({style['id']:
                          NameStyle(name=name, style=style['name'])
                          })
    return SpeakerInfo(by_name, by_id)


def get_speaker_info(
    url: str = "http://localhost:50021",
    api: str = 'speakers') -> SpeakerInfo:
    loaded = json.loads(Talker(url, api).get())
    return speakerinfo2dict(loaded)




class Speaker:
    '''
    Say something by VOICEVOX.
    It can preload voice asynchronously before using it.
    '''
    def __init__(self, text: str, speaker: int = 1,
                 url: str="http://localhost:50021",
                 preload: bool = True,
                 speed_scale = 1,
                 pitch_scale = 0.0,
                 intonation_scale = 1,
                 volume_scale = 1,
                 pre_phoneme_length = 0.1,
                 post_phoneme_length = 0.1,
                 output_sampling_rate = 0,
                 output_stereo = True,
                 kana = "",
                 ):
        '''
        Get voice from VOICEVOX.

        Parameters
        ----------
        text: str
            String to read.
        speaker: int
            Number of voicevox library.
            This specifies which library to use.
        url: str
            URL of voicevox. Default is "http://localhost:50021".
            Of course, it can also be remote host.
        preload: bool
            If this is true, the data is retrieved asynchronously
            by other thread.
            If it is not true, 'load' method should be done before
            retrieving voice.
        '''
        self.url: str = url
        self.text = text
        self.speaker = speaker
        self.receive_thread = Thread(target=self._receive)
        self.loaded = preload
        if self.loaded:
            self.receive_thread.start()
        self.speed_scale = speed_scale
        self.pitch_scale = pitch_scale
        self.intonation_scale = intonation_scale
        self.volume_scale = volume_scale
        self.pre_phoneme_length = pre_phoneme_length
        self.post_phoneme_length = post_phoneme_length
        self.output_sampling_rate = output_sampling_rate
        self.output_stereo = output_stereo
        self.kana = kana

    def load(self) -> None:
        '''
        Start making voice by voicevox.
        It is not needed if preload option is True in constructor.

        Returns
        ----------
        None
        '''
        self.receive_thread.start()

    def _receive(self) -> None:
        '''
        Receive voice and put it in self.sound.
        It may be used as background task.
        '''
        self.loaded = True
        voice_token = Talker(self.url, VOICE_TOKEN_API)\
            .set_get(dict2get(dict(text=self.text, speaker=self.speaker)))\
            .set_method('POST').get()
        token_dict = json.loads(voice_token.decode('utf-8'))
        token_dict["speedScale"] = self.speed_scale
        token_dict["pitchScale"] = self.pitch_scale
        token_dict["intonationScale"] = self.intonation_scale
        token_dict["volumeScale"] = self.volume_scale
        token_dict["prePhonemeLength"] = self.pre_phoneme_length
        token_dict["postPhonemeLength"] = self.post_phoneme_length
        if self.output_sampling_rate != 0:
            token_dict["outputSamplingRate"] = self.output_sampling_rate
        token_dict["outputStereo"] = self.output_stereo
        if self.kana != '':
            token_dict["kana"] = self.kana
        voice_token = dict2post(token_dict)
        self.sound = Talker(self.url, VOICE_API)\
            .set_header(HEADER_JSON)\
            .set_get(dict2get(dict(speaker=self.speaker)))\
            .set_post(voice_token).get()

    def get(self) -> bytes:
        '''
        Get voice data from voicevox.

        Returns
        ----------
        bytes: Voice from voicevox.
        '''
        self.receive_thread.join()
        return self.sound

    def speak(self, command: List[str] = ['aplay']) -> None:
        '''
        Play sound from voicevox.

        Parameters
        ----------
        command: List[str]
            By default, if you are using linux, aplay is used.
            If you are using windows, mshta.exe may be used.

        Returns
        -------
        None
        '''
        task = Popen(command, stdin=PIPE)
        task.communicate(self.get())


class OrderedThreadQueue:
    def __init__(self, end_object: Any = None,
                 endless: bool = False):
        '''
        end_object: Any
            If it is got from queue, the procedure ends.
            It should be singleton.
        endless: bool
            If it is True, this programm is not terminated.
            It may be good if you want to make daemon.
        '''
        self.run = False
        self.queue: Queue = Queue()
        self.end_object = end_object
        self.endless = endless

    @abstractmethod
    def function(self, *args: Any, **kwargs: Any) -> Any:
        '''
        A method to process results.
        It should be inherited.
        '''
        pass

    def repeat(self) -> None:
        '''
        Repeat processing data in queue.
        This should not be called if you want to
        process them asynchronously.
        '''
        while True:
            obj = self.queue.get()
            if not self.endless and obj is self.end_object:
                break
            self.function(obj)

    def start(self) -> 'OrderedThreadQueue':
        '''
        Start processing repeatedly.
        '''
        self.thread = Thread(target=self.repeat)
        self.thread.start()
        return self

    def put(self, data: Any) -> None:
        '''
        Put something into queue.
        '''
        self.queue.put(data)

    def end(self) -> None:
        self.put(None)
        self.thread.join()

    def __enter__(self) -> 'OrderedThreadQueue':
        return self.start()

    def __exit__(self, i, j, k) -> None:
        self.end()

class Speaq(OrderedThreadQueue):
    def function(self, data: Speaker) -> None:
        return data.speak()

