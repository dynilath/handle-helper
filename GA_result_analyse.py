import data
import pinyin
import pattern
from matplotlib import pyplot as plt
import numpy as np

pinyin.load_pinyin_file()

ga_best_sol = '己山直玉'
best_sol_word = [ga_best_sol, [pinyin.get_pinyin(c) for c in ga_best_sol]]
word_list_with_ent = data.get_words_with_entropy()
word_list = [w[0] for w in word_list_with_ent]

pat_map = {}

for w in word_list:
    pat = pattern.match_han_word_pattern(best_sol_word, w)
    if not pat in pat_map:
        pat_map.setdefault(pat, [])
    pat_map[pat].append(w)

guess_times_map = {}

for wlen, wl in pat_map.items():
    gues = len(wl)
    if not gues in guess_times_map:
        guess_times_map.setdefault(gues, [])
    guess_times_map[gues].extend(wl)

gt_list = [(k, v) for k, v in guess_times_map.items()]

gt_list.sort(key=lambda x: x[0])

x = np.array([i[0] for i in gt_list])
y = np.array([len(i[1]) for i in gt_list])

plt.bar(x, y)
plt.show()
