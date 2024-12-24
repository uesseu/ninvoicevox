ZUNDA_FOOTER = (
    ('なのです。', 'なのだ。'),
    ('ませんでした。', 'なかったのだ。'),
    ('ました。', 'たのだ。'),
    ('います。', 'いるのだ。'),
    ('いです。', 'のだ。'),
    ('です。', 'なのだ。')
)


def change_style(text):
    for zf in ZUNDA_FOOTER:
        text = text.replace(*zf)
    return text
