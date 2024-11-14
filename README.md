# これはなあに？
Voicevox engineのpython用クライアントを書いてみました。
Voicevox engineは下記です。
https://github.com/VOICEVOX/voicevox_engine/releases/latest

単なるhttpサーバーのクライアントです。依存パッケージは標準以外ないです。
このクライアントは僕のお仕事のpythonスクリプトの進捗報告の為に作成されました。
このパッケージには三つの機能があります。

- ninvoicevox: python上でのvoicevox制御
- ninvoice: シェルからの音再生
- zundaerror: ずんだもんのpythonエラー報告

一応、下手な英語も併記しますね。

[README_EN.md](./README_EN.md)

...要らなそうだけど🤔

インストールは

```
pip install git+https://github.com/uesseu/ninvoicevox
```


# 使い方(ninvoicevox)
まずはvoicevox engineのhttpサーバーを起動して下さい。

```bash
cd [path of voicevox engine]
./run
```

また、linuxの場合はALSAの音声出力ソフトのaplayを使えるようにしておいてください。
依存先じゃないけれど、デフォルトでこれを使います。

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

# 使い方(ninvoice)
シェルから使えるninvoicevoxです。説明はこうやって表示してみてください。

```sh
ninvoice -h
```

シェル上からなら二通りの使いかたがあります。

```sh
echo 'こんにちは、ずんだもんなのだ' | ninvoice -c
```

この例では標準入力を読みあげています。

```sh
ninvoice -c 'こんにちは、ずんだもんなのだ'
```

この例では引数を読みあげています。標準入力を読むか引数を読むかはttyなのかどうかで判別しています。なので、例えばvim等でやる場合には引数を読む方法は使えません。vimでならこうします。

```vim
こんにちは
```
ここから行をvisual modeで選択し、標準入出力に渡します。

```vim
:'<,'>!ninvoice -c
```

ちなみに、-cはキャッシュするという意味です。他にも色々あるので見てみるといいですね。

# 使い方(ZundaError)
上記を使ってずんだもんがpythonの終りとほとんどのエラーを報告することができます。
以前、ずんだエラーというのを書いたことがありますが、それの改良版です。
当然VOICEVOX依存ですが、常にVOICEVOXを起動するのも大変です。
なので、キャッシュすることができます。
VOICEVOXを起動している場合には具体的なエラー内容まで読んでくれますが、
VOICEVOXを起動せずキャッシュの場合はそこまではできません。
キャッシュする方法は以下のとおりです。

```python
from ninvoicevox import zundaerror
zundaerror.install()
```

それ以降は下記をimportするだけでエラー報告がずんだもん化します。

```python
from ninvoicevox import zundaerror
```

# ライセンス
このコード自体は全然大したことないのでMITライセンスにします。
ですが、用いられている音声ライブラリまでOSSとは限りません。
Voicevoxの説明書きをよく読むと良いのではないかと思います。

