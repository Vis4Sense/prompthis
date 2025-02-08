SYMBOLS = [".", ",", "?", "!", "\\"]


def split_into_tokens(text):
    text = text.replace('|', '||ææææ||')  # use | as delimiter
    text = text.replace('\n', '||').replace(' ', '||')

    symbols = ['.', ',', ';', ':', '?', '!']
    # [ '-', '_', '/', '\\', '(', ')', '[', ']', '{', '}',
    #             '*', '#', '@', '&', '=', '+', '%', '~', '$', '^', '<', '>', '"',
    #            '´', '`', '¸', '˛', '’',
    #            '¤', '₳', '฿', '₵', '¢', '₡', '₢', '₫', '₯', '֏', '₠', '€', 'ƒ', '₣', '₲', '₴', '₭',
    #            '₺', '₾', 'ℳ', '₥', '₦', '₧', '₱', '₰', '£', '៛', '₽', '₹', '₨', '₪', '৳', '₸', '₮',
    #            '₩', '¥', '§', '‖', '¦', '⟨', '⟩', '–', '—', '¯', '»', '«', '”', '÷', '×', '′', '″',
    #            '‴', '¡', '¿', '©', '℗', '®', '℠', '™']

    for c in symbols:
        text = text.replace(c, '||{}||'.format(c))

    # re-construct some special character groups as they are tokens
    text = text.replace('[||||[', '[[').replace(']||||]', ']]')
    text = text.replace('{||||{', '{{').replace('}||||}', '}}')
    text = text.replace('<||||!||||-||||-||', '||<!--||').replace('||-||||-||||>', '||-->||')

    while '||||' in text:
        text = text.replace('||||', '||')

    tokens = filter(lambda a: a != '', text.split('||'))  # filter empty strings
    tokens = ['|' if w == 'ææææ' else w for w in tokens]  # insert back the |s
    return tokens


def split_prompt_into_tokens(prompt, symbols = SYMBOLS):
    sentences = split_prompt_into_sentences(prompt)
    tokens = []
    for sentence in sentences:
        tokens += split_sentence_into_tokens(sentence, symbols)
    return tokens


def split_prompt_into_sentences(prompt):
    sentences = prompt.split(";")
    sentences = [s.strip() for s in sentences]
    return sentences


def split_sentence_into_tokens(sentence, symbols=SYMBOLS):
    weight = 1.0
    sd_weight_map = {"(": 1.1, ")": 1.1, "[": 0.9, "]": 0.9}

    # for disco prompt, weight is after ":"
    if ":" in sentence:
        segments = sentence.split(":")
        assert len(segments) == 2
        sentence, weight = segments
        weight = float(weight)

    sentence = sentence.replace(" ", "||")
    for symbol in symbols:
        sentence = sentence.replace(symbol, f"||{symbol}||")

    tokens = filter(lambda x: x != "", sentence.split("||"))
    tokens = list(tokens)

    stack = []
    tokens_with_weight = [{}] * len(tokens)

    for idx, token in enumerate(tokens):
        if token[0] not in "([" and token[-1] not in ")]" and len(stack) == 0:
            tokens_with_weight[idx] = {
                "text": token,
                "text_original": token,
                "weight": weight,
            }
            continue
        stack.append((idx, token))
        if token[-1] in ")]":
            assert len(stack) > 0
            cnt = 0
            for i in range(len(token) - 1, -1, -1):
                if token[i] == token[-1]:
                    cnt += 1
                else:
                    break
            token_weight = weight * pow(sd_weight_map[token[-1]], cnt)
            while True:
                try:
                    top_idx, top = stack.pop()
                    tokens_with_weight[top_idx] = {
                        "text": top.strip("()[]"),
                        "text_original": top,
                        "weight": token_weight,
                    }
                    if top[0] in "([":
                        break
                except:
                    break

    return tokens_with_weight
