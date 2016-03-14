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
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# Autores:
#    Manuel Vázquez Acosta
#    Roberto Oscar Labrada
#    Miguel Yuniesqui Godales

# $Id: streams.py 527 2008-02-26 22:31:09Z mygodales@UCI.CU $

"""
Este módulo implementa la lectura de ficheros para pasarlos al detector 
de lenguajes
"""

import chardet
import codecs
import sys

class Stream(object):
    """
    Streams objects allow to read files in any encoding for which
    there is a decoder in encodings (or codecs) module, and chardet may
    detect.
    
    It exists fundamentally to generate the characters of the file in 
    unicode.
    
    Usage:
        file = file('/path/to/text/file')
        stream = Stream(file)
        for unicodechar in stream.generateUnicodeChars():
            print unicodechar
    """
    def __init__(self, stream):
        buff = stream.read(2048)
        stream.seek(0)
        
        charset = chardet.detect(buff)
        
        if charset['confidence'] > 0.75:
            encoding = charset['encoding']
            self.__stream__ = stream
            self.__encoding__ = encoding
        else:
            #TODO: Cambiar por una excepcion
            assert False
            
    def __call__(self, limit = None):
        return self.__iter__(limit)
            
    def __iter__(self, limit = None):
        return self.generateUnicodeChars(limit)
    
    def generateUnicodeChars(self, limit = None):
        """
        Generates each unicode character of the stream
        """
        decoder = codecs.getdecoder(self.__encoding__)
               
        stream = self.__stream__.__iter__()
        NotEOF = True
        i = 0
        while NotEOF and (not limit or i < limit):
            try:
                which = stream.next()
                try:
                    line = decoder(which)[0]
                except:
                    print "Can't decoded properly. Passing raw" > sys.stderr
                    line = which
                    
                if len(line) > 1:
                    for char in line:
                        i = i + 1
                        yield char
                elif len(line) == 1:
                    i = i + 1
                    yield line     
           
            except StopIteration:
                NotEOF = False
