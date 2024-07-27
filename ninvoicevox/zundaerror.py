from .voice import Speaker, get_speaker_info
import traceback
import sys
import os
from typing import Optional
from urllib.error import URLError

HOME = 'USERPROFILE' if os.name == 'nt' else 'HOME'
if 'ZUNDA_ERROR' in os.environ[HOME]:
    CACHE_DIRECTORY = os.environ["ZUNDA_ERROR"]
else:
    CACHE_DIRECTORY = f'{os.environ[HOME]}/.zundaerror'


def zundamon_says(error_txt: str, backup_txt: Optional[str] = None):
    print(error_txt)
    with_server = True
    try:
        info = get_speaker_info().name['ずんだもん']['ノーマル']
    except URLError:
        info = 3  # 3 is Normal of lovely Zundamon.
        with_server = False
    if backup_txt:
        if with_server:
            Speaker(info, directory=CACHE_DIRECTORY,
                    enable_cache=False).text(error_txt).speak()
        else:
            Speaker(info, directory=CACHE_DIRECTORY,
                    enable_cache=True).text(backup_txt).speak()
    else:
        Speaker(info, directory=CACHE_DIRECTORY,
                enable_cache=True).text(error_txt).speak()
    return error_txt


def make_single_cache(speaker: Speaker, text: str):
    voice = speaker.text(text)
    voice.get()
    sys.stdout.write('🫛')
    sys.stdout.flush()


def make_zundamon_cache():
    info = get_speaker_info().name['ずんだもん']['ノーマル']
    speaker = Speaker(info, enable_cache=True, directory=CACHE_DIRECTORY)
    make_single_cache(speaker, 'そのようなファイルやフォルダはないのだ。')
    make_single_cache(speaker, 'そのようなファイルやフォルダは既にあるのだ。')
    make_single_cache(speaker, 'それはディレクトリなのだ。')
    make_single_cache(speaker, 'それはディレクトリではないのだ。')
    make_single_cache(speaker, '僕には十分なアクセス権がないのだ。')
    make_single_cache(speaker, 'プロセスが見付からないのだ。')
    make_single_cache(speaker, 'タイムアウトなのだ。')
    make_single_cache(speaker, '中断するように言われたのだ。')
    make_single_cache(speaker, '接続が拒否されたのだ。')
    make_single_cache(speaker, '接続が中断されたのだ。')
    make_single_cache(speaker, 'パイプが壊れたのだ。')
    make_single_cache(speaker, '子プロセスが失敗したのだ。')
    make_single_cache(speaker, '非同期処理に失敗したのだ。')
    make_single_cache(speaker, 'ユニコードのエンコードに失敗したのだ。')
    make_single_cache(speaker, 'ユニコードのデコードに失敗したのだ。')
    make_single_cache(speaker, 'ローカル変数が変なのだ。')
    make_single_cache(speaker, '型のエラーなのだ。')
    make_single_cache(speaker, 'それは定義されていないのだ。')
    make_single_cache(speaker, 'ゼロで割り算をしてはいけないのだ。')
    make_single_cache(speaker, 'オーバーフローなのだ。')
    make_single_cache(speaker, '数学的に間違いなのだ。')
    make_single_cache(speaker, 'テストが失敗したようなのだ。')
    make_single_cache(speaker, '属性のエラーなのだ。')
    make_single_cache(speaker, '文字が入力されなかったのだ。')
    make_single_cache(speaker, 'インポートできなかったのだ。')
    make_single_cache(speaker, '添字が範囲外なのだ。')
    make_single_cache(speaker, '辞書のキーが違うのだ。')
    make_single_cache(speaker, 'ユーザーさんが中止しろって言ったからやめたのだ。')
    make_single_cache(speaker, 'メモリー不足なのだ。')
    make_single_cache(speaker, 'バッファ関連のエラーなのだ。')
    make_single_cache(speaker, 'キーが違うのだ。')
    make_single_cache(speaker, 'OS関連のエラーなのだ。')
    make_single_cache(speaker, '無限ループしていそうなのだ。')
    make_single_cache(speaker, '既にガベコレされているのだ。')
    make_single_cache(speaker, '何かよくわからないエラーなのだ。')
    make_single_cache(speaker, 'インデントがおかしいのだ。')
    make_single_cache(speaker, 'タブとスペースどっちかにすべきなのだ。')
    make_single_cache(speaker, 'インタプリタのエラーなのだ。')
    make_single_cache(speaker, '文法が間違っているのだ。')
    make_single_cache(speaker, '何らかのエラーなのだ。')
    print('\nずんだもんの声のキャッシュがインストールされたのだ！')


