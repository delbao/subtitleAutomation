#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from langdetect import detect


def main():
    try:
        with open(sys.argv[1]) as file_:
            text = file_.read()
        text = text.decode('utf_8')
        return detect(text)
    except UnicodeDecodeError:
        try:
            text = text.decode('utf_16')
            if detect(text) == 'en':
                return 'ch'
            return None
        except UnicodeDecodeError:
            return None
    except IndexError:
        return 'ERROR: File not open. Please input file'

if __name__ == "__main__":
    print(main())
