import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(current_dir)
sys.path.append(server_dir)

from myers.myers import diff as myers_diff
from utils.tokenize import split_prompt_into_tokens


SYMBOLS = [".", ",", "?", "!", "\\"]


def compare_two_sentences(s1, s2, symbols=SYMBOLS):
    '''
    Compare two sentences

    Returns:
        a list of tuples in the form of: (action, word, (s1_idx, s2_idx))
            - action (str): k | i | r | m
              k: keep, i: insert, r: remove, m: move
            - word (str): the word
            - s1_idx (int): the index of the word in s1, -1 for not existing
            - s2_idx (int): the index of the word in s2, -1 for not existing
    '''
    if isinstance(s1, str):
        t1 = split_prompt_into_tokens(s1, symbols)
        t2 = split_prompt_into_tokens(s2, symbols)
    else:
        t1 = s1
        t2 = s2

    tw1 = [item["text"] for item in t1]
    tw2 = [item["text"] for item in t2]
    cmp_res = myers_diff(tw1, tw2)
    kir_result = [] # k: keep, i: insert, r: remove

    # calculate the idx of the words in the old and new sentences
    # -1 for not exist in the sentence
    for idx, item in enumerate(cmp_res):
        action, word = item
        old_idx = -1
        new_idx = -1

        if action != "i":
            old_idx = len(["" for w in cmp_res[:idx] if w[0] != "i"])
        if action != "r":
            new_idx = len(["" for w in cmp_res[:idx] if w[0] != "r"])

        kir_result.append((action, word, (old_idx, new_idx)))

    # find moved words
    kirm_result = [] # k: keep, i: insert, r: remove, m: move
    for idx, item in enumerate(kir_result):
        if item is None:
            continue

        action, word, indexes = item
        old_idx, new_idx = indexes

        if action == "k" or word == ",":
            kirm_result.append(item)
            continue
        if action == "i" or action == "r": # find if the same word is removed
            flag = False
            for sub_idx, sub_item in enumerate(kir_result[idx:]):
                if sub_item is None:
                    continue
                sub_action, sub_word, sub_indexes = sub_item
                sub_old_idx, sub_new_idx = sub_indexes
                if sub_word != word:
                    continue
                if action == "i" and sub_action == "r":
                    kirm_result.append(("m", word, (sub_old_idx, new_idx)))
                    kir_result[idx + sub_idx] = None
                    flag = True
                    break
            if not flag:
                for sub_idx, sub_item in enumerate(kir_result[:idx]):
                    if sub_item is None:
                        continue
                    sub_action, sub_word, sub_indexes = sub_item
                    sub_old_idx, sub_new_idx = sub_indexes
                    if sub_word != word:
                        continue
                    if action == "i" and sub_action == "r":
                        kirm_result.append(("m", word, (sub_old_idx, new_idx)))
                        kir_result[sub_idx] = None
                        flag = True
                        break
            if not flag:
                kirm_result.append(item)

    # for matched words, compare the weight
    for idx, item in enumerate(kirm_result):
        if item is None:
            continue

        action, word, indexes = item
        old_idx, new_idx = indexes

        old_weight = 1
        new_weight = 1

        if action == "k":
            old_weight = t1[old_idx]["weight"]
            new_weight = t2[new_idx]["weight"]
            if old_weight < new_weight:
                action = "iw"
            elif old_weight > new_weight:
                action = "rw"

        weights = (old_weight, new_weight)        
        kirm_result[idx] = (action, word, indexes, weights)

    return kirm_result


if __name__ == "__main__":
    p1 = "The octopus spaceship in the green fields of england comes to save us, 90s, romantism Caspar David Friedrich and chris foss contemplative:2; signature signed watermark:-1"
    p2 = "A edgy photograph of a woman being helped by a robot in a field harvesting vegetables by chris foss and H R Giger 4k hot color scheme"
    results = compare_two_sentences(p1, p2)
    for item in results:
        print(item)
