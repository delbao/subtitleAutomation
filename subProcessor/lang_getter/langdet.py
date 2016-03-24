#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from langdetect import detect


def get_language():
    try:
        with open(sys.argv[1]) as file_:
            text = file_.read()
            text = text.decode('utf-8')
        return detect(text)
    except UnicodeDecodeError:
        return chine_or_none(text)
    except IndexError:
        return 'ERROR: File not open. Please input file'


def chine_or_none(text):
    try:
        text = text.decode('utf_16')
        if detect(text) == 'en':
            return 'ch'
        return None
    except UnicodeDecodeError:
        return None


if __name__ == "__main__":
    language = get_language()
    print(language)
