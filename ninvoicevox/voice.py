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
from hashlib import md5
import os
from logging import getLogger, basicConfig, WARNING, Logger, NullHandler
import tempfile
from itertools import chain
from copy import deepcopy
from .asyncqueue import AsyncQueue
import sys

basicConfig(level=WARNING)
logger = getLogger('ninvoice')
logger.addHandler(NullHandler())
HEADER_JSON = {"Content-Type": "application/json"}
VOICE_TOKEN_API = 'audio_query'
VOICE_API = 'synthesis'
UNIX_SOUND_PLAYER = ['aplay']
if os.name == 'nt':
    import winsound


NameStyle = namedtuple('NameStyle', ('name', 'style'))
SpeakerInfo = namedtuple('SpeakerInfo', ('name', 'id'))


class Dictionary:
    '''
    Class to configure dictionary of voicevox.
    '''

    def __init__(self, url: str = "http://localhost:50021"):
        self.url = url

    def get(self):
        return json.loads(Talker(self.url, 'user_dict').get())

    def delete(self, word_id: str):
        '''
        word_id: str
        '''
        return Talker(self.url, '/'.join(('user_dict_word', word_id)))\
            .set_method('DELETE').send()

    def update(
        self, word_id, surface: str, pronunciation: str, accent_type: int,
        url: str = "http://localhost:50021",
        word_type: str | None = None, priority: int | None = None
    ):
        '''
        surface: str
            Surface of word.
        pronunciation: str
            Pronounciation in katakana.
        accent_type: int
            Location of accent.
        word_type: str
            Type of word. it is one of them.
            "PROPER_NOUN" "COMMON_NOUN" "VERB" "ADJECTIVE" "SUFFIX"
        '''
        request = {
                    'word_uuid': word_id,
                    'surface': surface,
                    'pronunciation': pronunciation,
                    'accent_type': accent_type
                 }
        if word_type:
            request.update({'word_type': word_type})
        if priority:
            request.update({'priority': priority})
        return Talker(url, 'user_dict_word')\
            .set_header(HEADER_JSON)\
            .set_get(dict2get(request)).set_method('POST').send()

    def add(self, surface: str, pronunciation: str,
            accent_type: int,
            url: str = "http://localhost:50021",
            word_type: str | None = None,
            priority: str | None = None):
        '''
        surface: str
            Surface of word.
        pronunciation: str
            Pronounciation in katakana.
        accent_type: int
            Location of accent.
        word_type: str
            Type of word. it is one of them.
            "PROPER_NOUN" "COMMON_NOUN" "VERB" "ADJECTIVE" "SUFFIX"
        '''
        request = {
                    'surface': surface,
                    'pronunciation': pronunciation,
                    'accent_type': accent_type
                 }
        if word_type:
            request.update({'word_type': word_type})
        if priority:
            request.update({'priority': priority})
        return Talker(url, 'user_dict_word')\
            .set_header(HEADER_JSON)\
            .set_get(dict2get(request)).set_method('POST').send()


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


