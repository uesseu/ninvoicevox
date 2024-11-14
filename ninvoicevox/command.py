from argparse import ArgumentParser
from .voice import Speaker, get_speaker_info, AsyncQueue
import sys
import shutil

isatty = sys.stdin.isatty()
parser = ArgumentParser(description='''Voicevox client based on python.
This can use argument and stdin.
If you use it in not tty environment, it cannot read argument as text.

Example.

echo こんにちは、ずんだもんなのだ。| ninvoice -c
ninvoice こんにちは、ずんだもんなのだ。
''')
if sys.stdin.isatty():
    parser.add_argument('text', nargs='?', default='')
parser.add_argument('-c', '--cache', action='store_true',
                    help='Enable disk cache.'
                    'Cache is saved in directory named by -p option.')
parser.add_argument('-d', '--delete_cache', action='store_true',
                    help='Delete cache and close.')
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
args = parser.parse_args()


def main() -> None:
    text = args.text if isatty else sys.stdin.read()
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
    count = 0
    while could_speak is False and count < 5:
        if args.stdout:
            Speaker(
                enable_cache=args.cache,
                speaker_id=voice_id,
                speed_scale=args.speed_scale,
                directory=args.cache_path,
                parallel=True
            ).text(text).speak(None)
            could_speak = True
        try:
            Speaker(
                enable_cache=args.cache,
                speaker_id=voice_id,
                speed_scale=args.speed_scale,
                directory=args.cache_path,
                parallel=True
            ).text(text).speak()
            could_speak = True
        except * Exception as er:
            could_speak = False
            count += 1
