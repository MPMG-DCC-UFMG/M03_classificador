import sys
import re
import utils.preprocessing_portuguese as preprossPT

text_preprocessing = preprossPT.TextPreProcessing()
ATA, HOMOLOG, EDITAL, OUTROS = "ATA", "HOMOLOG", "EDITAL", "OUTROS"
title_keys = ["ata_title_count", "homolog_title_count",
              "edital_title_count", "outros_title_count"]
content_keys = ["ata_content_count", "homolog_content_count",
                "edital_content_count", "outros_content_count"]

keywords = [
    {
        "word": "ata",
        "title_regex": str(r"\bata\b"),
        "content_regex": str(r"\bata\b"),
        "class": ATA,
    },
    {
        "word": "sessão pública",
        "title_regex": str(r"\bsessão pública\b"),
        "content_regex": str(r"\bsessão pública\b"),
        "class": ATA,
    },
    {
        "word": "homolog",
        "title_regex": str(r"\bhomologação\b"),
        "content_regex": str(r"\bhomologação\b"),
        "class": HOMOLOG,
    },
    {
        "word": "adjudicação",
        "title_regex": str(r"\badjudicação\b"),
        "content_regex": str(r"\badjudicação\b"),
        "class": HOMOLOG,
    },
    {
        "word": "convite",
        "title_regex": str(r"\bconvite\b"),
        "content_regex": str(r"\bconvite\b"),
        "class": EDITAL,
    },
    {
        "word": "edital",
        "title_regex": str(r"\bedital\b"),
        "content_regex": str(r"\bedital\b"),
        "class": EDITAL,
    },
    {
        "word": "cronograma",
        "title_regex": str(r"\bcronograma\b"),
        "content_regex": str(r"\bcronograma\b"),
        "class": OUTROS,
    },
    {
        "word": "aditamento",
        "title_regex": str(r"\baditamento\b"),
        "content_regex": str(r"\baditamento\b"),
        "class": OUTROS,
    },
    {
        "word": "retificação",
        "title_regex": str(r"\bretificação\b"),
        "content_regex": str(r"\bretificação\b"),
        "class": OUTROS,
    },
    {
        "word": "contrato administrativo",
        "title_regex": str(r"\bcontrato administrativo\b"),
        "content_regex": str(r"\bcontrato administrativo\b"),
        "class": OUTROS,
    },
    {
        "word": "ordem de serviço",
        "title_regex": str(r"\bordem de serviço\b"),
        "content_regex": str(r"\bordem de serviço\b"),
        "class": OUTROS,
    },
    {
        "word": "resposta",
        "title_regex": str(r"\bresposta\b"),
        "content_regex": str(r"\bresposta\b"),
        "class": OUTROS,
    },
    {
        "word": "extrato",
        "title_regex": str(r"\bextrato\b"),
        "content_regex": str(r"\bextrato\b"),
        "class": OUTROS,
    },
    {
        "word": "diário oficial",
        "title_regex": str(r"\bdiário oficial\b"),
        "content_regex": str(r"\bdiário oficial\b"),
        "class": OUTROS,
    },
    {
        "word": "aviso de",
        "title_regex": str(r"\baviso de\b"),
        "content_regex": str(r"\baviso de\b"),
        "class": OUTROS,
    },
]

def content_preprocessing(content):
    content = text_preprocessing.remove_special_characters(content)
    content = text_preprocessing.remove_excessive_spaces(content)
    return content.lower().replace('a t a', 'ata')


def title_extraction_breaklines(content):
    first_lines = []
    
    if bool(content):
        content = text_preprocessing.remove_special_characters(content, exceptions=["\n"]).lower()
        content = text_preprocessing.remove_excessive_spaces(content)
        content = re.sub(r"\n\s*\n", "\n", content)
        first_lines = content.split("\n", 6)[:-1]
    else:
        return None
    return first_lines


