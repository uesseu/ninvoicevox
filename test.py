from ninvoicevox import Speaker, get_speaker_info, AsyncQueue
import time
from logging import basicConfig, WARNING
basicConfig(level=WARNING)


# 声の情報をゲットする
voice_info = get_speaker_info()
print(voice_info.name)  # voicevoxの声の種類の辞書
print(voice_info.id)  # 上記の逆引き

# 声の設定。ここでは「ずんだもん」の「あまあま」声にする。
# 他にも色々設定があるようだ。
zundamon = Speaker(get_speaker_info().name['ずんだもん']['あまあま'],
                   enable_cache=True)

# ここで、事前に言いたいことをロードしておく。
# デフォルトでバックグラウンドでやってくれる。
start = zundamon.text('作業を開始しましょう。')
mochi = zundamon.text('差し入れのずんだ餅をどうぞ。')
nodo = zundamon.text('ずんだ餅を喉に詰めないでください。')
end = zundamon.text('作業が終わりました。')

# 激重タスクがあるとする
def gekiomo():
    for n in range(10):
        print(n)
        time.sleep(0.25)


# このwith文の中でキューの中にputすると、
# 非同期的に声を出してくれるけれど、複数の音声が重ならない。
with AsyncQueue() as aq:
    aq.put(start.speak)
    gekiomo()
    aq.put(mochi.speak)
    gekiomo()
    aq.put(nodo.speak)
    gekiomo()
    aq.put(end.speak)

# 別にwith文必須なわけじゃなくて、start, endメソッドでいい。
aq = AsyncQueue().start()
aq.put(start.speak)
gekiomo()
aq.put(mochi.speak)
gekiomo()
aq.put(nodo.speak)
gekiomo()
aq.put(end.speak)
aq.end()

# 同期処理も
start.speak()
mochi.speak()
