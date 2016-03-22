#!/usr/bin/python
# -*- coding: utf-8 -*-
import re


def convert_ass_to_srt(input_buffer):
    input_buffer_srt = []
    for index, line in enumerate(input_buffer.split("\n")):
        if line[:9] == "Dialogue:":
            input_buffer_srt.append("%d\n" % index)
            clean_line = re.sub("{.*?}", "", line)
            entries = clean_line[10:].strip().split(",")
            input_buffer_srt.append(
                "%s --> %s\n" % (entries[1].replace(".", ",") + "0", entries[2].replace(".", ",") + "0"))
            input_buffer_srt.append("".join(entries[9:]).replace("\N", "\n") + "\n")
            input_buffer_srt.append("\n")
    return ''.join(input_buffer_srt)


def byte2int(b_str, width):
    val = sum(ord(b) << 8 * n for (n, b) in enumerate(reversed(b_str)))
    if val >= (1 << (width - 1)):
        val -= (1 << width)
    return val