def get_content_matches(title, content):
    matches_dict = {
        "title": title, "all_matches": [],
        "ata_title_matches": [], "ata_content_matches": [], "ata_title_count": 0, "ata_content_count": 0,
        "homolog_title_matches": [], "homolog_content_matches": [], "homolog_title_count": 0, "homolog_content_count": 0,
        "edital_title_matches": [], "edital_content_matches": [], "edital_title_count": 0, "edital_content_count": 0,
        "outros_title_matches": [], "outros_content_matches": [], "outros_title_count": 0, "outros_content_count": 0,
    }

    for word_dict in keywords:
        word = word_dict["word"]
        title_regex = word_dict["title_regex"]
        content_regex = word_dict["title_regex"]
        doc_class = word_dict["class"].lower()
        title_matches = []

        for index in range(len(title)):
            line = title[index]
            match = re.findall(title_regex, line.lower())

            if bool(match) and len(match) > 0:
                title_matches.append({"match": match, "line": index + 1})
                matches_dict[f"{doc_class}_title_matches"] += title_matches
                matches_dict[f"{doc_class}_title_count"] += len(title_matches)

        content_matches = re.findall(content_regex, content.lower())
        matches_dict[f"{doc_class}_content_matches"] += content_matches
        matches_dict[f"{doc_class}_content_count"] += max(
            len(content_matches) - len(title_matches), 0)
        matches_dict["all_matches"] += content_matches
    return matches_dict


def key_to_class(key):
    return {
        "ata_title_count": ATA,
        "ata_content_count": ATA,
        "homolog_title_count": HOMOLOG,
        "homolog_content_count": HOMOLOG,
        "edital_title_count": EDITAL,
        "edital_content_count": EDITAL,
    }.get(key, OUTROS)


def update_class_count(doc_class, ata_count, homolog_count, edital_count, others_count):
    if doc_class == ATA:
        ata_count += 1
    if doc_class == HOMOLOG:
        homolog_count += 1
    if doc_class == EDITAL:
        edital_count += 1
    if doc_class == OUTROS:
        others_count += 1
    return ata_count, homolog_count, edital_count, others_count

def get_meta_classe(matches_dict):
    ## se houver uma palavra que "anule" alguma das meta classes (ex: retificação de edital)
    title_counts = dict((k, matches_dict[k])
                        for k in matches_dict if k in title_keys)
    content_counts = dict((k, matches_dict[k])
                          for k in matches_dict if k in content_keys)

    if title_counts["outros_title_count"] > 0:
        return OUTROS
    elif title_counts["homolog_title_count"] > 0:
        return HOMOLOG
    title_counts = [(k, v) for k, v in sorted(
        title_counts.items(), key=lambda item: item[1], reverse=True)]

    content_counts = dict((k, matches_dict[k])
                          for k in matches_dict if k in content_keys)
    content_counts = [(k, v)for k, v in sorted(
        content_counts.items(), key=lambda item: item[1], reverse=True)]

    doc_class = ""
    ## se a palavra chave estiver no título tem um peso maior
    if title_counts[0][1] > 0:
        doc_class = key_to_class(title_counts[0][0])
    elif content_counts[0][1] > 0:
        doc_class = key_to_class(content_counts[0][0])
    else:
        doc_class = OUTROS
    return doc_class

classes_of_interest = [ATA, HOMOLOG, EDITAL, OUTROS]
keywords_of_interest = [key_word for key_word in keywords if key_word["class"] in classes_of_interest]


with open(sys.argv[1], 'r', encoding='utf-8') as f:
    text = f.read()
    ata_count, homolog_count, edital_count, others_count = (0,)*4
    content = content_preprocessing(text)
    title = title_extraction_breaklines(text)
    
    if (bool(title) and len(title)) == 0 or not (content):
        print("ERRO! Documento vazio ou inválido. Favor inserir um arquivo de texto válido.")
    else:
        matches_dict = get_content_matches(title, content)
        doc_class = get_meta_classe(matches_dict)
        # ata_count, homolog_count, edital_count, others_count = update_class_count(doc_class, ata_count, homolog_count, edital_count, others_count)
        # matches_dict["class"] = doc_class
        print(doc_class)
