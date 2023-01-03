from argparse import ArgumentParser
from .voice import Speaker, get_speaker_info
import sys
import shutil

isatty = sys.stdin.isatty()
parser = ArgumentParser(description='Voicevox client')
if sys.stdin.isatty():
    parser.add_argument('text', nargs='?', default='')
parser.add_argument('-c', '--cache', action='store_true',
                    help='Enable disk cache.'
                    'Cache is saved in directory named by -p option.')
parser.add_argument('-d', '--delete_cache', action='store_true',
                    help='Delete cache and close.')
parser.add_argument('-p', '--cache_path', default='.', help='Path to save cached voices.')
parser.add_argument('-s', '--speaker', nargs='?', default='ずんだもん',
                    help='Name of speaker.')
parser.add_argument('-n', '--name', nargs='?', default='ノーマル',
                    help='Name of voice.')
args = parser.parse_args()

def main() -> None:
    text =  args.text if isatty else sys.stdin.read()
    if args.delete_cache:
        shutil.rmtree(Speaker('', preload=False).directory)
        return None
    Speaker(enable_cache=args.cache,
            speaker_id=get_speaker_info().name[args.speaker][args.name],
            directory=args.cache_path
            ).text(text).speak()

