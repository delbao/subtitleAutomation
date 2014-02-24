try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO
import langdet
import streams
import languages
#from langdet import languages

def isEnglish(s):


 
  lang = langdet.LanguageDetector.detect(s)
  
  return lang == languages.english
  
