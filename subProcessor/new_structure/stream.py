import sys
import codecs
import chardet


# Work without this

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
        for unicodechar in stream.generate_unicode_chars():    import streams
    import sys
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
            assert False

    def __call__(self, limit=None):
        return self.__iter__(limit)

    def __iter__(self, limit=None):
        return self.generate_unicode_chars(limit)

    def generate_unicode_chars(self, limit=None):
        """
        Generates each unicode character of the stream
        """
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
