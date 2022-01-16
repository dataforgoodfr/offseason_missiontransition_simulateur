import re
import unicodedata

import numpy as np
import spacy

pat_punct = re.compile(r"[^\w\s]")
pat_space = re.compile(r" {1,}")
sp_fr = spacy.load("fr_core_news_sm", disable=["parser", "tagger", "ner", "textcat"])


def preproc_text(txt):
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = txt.encode("ascii", "ignore")
    txt = txt.decode("utf-8")
    txt = pat_punct.sub(" ", txt)
    txt = pat_space.sub(" ", txt)
    txt = txt.strip()
    sentence = sp_fr(txt)
    sentence = [
        word.lemma_ for word in sentence if word not in sp_fr.Defaults.stop_words
    ]
    txt = " ".join(sentence)
    return txt


vect_preproc_text = np.vectorize(preproc_text)
