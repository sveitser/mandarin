from pypinyin import pinyin, Style

COLS = {
    "1": "e30000",
    "2": "02b31c",
    "3": "1510f0",
    "4": "8900bf",
    "5": "777777",
}


def colorize_char(char, tone):
    col = COLS[tone]
    return f'<span style="color:#{col}">{char}</span>'


def colorize_word(word):
    pinyin_syllabels = pinyin(word, style=Style.TONE3, heteronym=False)
    tones = [syl[0][-1] for syl in pinyin_syllabels]
    tones = [tone if tone.isdigit() else "5" for tone in tones]
    # print(word, tones)
    return "".join(colorize_char(char, tone) for char, tone in zip(word, tones))
