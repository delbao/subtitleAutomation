#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re


def convert(input_buffer):
    input_buffer_srt = []
    index = 0

    for line in input_buffer.split("\n"):
        if line[:9] == "Dialogue:":
            # format: index \n start --> end \n text \n\n
            input_buffer_srt.append("%d\n" % index)
            index += 1

            clean_line = re.sub("{.*?}", "", line)
            entries = clean_line[10:].strip().split(",")

            input_buffer_srt.append(
                "%s --> %s\n" % (entries[1].replace(".", ",") + "0", entries[2].replace(".", ",") + "0"))
            input_buffer_srt.append("".join(entries[9:]).replace("\N", "\n") + "\n")
            input_buffer_srt.append("\n")

    return ''.join(input_buffer_srt)


if __name__ == "__main__":
    sys.argv[1:]
