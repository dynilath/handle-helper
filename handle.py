import pattern
import data
import pinyin


def print_first5(src):
    for i in range(5):
        if i < len(src):
            print("%s - %f" % (src[i][0][0], src[i][1]))


def filter_by_pattern(patt, guess, guess_pinyin, possible_with_weight_list):
    ret = []
    for [word_with_pinyin, weight] in possible_with_weight_list:
        p = pattern.match_word_with_word(
            guess, word_with_pinyin[0], guess_pinyin, word_with_pinyin[1])
        if p == patt:
            ret.append(word_with_pinyin)
    return ret


if __name__ == "__main__":
    possible_with_weight = data.get_words_with_entropy()

    pinyin.load_pinyin_file()

    word_to_pinyin_map = {}
    for w in possible_with_weight:
        word_to_pinyin_map.setdefault(w[0][0], w[0][1])

    print("这是一个汉兜（https://handle.antfu.me/）求解工具")
    print("")
    print("输入范例：")
    print("不可一世 0000 1000 0010 0112")
    print("第一组数字0000，表示“不可一世”四个字没有一个正确")
    print("第二组数字1000，表示“不可一世”四个字的拼音中，不bù的辅音b在答案中存在")
    print("第三组数字0010，表示“不可一世”四个字的拼音中，一yī的元音i在答案中存在")
    print("第四组数字0112，表示“不可一世”四个字的拼音中，可kě的音调、一yī的音调、世shì的音调在答案中存在，且世shì的音调位置也正确")

    while True:
        print("")
        print("推荐词(信息熵排序)：")
        print_first5(possible_with_weight)

        if len(possible_with_weight) < 2:
            break

        # while True:
        print("")
        a = input("输入四字词语，以及匹配结果：\n")

        _guess, _word_result, _initial_result, _simple_result, _tone_result = a.split()

        pats = [pattern.number_str_to_pattern(_word_result),
                pattern.number_str_to_pattern(_initial_result),
                pattern.number_str_to_pattern(_simple_result),
                pattern.number_str_to_pattern(_tone_result), ]

        pat = 0
        for p in pats:
            pat *= 81
            pat += p

        guess = _guess[0:4]
        if not guess in word_to_pinyin_map:
            guess_pinyin = data.default_pinyin(guess)
        else:
            guess_pinyin = word_to_pinyin_map.get(guess)

        print("输入词语：%s" % guess)
        print("拼音数据：%s" % guess_pinyin)
        print("匹配数据：%s" % pattern.pattern_to_display(pat))

        next_word_list = filter_by_pattern(
            pat, guess, guess_pinyin, possible_with_weight)

        possible_with_weight = data.generate_word_list_with_entropy(
            next_word_list)
