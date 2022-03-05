import pinyin


def match_hanji(match, compare, match_pinyin, compare_pinyin):
    # 汉字、声母、韵母、声调
    return [match == compare,
            match_pinyin[0] == compare_pinyin[0],
            match_pinyin[1] == compare_pinyin[1],
            match_pinyin[2] == compare_pinyin[2]]


def match_one(first, second):
    v = [0, 0, 0, 0]
    vret = [0, 0, 0, 0]

    for i in range(4):
        if first[i] == second[i]:
            vret[i] = v[i] = 2

    for i in range(4):
        if vret[i] > 0:
            continue
        for j in range(4):
            if v[j] > 0:
                continue
            elif first[i] == second[j]:
                vret[i] = v[j] = 1

    ret = 0
    for i in range(4):
        ret *= 3
        ret += vret[i]

    return ret


pinyin_match_result = {}


def match_pinyin(guess_pinyin, word_pinyin) -> int:
    ret = 0
    for i in range(3):
        ret *= 81
        ret += match_one(
            [guess_pinyin[0][i], guess_pinyin[1][i],
                guess_pinyin[2][i], guess_pinyin[3][i]],
            [word_pinyin[0][i], word_pinyin[1][i],
                word_pinyin[2][i], word_pinyin[3][i]]
        )
    return ret


def match_word_with_word(guess, word, guess_pinyin, word_pinyin):
    ret = match_one(guess, word) * 81 * 81 * 81
    ret += match_pinyin(guess_pinyin, word_pinyin)
    return ret


def pattern_to_display(pattern):
    display = ["⬜", "🟨", "🟩"]
    ret = ""
    for i in range(4):
        for i in range(4):
            v = pattern % 3
            ret = "%s%s" % (display[v], ret)
            pattern = int(pattern / 3)
        ret = "%s%s" % (" ", ret)
    return ret


def number_str_to_pattern(number):
    ret = 0
    for i in range(4):
        ret *= 3
        v = 0
        if number[i] == '1':
            v = 1
        elif number[i] == '2':
            v = 2
        ret += v
    return ret


def match_han_word_pattern(guess, target):
    return match_word_with_word(guess=guess[0], word=target[0], guess_pinyin=guess[1], word_pinyin=target[1])


if __name__ == "__main__":

    pinyin.load_pinyin_file()

    def show_pinyin_split(word):
        pinyin_split = [pinyin.get_pinyin(w) for w in word]
        print(pinyin_split)
        return pinyin_split

    target = u"铁石心肠"
    target_split = show_pinyin_split(target)

    pat = match_word_with_word(
        target, target, target_split, target_split)
    print("%s" % pattern_to_display(pat))

    guess = u"研经铸史"
    guess_split = show_pinyin_split(guess)
    pat = match_word_with_word(
        guess, target, guess_split, target_split)
    print("%s" % pattern_to_display(pat))

    guess = u"身当矢石"
    guess_split = show_pinyin_split(guess)
    pat = match_word_with_word(
        guess, target, guess_split, target_split)
    print("%s" % pattern_to_display(pat))
