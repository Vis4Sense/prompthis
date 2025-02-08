import os
import sys
import json
import shutil
import pandas as pd

from ..text_comparison.cmp_prompt_with_weight import compare_two_sentences

PROMPT_FILE = "prompts.json"
IMAGE_FILE = "image_cluster.json"

# compare two prompts
def cmp_prompts(p1, p2):
    symbols = [",", ".", "?", "by", "in", "the", "a", "he", "is", "and", "of"]
    p1 = p1["words"]
    p2 = p2["words"]
    cmp_res = compare_two_sentences(p1, p2)
    diff_words = [item for item in cmp_res if item[0] != "k"]
    diff_words = list(filter(lambda x: x[1] not in symbols, diff_words))

    return diff_words

# Prompt pairs to compare
def get_prompt_pairs(prompts, max_dist=5):
    cnt_prompts = len(prompts)
    pairs = []

    for i in range(cnt_prompts):
        for j in range(i + 1, cnt_prompts):
            dist = len(cmp_prompts(prompts[i], prompts[j]))
            if dist <= max_dist:
                pairs.append((i, j))

    return pairs


# Original edges
def generate_original_edges(prompts, pairs, img_cluster, image_indexes):
    edges = []

    for i, j in pairs:
        images1 = image_indexes[i]
        images2 = image_indexes[j]

        diff_words = cmp_prompts(prompts[i], prompts[j])

        for diff in diff_words:
            for idx1 in images1:
                for idx2 in images2:
                    sum_weight = 1
                    edge = {
                        "word": diff[1],
                        "action": diff[0],
                        "src": idx1,
                        "tgt": idx2,
                        "src_clu": img_cluster[idx1],
                        "tgt_clu": img_cluster[idx2],
                        "src_pmt": i,
                        "tgt_pmt": j,
                        "ratio": len(images1) * len(images2),
                        "weight": sum_weight / (len(diff_words) * len(images1) * len(images2))
                    }
                    edges.append(edge)

    return edges


# Normalize edges
def normalize_edges(edges):
    def reverse_edge(edge):
        edge["src"], edge["tgt"] = edge["tgt"], edge["src"]
        edge["src_clu"], edge["tgt_clu"] = edge["tgt_clu"], edge["src_clu"]
        edge["src_pmt"], edge["tgt_pmt"] = edge["tgt_pmt"], edge["src_pmt"]
        if edge["action"] == "r":
            edge["action"] = "i"
        elif edge["action"] == "i":
            edge["action"] = "r"
        return edge

    norm_edges = []

    for edge in edges:
        src_clu = edge["src_clu"]
        tgt_clu = edge["tgt_clu"]
        action = edge["action"]

        if src_clu == tgt_clu:
            src_pmt = edge["src_pmt"]
            tgt_pmt = edge["tgt_pmt"]
            if src_pmt > tgt_pmt:
                edge = reverse_edge(edge)
        elif src_clu > tgt_clu:
            edge = reverse_edge(edge)

        norm_edges.append(edge)

    return norm_edges


def edge_to_key(edge):
    word = edge["word"]
    action = edge["action"]
    src_clu = edge["src_clu"]
    tgt_clu = edge["tgt_clu"]
    return (word, action, src_clu, tgt_clu)


# Bundle edges
def bundle_edges(edges):
    edge_dict = {}

    for edge in edges:
        weight = edge["weight"]
        key = edge_to_key(edge)
        if key not in edge_dict:
            edge_dict[key] = 0
        edge_dict[key] += weight

    return edge_dict


# Calculate edge weight
def update_weight(edges, weights):
    new_edges = []

    image_pairs = {}
    for idx, edge in enumerate(edges):
        src = edge["src"]
        tgt = edge["tgt"]
        key = (src, tgt)
        if key not in image_pairs:
            image_pairs[key] = []
        image_pairs[key].append(idx)

    for key, idxs in image_pairs.items():
        sum_weight = 0
        for idx in idxs:
            key = edge_to_key(edges[idx])
            sum_weight += weights[key]
        for idx in idxs:
            edge = edges[idx]
            key = edge_to_key(edge)
            edge["weight"] = weights[key] / (sum_weight * edge["ratio"])
            new_edges.append(edge)

    new_edge_dict = bundle_edges(new_edges)
    return new_edges, new_edge_dict


def merge_edges(edges):
    same_src_tgt_weight_edges = {}
    for edge in edges:
        src = edge["src"]
        tgt = edge["tgt"]
        weight = edge["weight"]
        weight = round(weight, 3)
        key = (src, tgt, weight)
        if key not in same_src_tgt_weight_edges:
            same_src_tgt_weight_edges[key] = []
        same_src_tgt_weight_edges[key].append(edge)
    new_edges = []
    for key, value in same_src_tgt_weight_edges.items():
        changes = [{
            "word": edge["word"],
            "action": edge["action"],
        } for edge in value]

        new_edge = {
            "word": " ".join([change["word"] for change in changes]),
            "action": value[0]["action"],
            "changes": changes,
            "src": value[0]["src"],
            "tgt": value[0]["tgt"],
            "src_clu": value[0]["src_clu"],
            "tgt_clu": value[0]["tgt_clu"],
            "src_pmt": value[0]["src_pmt"],
            "tgt_pmt": value[0]["tgt_pmt"],
            "ratio": value[0]["ratio"],
            "weight": min(value[0]["weight"] * len(value), 1.0),
        }
        new_edges.append(new_edge)
    return new_edges


def derive(prompts, prompt_pairs, image_clusters, image_indices):
    print('derive')
    original_edges = generate_original_edges(prompts, prompt_pairs, image_clusters, image_indices)
    normalized_edges = original_edges
    bundled_edges = bundle_edges(normalized_edges)
    new_edges, new_weights = update_weight(original_edges, bundled_edges)
    new_edges = merge_edges(new_edges)
    new_weights = bundle_edges(new_edges)
    new_edges, new_weights = update_weight(new_edges, new_weights)

    weights = sorted(bundled_edges.items(), key=lambda x: x[1], reverse=True)
    new_weights = sorted(new_weights.items(), key=lambda x: x[1], reverse=True)

    edge_groups = []
    for key, value in new_weights:
        for edge in new_edges:
            if edge["word"] ==  key[0] and edge["action"] == key[1] and \
                edge["src_clu"] == key[2] and edge["tgt_clu"] == key[3]:
                changes = edge["changes"]
                break
        edge_groups.append({
            "word": key[0],
            "changes": changes,
            "action": key[1],
            "src_clu": key[2],
            "tgt_clu": key[3],
            "weight": value
        })

    return new_edges, edge_groups
