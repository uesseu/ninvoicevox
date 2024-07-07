# これはなあに？
Voicevox engineのpython用クライアントを書いてみました。
Voicevox engineは下記です。
https://github.com/VOICEVOX/voicevox_engine/releases/latest

単なるhttpサーバーのクライアントです。依存パッケージは標準以外ないです。
このクライアントは僕のお仕事のpythonスクリプトの進捗報告の為に作成されました。
voicevoxで生成された声を同時に1つだけ再生する事が出来ます。
バックグラウンドで複数声が出てもわけわからなくなりますからね。

一応、下手な英語も併記しますね。
...要らなそうだけど🤔

インストールは

```
pip install git+https://github.com/uesseu/ninvoicevox
```

# Ninvoicevox
Ninvoicevox is python client of voicevox engine.  
Below is the link to voicevox engine.

https://github.com/VOICEVOX/voicevox_engine/releases/latest

It is simple client of http server and does not depends on other python package.
This package was developped for me to know progress of slow python task.
It has ability to play voice only one sound at once asynchronously,
since hearing multiple sounds is not easy for me.

...Im japanese and voicevox may be good software for japanese.
Im not good at English, And so, this README is written in japanese at first.
...It may be only for japanese and may not be needed English version🤔

Install:
```
pip install git+https://github.com/uesseu/ninvoicevox
```

# 使い方
まずはvoicevox engineのhttpサーバーを起動して下さい。
また、linuxの場合はALSAの音声出力ソフトのaplayを使えるようにしておいてください。
依存先じゃないけれど、デフォルトでこれを使います。

```bash
cd [path of voicevox engine]
./run
```

- Speaker, get_speaker_infoをインポートしましょう。
- Voicevoxを進捗報告に使うならAsyncQueueをインポートすると良いです。
- get_speaker_infoを使って声のidを取得します。
- Speakerオブジェクトを作ります。
- Speaker.textを使ってVoiceオブジェクトを作ります。
- Voiceオブジェクトは生成と同時に声をバックグラウンドで取得し始めます。
- Voice.speakで声を他のプログラムで再生します。
- AsyncQueueを使うとバックグラウンドかつ一つだけの声を再生できます。

...コードを見たほうが早いですね。

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

# ライセンス
このコード自体は全然大したことないのでMITライセンスにします。
ですが、用いられている音声ライブラリまでOSSとは限りません。
Voicevoxの説明書きをよく読むと良いのではないかと思います。

# Licence
I'll license this dumb code to MIT. However, the libraries used may not be OSS.
Read document of voicevox carefully.
