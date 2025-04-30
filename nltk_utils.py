import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

#transform sentences into tokens
from nltk.tokenize import WordPunctTokenizer
tokenizer = WordPunctTokenizer()
def tokenize(sentence):
    return tokenizer.tokenize(sentence)

#transform words into their basic form
def stem(word):
    return stemmer.stem(word.lower())

#creates a binary vector that shows what words from the sentence appear in our vocab
def bag_of_words(tokenized_sentence, words):
    sentence_words = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1.0
    return bag
