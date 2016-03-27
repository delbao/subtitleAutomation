#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langdetect import detect


def get_language(string):
    try:
        return detect(string.decode('utf-8'))
    except UnicodeDecodeError:
        return chine_or_none(string)
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
