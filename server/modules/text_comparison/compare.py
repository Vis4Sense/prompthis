import os
import sys
import json
import copy
import shutil

import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(current_dir)

from .cmp_prompt_with_weight import compare_two_sentences


SYMBOLS = [".", ",", "?", "!", "\\"]


def calculate_consecutive_editing(prompts):
    result_prompts = []

    for i, prompt in enumerate(prompts):
        pre = "" if i == 0 else prompts[i-1]["prompt"]
        cur = prompt["prompt"]

        cmp_res = compare_two_sentences(pre, cur)
        words = []

        for idx, item in enumerate(cmp_res):
            action, word, indexes, weights = item
            pre_idx, cur_idx = indexes
            pre_weight, cur_weight = weights
            words.append({
                "id": f"{i}-{idx}",
                "text": word,
                "label": "[F]",
                "action": action,
                "pre_idx": pre_idx,
                "cur_idx": cur_idx,
                "pre_weight": pre_weight,
                "cur_weight": cur_weight,
                "prev": [],
                "next": []
            })
        
        # find previous words
        for idx, word in enumerate(words):
            if word["action"] in ["k", "r", "m"]: # kept or removed or moved from the last prompt
                pre_words = result_prompts[i-1]["words"]
                pre_idx = word["pre_idx"]

                for pre_word in pre_words:
                    if pre_word["cur_idx"] == pre_idx:
                        word["prev"].append({
                            "id": pre_word["id"],
                            "link": word["action"]
                        })
                        pre_word["next"].append({
                            "id": word["id"],
                            "link": word["action"]
                        })
            
            elif word["action"] == "i": # inserted, find whether the word appeared in previous prompt words
                pidx = i - 1
                while pidx >= 0:
                    pre_words = result_prompts[pidx]["words"]
                    for pre_word in pre_words:
                        if word["text"] == pre_word["text"]:
                            word["prev"].append({
                                "id": pre_word["id"],
                                "link": word["action"]
                            })
                            pre_word["next"].append({
                                "id": word["id"],
                                "link": word["action"]
                            })
                    if len(word["prev"]):
                        break
                    pidx -= 1

        result_prompts.append({
            "id": i,
            "text": prompt["prompt"],
            "words": words,
        })

    for prompt in result_prompts:
        words = prompt["words"]
        for word in words:
            del word["pre_idx"]
            del word["cur_idx"]

    return result_prompts


def merge_phrases(prompts, symbols=SYMBOLS):
    result_prompts = []

    def merge_phrase(phrase, word_array):
        result = []
        def sentence_contains_phrase(sentence, phrase):
            for i in range(len(sentence) - len(phrase) + 1):
                segment = sentence[i:i+len(phrase)]
                flag = True
                for j, seg in enumerate(segment):
                    if seg["text"] != phrase[j]["text"]:
                        flag = False
                if flag:
                    action = segment[0]["action"]
                    for _, seg in enumerate(segment):
                        if seg["action"] != action:
                            flag = False
                if flag:
                    return True
            phrase_texts = [word["text"] for word in phrase]
            for words in sentence:
                if words["action"] != "k" and words["text"] in phrase_texts:
                    return False
            return True

        def merge(sentence, phrase):
            def apply(sentence):
                len_s = len(sentence)
                len_p = len(phrase)

                for i in range(len_s - len_p + 1):
                    segment = sentence[i:i+len_p]
                    flag = True
                    for j, seg in enumerate(segment):
                        if seg["text"] != phrase[j]["text"]:
                            flag = False
                            break
                    action = segment[0]["action"]
                    for _, seg in enumerate(segment):
                        if seg["action"] != action:
                            flag = False
                            break
                    if not flag:
                        continue
                    new_word = {
                        "id": segment[0]["id"],
                        "text": " ".join([word["text"] for word in segment]),
                        "label": segment[0]["label"],
                        "action": action,
                        "pre_weight": segment[0]["pre_weight"],
                        "cur_weight": segment[0]["cur_weight"],
                        "prev": [],
                        "next": segment[0]["next"]
                    }
                    sentence[i] = new_word
                    del sentence[i+1:i+len_p]
                    return True, sentence
                return False, sentence
            flag, sentence = apply(sentence)
            while flag:
                flag, sentence = apply(sentence)
            return sentence

        for words in word_array:
            if not sentence_contains_phrase(words, phrase):
                return False, word_array

        for words in word_array:
            words = merge(words, phrase)
            result.append(words)

        return True, result

    def apply(_prompts):
        prompts = copy.deepcopy(_prompts)
        word_array = [prompt["words"] for prompt in prompts]
        for words in word_array:
            len_w = len(words)
            for i, word in enumerate(words):
                for j in range(i+2, len_w):
                    if j >= len_w:
                        break
                    phrase = words[i:j]
                    flag = True
                    for _, phrase_word in enumerate(phrase):
                        if phrase_word["text"] in symbols:
                            flag = False
                            break
                        if phrase_word["action"] != word["action"]:
                            flag = False
                            break
                    if not flag:
                        break
                    flag, result = merge_phrase(phrase, word_array)
                    if flag:
                        print("successfully merged")
                        result = [{
                            "id": prompt["id"],
                            "text": prompt["text"],
                            "words": words
                        } for prompt, words in zip(_prompts, result)]

                        return True, result
        return False, _prompts

    flag, result_prompts = apply(prompts)
    while flag:
        flag, result_prompts = apply(result_prompts)
    return result_prompts


def calculate_distance_matrix(prompts):
    n = len(prompts)
    distances = [[0 for _ in range(n)] for _ in range(n)]

    for i, p1 in enumerate(prompts):
        for j, p2 in enumerate(prompts):
            prompt1 = p1["words"]
            prompt2 = p2["words"]
            cmp_res = compare_two_sentences(prompt1, prompt2)
            # weight change is not considered as a diff word
            diff_words = [item for item in cmp_res if item[0] in ["r", "i", "m"]]
            dist = len(diff_words)
            distances[i][j] = dist


    with open("./cache/distances.json", "w", encoding="utf-8") as f:
        json.dump(distances, f, indent=4)


def compare(prompts, dir=None):
    prompts = calculate_consecutive_editing(prompts)

    prompts = merge_phrases(prompts)

    for prompt in prompts:
        for word in prompt["words"]:
            word["weight"] = word["cur_weight"]

    return prompts
