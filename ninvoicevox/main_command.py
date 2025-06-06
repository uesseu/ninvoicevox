from argparse import ArgumentParser
from .voice import Speaker, get_speaker_info, AsyncQueue
import sys
import shutil

parser = ArgumentParser(description='''Voicevox client based on python.
This can use argument and stdin.

Example.

echo こんにちは、ずんだもんなのだ。| ninvoice -c
ninvoice こんにちは、ずんだもんなのだ。
ninvoice < [filename]
''')
parser.add_argument('text', nargs='?', default='')
parser.add_argument('-c', '--cache', action='store_true',
                    help='Enable disk cache.'
                    'Cache is saved in directory named by -p option.')
parser.add_argument('-d', '--delete_cache', action='store_true',
                    help='Delete cache and close.')
parser.add_argument('-u', '--url', type=str, default="http://localhost:50021",
                    help='URL of the server. It should be with port number.')
parser.add_argument('-l', '--list_speakers', action='store_true',
                    help='Show list of speakers and exit.')
parser.add_argument('-p', '--cache_path', default='.ninvoice_cache',
                    help='Path to save cached voices.')
parser.add_argument('-i', '--id', nargs='?', default=None,
                    type=int, help='ID of speaker.')
parser.add_argument('-s', '--speaker', nargs='?', default='ずんだもん',
                    help='Name of speaker.')
parser.add_argument('-n', '--name', nargs='?', default='ノーマル',
                    help='Name of voice.')
parser.add_argument('-a', '--speed_scale', type=float, default=1.0,
                    help='Set speed.')
parser.add_argument('-S', '--stdout', action='store_true',
                    help='Show list of speakers and exit.')
parser.add_argument('--zundamon', action='store_true',
                    help='Speak in zundamon style.')
args = parser.parse_args()


def main() -> None:
    text = args.text if args.text or sys.stdin.isatty() else sys.stdin.read()
    if args.zundamon:
        from .terms import change_style
        text = change_style(text)
    if args.delete_cache:
        shutil.rmtree(Speaker('', preload=False).directory)
        return None
    if args.list_speakers:
        print(get_speaker_info())
    if args.id is None:
        try:
            voice_id = get_speaker_info().name[args.speaker][args.name]
        except BaseException:
            voice_id = 3
    else:
        voice_id = args.id
    could_speak = False
    speaker = Speaker(
        enable_cache=args.cache,
        speaker_id=voice_id,
        speed_scale=args.speed_scale,
        directory=args.cache_path,
        url=args.url,
        parallel=True
    )
    count = 0
    while could_speak is False and count < 5:
        option = [None] if args.stdout else []
        try:
            speaker.text(text).speak(*option)
            could_speak = True
        except * Exception as er:
            could_speak = False
            count += 1
