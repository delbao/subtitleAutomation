try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import langdet
import languages


def is_english(s):
    lang = langdet.LanguageDetector.detect(s)

    return lang == languages.english
