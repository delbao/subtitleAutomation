#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re

def convert(buffer):

       
       
    
    buffer_srt = []
    index = 0
    
    for line in buffer.split("\n"):
        if line[:9] == "Dialogue:":
            #format: index \n start --> end \n text \n\n
            buffer_srt.append("%d\n" % (index))
            index += 1

            clean_line = re.sub("{.*?}", "", line)
            entries = clean_line[10:].strip().split(",")

            buffer_srt.append("%s --> %s\n" % (entries[1].replace(".",",")+"0", entries[2].replace(".",",")+"0"))
            buffer_srt.append("".join(entries[9:]).replace("\N","\n")+"\n")
            buffer_srt.append("\n")

    return ''.join(buffer_srt)

if __name__ == "__main__":
    main(sys.argv[1:])
