'''
A python client of voicevox-engine.

>>> from ninvoicevox import AsyncQueue, Speaker, get_speaker_info
>>> info = get_speaker_info()
>>> zundamon = Speaker(info.name['ずんだもん']['ノーマル'],
>>>                    enable_cache=True)
>>> voice = {}
>>> voice['start'] = zundamon.text('処理が始まりました。')
>>> voice['under_going'] = zundamon.text('処理が途中です。')
>>> voice['end'] = zundamon.text('処理が終わりましたよ。')
>>> def heavy_task():
>>>     pass
>>> with AsyncQueue() as q:
>>>     q.put(voice['start'].speak)  # Speaks in background.
>>>     heavy_task()
>>>     q.put(voice['under_going'].speak)  # Speaks in background after 'start'.
>>>     heavy_task()
>>>     q.put(voice['end'].speak)  # Speaks in backgournd after 'under_going'.
'''
import json
import time
from pathlib import Path
from typing import List, Optional
from threading import Thread
from subprocess import PIPE, Popen
from collections import namedtuple
from .talker import Talker, dict2post, dict2get
from copy import deepcopy
from hashlib import md5
import os
from logging import getLogger, basicConfig, INFO, Logger
import tempfile

basicConfig(level=INFO)
logger = getLogger()
HEADER_JSON = {"Content-Type": "application/json"}
VOICE_TOKEN_API = 'audio_query'
VOICE_API = 'synthesis'
UNIX_SOUND_PLAYER = ['aplay']
if os.name == 'nt':
    import winsound


NameStyle = namedtuple('NameStyle', ('name', 'style'))
SpeakerInfo = namedtuple('SpeakerInfo', ('name', 'id'))
def speakerinfo2dict(loaded: List[dict]) -> SpeakerInfo:
    '''
    Convert json data from voicevox to structure of python.
    '''
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
    '''
    Get voice library information from voicevox server.
    It returns namedtuple named 'SpeakerInfo'.
    The structure of SpeakerInfo is like (by_name, by_id).
    SpeakerInfo.by_name is dictionary.
    It is used like below.

    >>> SpeakerInfo.by_name['ずんだもん']['あまあま']
    1

    SpeakerInfo.by_id is dictionary, too.
    It is used like below.

    >>> SpeakerInfo.by_id[1]
    NameStyle(name='ずんだもん', style='あまあま')

    '''
    loaded = json.loads(Talker(url, api).get())
    return speakerinfo2dict(loaded)


class Speaker:
    '''
    Say something by VOICEVOX.

    Parameters
    ----------
    speaker_id: int
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
    speed_scale: float = 1,
        Voicevox option. speedScale.
    pitch_scale = 0.0,
        Voicevox option. pitchScale.
    intonation_scale = 1,
        Voicevox option. intonationScale.
    volume_scale = 1,
        Voicevox option. volumeScale.
    pre_phoneme_length = 0.1,
        Voicevox option. prePhonemeLength.
    post_phoneme_length = 0.1,
        Voicevox option. postPhonemeLength.
    output_sampling_rate = 0
        Voicevox option. outputSamplingRate.
    output_stereo = True
        Voicevox option. outputStereo.
    kana = ""
        Voicevox option. kana.
    directory: str = 'voice_cache'
        Directory to save cached voice.
        I recommend to use tempfile in standard package of python.
    enable_cache: bool = False
        Make cache file or not.
        This object makes cache file, however it does not delete the file.

    >>> from ninvoicevox import AsyncQueue, Speaker, get_speaker_info
    >>> info = get_speaker_info()
    >>> zundamon = Speaker(info.name['ずんだもん']['ノーマル'],
    >>>                    enable_cache=True)
    >>> voice = {}
    >>> voice['start'] = zundamon.text('処理が始まりました。')
    >>> voice['under_going'] = zundamon.text('処理が途中です。')
    >>> voice['end'] = zundamon.text('処理が終わりましたよ。')
    >>> def heavy_task():
    >>>     pass
    >>> with AsyncQueue() as q:
    >>>     q.put(voice['start'].speak)  # Speaks in background.
    >>>     heavy_task()
    >>>     q.put(voice['under_going'].speak)  # Speaks in background after 'start'.
    >>>     heavy_task()
    >>>     q.put(voice['end'].speak)  # Speaks in backgournd after 'under_going'.
    '''
    def __init__(self, speaker_id: int = 1,
                 url: str="http://localhost:50021",
                 preload: bool = True,
                 speed_scale: float = 1,
                 pitch_scale: float = 0.0,
                 intonation_scale: float = 1,
                 volume_scale: float = 1,
                 pre_phoneme_length: float = 0.1,
                 post_phoneme_length: float = 0.1,
                 output_sampling_rate: float = 0,
                 output_stereo = True,
                 kana: str = "",
                 directory: str = 'voice_cache',
                 enable_cache: bool = False,
                 logger: Logger = logger
                 ) -> None:
        self.directory = Path(directory)
        self.enable_cache = enable_cache
        self.url: str = url
        self.speaker_id = speaker_id
        self.preload = preload
        self.speed_scale = speed_scale
        self.pitch_scale = pitch_scale
        self.intonation_scale = intonation_scale
        self.volume_scale = volume_scale
        self.pre_phoneme_length = pre_phoneme_length
        self.post_phoneme_length = post_phoneme_length
        self.output_sampling_rate = output_sampling_rate
        self.output_stereo = output_stereo
        self.kana = kana
        self.enable_cache = enable_cache
        self.logger = logger

    def text(self, text: str) -> 'Voice':
        return Voice(text, self, self.logger)


