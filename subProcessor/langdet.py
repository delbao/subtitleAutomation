#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#    Copyright (C) 2007  Universidad de las Ciencias Informáticas
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
#    USA
#

# Autores:
#    Manuel Vázquez Acosta
#    Roberto Oscar Labrada
#    Miguel Yuniesqui Godales

# $Id: langdet.py 773 2008-12-05 07:38:25Z manuelva@UCI.CU $

"""
Este módulo implementa el algoritmo fundamental
"""
from __future__ import division

import string
import math
from languages import english, spanish, french

class LanguageDetector(object):
    """
    LanguageDetector can detect the language of text.
    Currently it can detect either english or spanish text.
    """

    @staticmethod
    def __computeFrequencies__(itText):
        """
        Computes the vector of frequencies of the string given in parameter
        str.

        Returns a mapping from 1-grams and 2-grams to real numbers.
        """
        frequencies = {}
        AmountOfLetters = 0
        AmountOfTwograms = 0

        LastLetter = None
        for which in itText:
            letter = which.lower()
            if letter in string.letters+u'áéíóúñäëïöüàèìòùâêîôûãĩõũçßæ':
                if not letter in frequencies:
                    frequencies[letter] = 0
                frequencies[letter] += 1
                AmountOfLetters += 1

                if LastLetter != None:
                    twogram = LastLetter + letter
                    if not twogram in frequencies:
                        frequencies[twogram] = 0

                    frequencies[twogram] += 1
                    AmountOfTwograms += 1

                LastLetter = letter
            else:
                LastLetter = None

        for which in frequencies:
            if len(which) == 1:
                frequencies[which] = frequencies[which] / AmountOfLetters
            else:
                assert len(which) == 2
                frequencies[which] = frequencies[which] / AmountOfTwograms

        return frequencies

    @staticmethod
    def __cosineSimilarity__(mVector1, mVector2):
        """Computes the cosine similarity of two vectors.
        Actually, is not the cosine similarity. The c.s would be:
        \frac{v1 \cdot v2}{|v1||v2|}.

        Since we know |v1|=|v2|=\sqrt{2}, we avoid the extra calculation."""
        if len(mVector1) < len(mVector2):
            v1, v2 = mVector1, mVector2
        else:
            v1, v2 = mVector2, mVector1

        result= 0
        for which in v1:
            if which in v2:
                result += v1[which]*v2[which]

        return result

    @classmethod
    def __compareByCosine__(cls, vector):
        sp = cls.__cosineSimilarity__(vector, spanish.FOOTPRINT_VECTOR)
        en = cls.__cosineSimilarity__(vector, english.FOOTPRINT_VECTOR)
        fr = cls.__cosineSimilarity__(vector, french.FOOTPRINT_VECTOR)
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
    def detect(self, itText):
        """
        This method detects the language of the text given in parameter
        itText.
        """
        vector = self.__computeFrequencies__(itText)
        return self.__compareByCosine__(vector)

    detectLanguage = detect # Just for backwards compatibility

def main():
    import streams
    import sys

    try:
        import psyco
        psyco.bind(streams.Stream.generateUnicodeChars)
        psyco.bind(LanguageDetector.__computeFrequencies__)
    except:
        pass
    stream = streams.Stream(file(sys.argv[1]))
    result = LanguageDetector.detect(stream(2048))
    print result.ISO_639_1_LANGUAGE_CODE

def vector():
    import streams
    import sys

    try:
        import psyco
        psyco.bind(streams.Stream.generateUnicodeChars)
        psyco.bind(LanguageDetector.__computeFrequencies__)
    except:
        pass
    try:
        import pprint
        repr = pprint.pformat
    except:
        pass
    stream = streams.Stream(file(sys.argv[1]))
    freq = LanguageDetector.__computeFrequencies__(stream)
    print repr(freq)


if __name__ == "__main__":
    main()
