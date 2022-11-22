import time
from voice import Speaker, Speaq, get_speaker_info

def main() -> None:
    info = get_speaker_info()
    t = time.time()
    mochi = Speaker('餅を喉に詰めないようにして下さい。',
                    info.name['ずんだもん']['あまあま'])
    s1 = Speaker('一')
    s2 = Speaker('二')
    s3 = Speaker('三')
    print(time.time() - t)
    mochi.speak()
    s1.speak()
    s1.speak()
    speaq = Speaq().start()
    speaq.put(s1)
    speaq.put(s2)
    speaq.put(s3)
    speaq.end()
    with Speaq() as q:
        q.put(s1)
        q.put(s2)
        q.put(s3)
if __name__ == '__main__':
    main()