class Voice:
    '''
    Voice object.
    It can be yielded from text method of Speaker object.
    It can preload voice asynchronously before using it.
    '''
    def __init__(self, text: str, speaker: Speaker,
                 logger: Optional[Logger] = logger) -> None:
        self.logger = logger
        self.text = text
        self.speaker = speaker
        self.receive_thread = Thread(target=self._receive)
        if self.speaker.preload:
            self.receive_thread.start()
        self.sound: Optional[bytes] = None

    def load(self) -> None:
        '''
        Start making voice by voicevox.
        It is not needed if preload option is True in constructor.

        Returns
        ----------
        None
        '''
        self.receive_thread.start()

    def _setup_token_dict(self) -> None:
        '''
        Set up dict of token.
        '''
        voice_token = Talker(self.speaker.url, VOICE_TOKEN_API)\
            .set_get(dict2get(dict(text=self.text, speaker=self.speaker.speaker_id)))\
            .set_method('POST').get()
        self.token_dict = json.loads(voice_token.decode('utf-8'))
        self.token_dict["speedScale"] = self.speaker.speed_scale
        self.token_dict["pitchScale"] = self.speaker.pitch_scale
        self.token_dict["intonationScale"] = self.speaker.intonation_scale
        self.token_dict["volumeScale"] = self.speaker.volume_scale
        self.token_dict["prePhonemeLength"] = self.speaker.pre_phoneme_length
        self.token_dict["postPhonemeLength"] = self.speaker.post_phoneme_length
        if self.speaker.output_sampling_rate != 0:
            self.token_dict["outputSamplingRate"] = self.speaker.output_sampling_rate
        self.token_dict["outputStereo"] = self.speaker.output_stereo
        if self.speaker.kana != '':
            self.token_dict["kana"] = self.speaker.kana

    def _receive(self) -> None:
        '''
        Receive voice and put it in self.sound.
        It may be used as background task.
        '''
        if self.logger is not None:
            t = time.time()
        self._setup_token_dict()
        if self.speaker.enable_cache:
            if self.load_cache():
                return None
        voice_token = dict2post(self.token_dict)
        self.sound = Talker(self.speaker.url, VOICE_API)\
            .set_header(HEADER_JSON)\
            .set_get(dict2get(dict(speaker=self.speaker.speaker_id)))\
            .set_post(voice_token).get()
        if self.speaker.enable_cache:
            self.save_cache()
        if self.logger is not None:
            self.logger.info(f'Time spent to speak: {time.time() - t}')

    def get(self) -> bytes:
        '''
        Get voice data from voicevox.

        Returns
        ----------
        bytes: Voice from voicevox.
        '''
        self.receive_thread.join()
        return self.sound

    def make_fname(self) -> str:
        '''
        Make name of cache file from option.
        It is hard to same as other cache but not perfect.
        '''
        token_dict = deepcopy(self.token_dict)
        token_dict['url'] = self.speaker.url
        token_dict['text'] = self.text
        token_dict['speaker'] = self.speaker.speaker_id
        hash_md5 = md5()
        hash_md5.update(json.dumps(token_dict).encode())
        return hash_md5.hexdigest()

    def save_cache(self, logger: Logger = logger) -> None:
        '''
        Load voice cache from disk.

        logger: Logger
            If you want to replace logger, you can set it.
        '''
        if not os.path.exists(self.speaker.directory):
            os.makedirs(self.speaker.directory)
        fname = self.speaker.directory / self.make_fname()
        with open(fname, 'wb') as fb:
            logger.info(f'cache saved as {fname}')
            fb.write(self.sound)

    def load_cache(self, logger: Logger = logger) -> bool:
        '''
        Load voice cache from disk.

        logger: Logger
            If you want to replace logger, you can set it.
        '''
        try:
            fname = self.speaker.directory / self.make_fname()
            with open(fname, 'rb') as fb:
                self.sound = fb.read()
            logger.info(f'loaded {fname}')
            return True
        except BaseException as er:
            return False

    def speak(self, command: List[str] = UNIX_SOUND_PLAYER) -> None:
        '''
        Play sound from voicevox.

        Parameters
        ----------
        command: List[str]
            By default, if you are using linux, aplay is used.
            If you want to use other sound player, write like below.
            ['program', '-option']

            If you are using windows, standard library named windound is used.
            There is a little difference between unix and windows.

        Returns
        -------
        None
        '''
        if os.name == 'nt':
            winsound.PlaySound(self.get(), winsound.SND_MEMORY)
        else:
            task = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            task.communicate(self.get())
            task.wait()
