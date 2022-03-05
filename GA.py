import math
from tkinter import BROWSE
import pattern
import data
import pinyin
import pygad
import numpy as np

from multiprocessing import Pool, Lock

pinyin_map = pinyin.load_pinyin_file()
words_with_ent = data.get_words_with_entropy()

words_list = [w[0] for w in words_with_ent]

hanji_list = [k for k in pinyin_map]

theorically_maxium = math.log2(len(words_list))

pinyin_2_hanji_map = {}

initial_set = set()
simple_set = set()
tone_set = set()

for k, v in pinyin_map.items():
    initial_set.add(v[0])
    simple_set.add(v[1])
    tone_set.add(v[2])
    tpy = ''.join(v)
    if not tpy in pinyin_2_hanji_map:
        pinyin_2_hanji_map.setdefault(tpy, [])
    pinyin_2_hanji_map[tpy].append(k)

max_hanji_choose = 0
for v in pinyin_2_hanji_map.values():
    v.sort()
    if len(v) > max_hanji_choose:
        max_hanji_choose = len(v)

initial_list = [v for v in initial_set]
initial_list.sort()

simple_list = [v for v in simple_set]
simple_list.sort()

tone_list = [v for v in tone_set]
tone_list.sort()

print_lock = Lock()

my_gene_space = [
    range(max_hanji_choose), range(max_hanji_choose),
    range(max_hanji_choose), range(max_hanji_choose),

    range(len(initial_list)), range(len(initial_list)),
    range(len(initial_list)), range(len(initial_list)),

    range(len(simple_list)), range(len(simple_list)),
    range(len(simple_list)), range(len(simple_list)),

    range(len(tone_list)), range(len(tone_list)),
    range(len(tone_list)), range(len(tone_list)), ]


def sol_2_words(solution):
    words = solution[0: 4]
    initials = solution[4: 8]
    simples = solution[8: 12]
    tones = solution[12: 16]

    pys = [''.join([
        initial_list[initials[i]],
        simple_list[simples[i]],
        tone_list[tones[i]]])
        for i in range(4)]

    result_words = []

    for i in range(4):
        if pys[i] in pinyin_2_hanji_map:
            ws = pinyin_2_hanji_map[pys[i]]
            result_words.append(ws[words[i] % len(ws)])
        else:
            return 0

    return [''.join(result_words), [pinyin_map[v]
                                    for v in result_words]]


def fitness_func(solution, solution_idx):
    target_word = sol_2_words(solution)
    rlist, ent = data.average_info_entropy(
        target_word, words_list, target_word)
    print_lock.acquire()
    print("%s : %f" % (target_word[0], ent))
    print_lock.release()
    return 1/(theorically_maxium - ent + 0.00001)


def fitness_wrapper(solution):
    return fitness_func(solution, 0)


class PooledGA(pygad.GA):

    def cal_pop_fitness(self):
        global pool
        pop_fitness = pool.map(fitness_wrapper, self.population)
        return np.array(pop_fitness)


if __name__ == '__main__':
    ga_instance = PooledGA(num_generations=400,
                           num_parents_mating=2,
                           sol_per_pop=100,
                           mutation_probability=1 -
                           math.pow(0.1, 1/len(my_gene_space)),
                           num_genes=len(my_gene_space),
                           fitness_func=fitness_func,
                           gene_type=int,
                           gene_space=my_gene_space)

    with Pool(processes=5) as pool:
        ga_instance.run()

        best_sol = ga_instance.best_solution()[0]

        sol_word = sol_2_words(best_sol)
        rlist, ent = data.guess_vs_possibles(
            sol_word, words_list, sol_word)

        print("Result : %s - %s" % (sol_word[0], ent))
