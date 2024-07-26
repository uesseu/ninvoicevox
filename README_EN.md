# Ninvoicevox
Ninvoicevox is python client of voicevox engine.  
Below is the link to voicevox engine.

https://github.com/VOICEVOX/voicevox_engine/releases/latest

It is a simple client of http server and does not depends on other python package.
This package was developped for me to know progress of slow python task.
It has ability to play voice only one sound at once asynchronously,
since hearing multiple sounds is not easy for me.
Furthermore, error of python is reported by voice.

...Im japanese and voicevox may be good software for japanese.
Im not good at English, And so, this README is written in japanese at first.
...It may be only for japanese and may not be needed English version🤔

Install:
```
pip install git+https://github.com/uesseu/ninvoicevox
```

# Usage
At first, start http server of voicevox.
If you want to use in linux, install aplay, which is player of alsa.
Aplay is not required, however it is default for this software.

```bash
cd [path of voicevox engine]
./run
```

- Import Speaker, get_speaker_info
- If you want voicevox to report the progress of the work, import the AsyncQueue.
- Get speaker id by get_speaker_info.
- Make Speaker object.
- Make Voice object by Speaker.text method.
- Voice object gets voice from server in background.
- Voice is played by Voice.speak method by other program.
- AsyncQueue can regulate voice to speak only one voice at once.

The code below may be more simple.

```python
from ninvoicevox import AsyncQueue, Speaker, get_speaker_info

info = get_speaker_info()
zundamon = Speaker(info.name['ずんだもん']['ノーマル'],
                   enable_cache=True)

voice = {}
voice['start'] = zundamon.text('処理が始まりました。')
voice['under_going'] = zundamon.text('処理が途中です。')
voice['end'] = zundamon.text('処理が終わりましたよ。')

def heavy_task():
    pass

with AsyncQueue() as q:
    q.put(voice['start'].speak)  # Speaks in background.
    heavy_task()
    q.put(voice['under_going'].speak)  # Speaks in background after 'start'.
    heavy_task()
    q.put(voice['end'].speak)  # Speaks in backgournd after 'under_going'.
```

# Licence
I'll license this dumb code to MIT. However, the libraries used may not be OSS.
Read document of voicevox carefully.
