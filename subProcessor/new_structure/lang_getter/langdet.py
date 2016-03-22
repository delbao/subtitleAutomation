#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import pprint
import string
import sys

from new_structure.lang_getter.languages import spanish, english, french
from stream import Stream


class LanguageDetector(object):
    @staticmethod
    def __compute_vector_of_frequencies__(it_text):
        frequencies = {}
        amount_of_letters = 0
        amount_of_two_grams = 0
        last_letter = None
        for which in it_text:
            letter = which.lower()
            if letter in string.letters + u'áéíóúñäëïöüàèìòùâêîôûãĩõũçßæ':
                if letter not in frequencies:
                    frequencies[letter] = 0
                frequencies[letter] += 1
                amount_of_letters += 1
                if last_letter is not None:
                    two_gram = last_letter + letter
                    if two_gram not in frequencies:
                        frequencies[two_gram] = 0
                    frequencies[two_gram] += 1
                    amount_of_two_grams += 1
                last_letter = letter
            else:
                last_letter = None
        for which in frequencies:
            if len(which) == 1:
                frequencies[which] = frequencies[which] / amount_of_letters
            else:
                assert len(which) == 2
                frequencies[which] = frequencies[which] / amount_of_two_grams
        return frequencies

    @staticmethod
    def __cosine_similarity_two_vectors__(vector1, vector2):
        if len(vector1) < len(vector2):
            v1, v2 = vector1, vector2
        else:
            v1, v2 = vector2, vector1

        result = 0
        for which in v1:
            if which in v2:
                result += v1[which] * v2[which]

        return result

    @classmethod
    def __compareByCosine__(cls, vector_):
        sp = cls.__cosine_similarity_two_vectors__(vector_, spanish.FOOTPRINT_VECTOR)
        en = cls.__cosine_similarity_two_vectors__(vector_, english.FOOTPRINT_VECTOR)
        fr = cls.__cosine_similarity_two_vectors__(vector_, french.FOOTPRINT_VECTOR)
        if sp > en:
            if sp > fr:
                return spanish
            else:
                return french
        else:
            if en > fr:
                return english
            else:
                return french

    @classmethod
    def detect_the_language_of_the_text(cls, it_text):
        vector_ = cls.__compute_vector_of_frequencies__(it_text)
        return cls.__compareByCosine__(vector_)

    detectLanguage = detect_the_language_of_the_text


def main():
    stream = Stream(file(sys.argv[1]))
    result = LanguageDetector.detect_the_language_of_the_text(stream(2048))
    print result.ISO_639_1_LANGUAGE_CODE


def vector():
    repr_ = pprint.pformat
    stream = Stream(file(sys.argv[1]))
    freq = LanguageDetector.__compute_vector_of_frequencies__(stream)
    print repr_(freq)


if __name__ == "__main__":
    main()