def get_speaker_info(url: str = "http://localhost:50021",
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
    parallel: bool
        Apply parallel process.
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
                 url: str = "http://localhost:50021",
                 preload: bool = True,
                 parallel: bool = False,
                 speed_scale: float = 1,
                 pitch_scale: float = 0.0,
                 intonation_scale: float = 1,
                 volume_scale: float = 1,
                 pre_phoneme_length: float = 0.1,
                 post_phoneme_length: float = 0.1,
                 output_sampling_rate: float = 0,
                 output_stereo: bool = True,
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
        self.parallel = parallel
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
        if self.parallel:
            return Voices(text, self, self.logger)
        return Voice(text, self, self.logger)


class Voice:
    '''
    Voice object.
    It can be yielded from text method of Speaker object.
    It can preload voice asynchronously before using it.

    text: str
        Text to read.
    speaker: Speaker
        Speaker object, which represents attributes of voicevox.
    logger: Logger
        Logger you want to use.
    '''

    def __init__(self, text: str, speaker: Speaker,
                 logger: Logger = logger) -> None:
        self.logger = logger
        self.text = text
        self.speaker = speaker
        self.is_receiving: bool = False
        if self.speaker.preload:
            self.receive_thread = Thread(target=self._receive)
            self.receive_thread.start()
            self.is_receiving = True
        self.sound: Optional[bytes] = None

    def _setup_token_dict(self, online=True) -> dict:
        '''
        Set up dict of token.

        online: bool
            Get json from server. If False, makes own dictionary.
        '''
        if online:
            voice_token = Talker(self.speaker.url, VOICE_TOKEN_API)\
                .set_get(
                    dict2get(
                        dict(text=self.text, speaker=self.speaker.speaker_id)
                    )
                ).set_method('POST').get()
            token_dict = json.loads(voice_token.decode('utf-8'))
        else:
            token_dict = dict(text=self.text, speaker=self.speaker.speaker_id)
        token_dict["speedScale"] = self.speaker.speed_scale
        token_dict["pitchScale"] = self.speaker.pitch_scale
        token_dict["intonationScale"] = self.speaker.intonation_scale
        token_dict["volumeScale"] = self.speaker.volume_scale
        token_dict["prePhonemeLength"] = self.speaker.pre_phoneme_length
        token_dict["postPhonemeLength"] = self.speaker.post_phoneme_length
        if self.speaker.output_sampling_rate != 0:
            token_dict["outputSamplingRate"
                       ] = self.speaker.output_sampling_rate
        token_dict["outputStereo"] = self.speaker.output_stereo
        if self.speaker.kana != '':
            token_dict["kana"] = self.speaker.kana
        return token_dict

    def _receive(self) -> None:
        '''
        Receive voice and put it in self.sound.
        It may be used as background task.
        '''
        self.is_receiving = True
        if self.logger is not None:
            t = time.time()
        if self.speaker.enable_cache:
            if self.load_cache():
                self.is_receiving = False
                return None
        self.token_dict = self._setup_token_dict()
        voice_token = dict2post(self.token_dict)
        self.sound = Talker(self.speaker.url, VOICE_API)\
            .set_header(HEADER_JSON)\
            .set_get(dict2get(dict(speaker=self.speaker.speaker_id)))\
            .set_post(voice_token).get()
        if self.speaker.enable_cache:
            self.save_cache()
        if self.logger is not None:
            self.logger.info(f'Time spent to speak: {time.time() - t}')
        self.is_receiving = False

    def get(self, timeout: float = 5.0) -> bytes:
        '''
        Get voice data from voicevox.
        If it failed to receive sound, it tries to receive again
        until timeout.
        If preload option is True or is receiving,
        it does not retry.

        trial_num: int
            Number to try.

        Returns
        ----------
        bytes: Voice from voicevox.
        '''
        if self.speaker.preload and self.is_receiving:
            self.receive_thread.join()
            while self.sound is None:
                self.receive_thread = self._receive()
        else:
            # If sound could not be loaded, repeat receiving.
            if self.is_receiving:
                count = 0
                while self.sound is None and count * 0.1 < timeout:
                    time.sleep(0.1)
                    count += 1
            else:
                t = time.time()
                while self.sound is None and time.time() - t < timeout:
                    self._receive()
        if self.sound is None:
            raise Exception('No sound is loaded')
        return self.sound

    def make_fname(self) -> str:
        '''
        Make name of cache file from option.
        It is hard to same as other cache but not perfect.
        '''
        token_dict = self._setup_token_dict(False)
        token_dict['url'] = self.speaker.url
        token_dict['text'] = self.text
        token_dict['speaker'] = self.speaker.speaker_id
        hash_md5 = md5()
        hash_md5.update(json.dumps(token_dict).encode())
        return hash_md5.hexdigest()

    def save_cache(self) -> None:
        '''
        Load voice cache from disk.

        logger: Logger
            If you want to replace logger, you can set it.
        '''
        if self.sound is None:
            raise Exception('Sound is None')
        if not os.path.exists(self.speaker.directory):
            os.makedirs(self.speaker.directory)
        fname = self.speaker.directory / self.make_fname()
        with open(fname, 'wb') as fb:
            self.logger.info(f'cache saved as {fname}')
            fb.write(self.sound)

    def load_cache(self) -> bool:
        '''
        Load voice cache from disk.

        logger: Logger
            If you want to replace logger, you can set it.
        '''
        fname = self.speaker.directory / self.make_fname()
        if Path(fname).exists():
            with open(fname, 'rb') as fb:
                self.sound = fb.read()
            if self.sound is None:
                Exception('Cache is empty')
            self.logger.info(f'loaded {fname}')
            return True
        else:
            FileNotFoundError('There is no cache.')
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
        if command is None:
            sys.stdout.buffer.write(self.get())
            return 0
        if os.name == 'nt':
            winsound.PlaySound(self.get(), winsound.SND_MEMORY)
        else:
            task = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            task.communicate(self.get())
            task.wait()


class Voices:
    def __init__(self, text: str, speaker: Speaker,
                 logger: Logger = logger) -> None:
        self.logger = logger
        speaker_ = deepcopy(speaker)
        speaker_.preload = False
        texts = list(chain.from_iterable(
            t.split('、') for t in text.split('。')
        ))
        self.voices = [Voice(text, speaker_, logger) for text in texts]

    def speak(self, command: list = UNIX_SOUND_PLAYER):
        with AsyncQueue() as aq:
            for voice in self.voices:
                aq.put(voice.get)
            for voice in self.voices:
                voice.speak(command)
