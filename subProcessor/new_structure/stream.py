import sys
import codecs
import chardet


class Stream(object):
    def __init__(self, stream):
        buff = stream.read(2048)
        stream.seek(0)

        charset = chardet.detect(buff)

        if charset['confidence'] > 0.75:
            encoding = charset['encoding']
            self.__stream__ = stream
            self.__encoding__ = encoding
        else:
            assert False

    def __call__(self, limit=None):
        return self.__iter__(limit)

    def __iter__(self, limit=None):
        return self.generate_unicode_chars(limit)

    def generate_unicode_chars(self, limit=None):
        decoder = codecs.getdecoder(self.__encoding__)
        stream = self.__stream__.__iter__()
        not_eof = True
        i = 0
        while not_eof and (not limit or i < limit):
            try:
                which = stream.next()
                try:
                    line = decoder(which)[0]
                except:
                    print "Can't decoded properly. Passing raw" > sys.stderr
                    line = which

                if len(line) > 1:
                    for char in line:
                        i += 1
                        yield char
                elif len(line) == 1:
                    i += 1
                    yield line

            except StopIteration:
                not_eof = False