def _exception_hook(cls, er, tb):
    if cls is FileNotFoundError:
        zundamon_says(
            f'{er.filename}というファイルやフォルダはないのだ。',
            'そのようなファイルやフォルダはないのだ。',
        )
    elif cls is FileExistsError:
        zundamon_says(
            f'{er.filename}というファイルやフォルダが既にあるのだ。'
            'そのようなファイルやフォルダは既にあるのだ。',
        )
    elif cls is IsADirectoryError:
        zundamon_says(
            f'{er.filename}はディレクトリなのだ。',
            'それはディレクトリなのだ。',
        )
    elif cls is NotADirectoryError:
        zundamon_says(
            f'{er.filename}はディレクトリではないのだ。',
            'それはディレクトリではないのだ。',
        )
    elif cls is PermissionError:
        zundamon_says(
            f'{er.filename}に対して十分なアクセス権がないのだ。',
            '僕には十分なアクセス権がないのだ。',
        )
    elif cls is ProcessLookupError:
        zundamon_says('プロセスが見付からないのだ。')
    elif cls is TimeoutError:
        zundamon_says('タイムアウトなのだ。')
    elif cls is InterruptedError:
        zundamon_says('中断するように言われたのだ。')
    elif cls is ConnectionRefusedError:
        zundamon_says('接続が拒否されたのだ。')
    elif cls is ConnectionAbortedError:
        zundamon_says('接続が中断されたのだ。')
    elif cls is BrokenPipeError:
        zundamon_says('パイプが壊れたのだ。')
    elif cls is ChildProcessError:
        zundamon_says('子プロセスが失敗したのだ。')
    elif cls is BlockingIOError:
        zundamon_says('非同期処理に失敗したのだ。')
    elif cls is UnicodeEncodeError:
        zundamon_says('ユニコードのエンコードに失敗したのだ。')
    elif cls is UnicodeDecodeError:
        zundamon_says('ユニコードのデコードに失敗したのだ。')
    elif cls is UnboundLocalError:
        zundamon_says('ローカル変数が変なのだ。')
    elif cls is TypeError:
        zundamon_says('型のエラーなのだ。')
    elif cls is NameError:
        zundamon_says(
            f'{er.name}は定義されていないのだ。',
            'それは定義されていないのだ。',
        )
    elif cls is ZeroDivisionError:
        zundamon_says('ゼロで割り算をしてはいけないのだ。')
    elif cls is OverflowError:
        zundamon_says('オーバーフローなのだ。')
    elif cls is ArithmeticError:
        zundamon_says('数学的に間違いなのだ。')
    elif cls is AssertionError:
        zundamon_says('テストが失敗したようなのだ。')
    elif cls is AttributeError:
        zundamon_says('属性のエラーなのだ。')
    elif cls is EOFError:
        zundamon_says('文字が入力されなかったのだ。')
    elif cls is ImportError:
        zundamon_says(
            f'{er.name}をインポートできなかったのだ。',
            'インポートできなかったのだ。',
        )
    elif cls is ModuleNotFoundError:
        zundamon_says(
            f'{er.name}をインポートできなかったのだ。',
            'インポートできなかったのだ。',
        )
    elif cls is IndexError:
        zundamon_says('添字が範囲外なのだ。')
    elif cls is KeyError:
        zundamon_says('辞書のキーが違うのだ。')
    elif cls is KeyboardInterrupt:
        zundamon_says(
            'ユーザーさんが中止しろって言ったからやめたのだ。'
        )
    elif cls is MemoryError:
        zundamon_says('メモリー不足なのだ。')
    elif cls is BufferError:
        zundamon_says('バッファ関連のエラーなのだ。')
    elif cls is LookupError:
        zundamon_says('キーが違うのだ。')
    elif cls is OSError:
        zundamon_says('OS関連のエラーなのだ。')
    elif cls is RecursionError:
        zundamon_says('無限ループしていそうなのだ。')
    elif cls is ReferenceError:
        zundamon_says('既にガベコレされているのだ。')
    elif cls is RuntimeError:
        zundamon_says('何かよくわからないエラーなのだ。')
    elif cls is IndentationError:
        zundamon_says('インデントがおかしいのだ。')
    elif cls is TabError:
        zundamon_says('タブとスペースどっちかにすべきなのだ。')
    elif cls is SystemError:
        zundamon_says('インタプリタのエラーなのだ。')
    elif cls is SyntaxError:
        zundamon_says('文法が間違っているのだ。')
    elif isinstance(er, ZundamonSays):
        pass
    else:
        zundamon_says('何らかのエラーなのだ。')
    traceback.print_exception(cls, er, tb)


def install():
    try:
        print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
        print('キャッシュを作りますか？作っておくのがオススメです。')
        print('もしキャッシュがないとVOICEVOX ENGINEの起動が毎回必須になります。')
        print('[Y/n]')
        command = input('> ').capitalize()
        if len(command) == 0:
            command = 'Y'
        if command[0] != 'Y':
            print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
            print(f'''では、キャッシュなしにします。
ただし、ずんだエラーはキャッシュディレクトリの存在が動作の必須条件です。
これだけは作らせてください。
{CACHE_DIRECTORY}
このディレクトリは環境変数"ZUNDA_ERROR"で変更することができます。
またキャッシュを作りたくなったらこのディレクトリを削除してもう一度
ずんだエラーをimportしてみてください。
''')
            print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
            os.mkdir(CACHE_DIRECTORY)
        else:
            print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
            print(f'''VOICEVOX ENGINEを起動して下さい。
もしVOICEVOX ENGINEを持っていないなら、このURLからダウンロードするといいです。
https://github.com/VOICEVOX/voicevox_engine/releases/latest

では、Enterキーを押したらキャッシュの作成を始めます。
キャッシュの場所は下記の通りです。
{CACHE_DIRECTORY}
なお、環境変数ZUNDA_ERRORを設定すれば、そのPATHがキャッシュのディレクトリになります。
''')
            print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
            input()
            make_zundamon_cache()

    except URLError:
        print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')
        print('''おや？キャッシュの作成に失敗したようですね。
VOICEVOX ENGINEを持っているなら、それを起動してからもう一度試してほしいです。
もしVOICEVOX ENGINEを持っていないなら、このURLからダウンロードするといいです。
https://github.com/VOICEVOX/voicevox_engine/releases/latest
''')
        print('🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛🫛')


sys.excepthook = _exception_hook


class ZundamonSays:
    def __str__(self):
        error_txt = ''.join(self.args)
        info = get_speaker_info().name['ずんだもん']['ノーマル']
        Speaker(info, enable_cache=True).text(error_txt).speak()
        return error_txt
