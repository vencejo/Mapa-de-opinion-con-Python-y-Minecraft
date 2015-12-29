import unicodedata
import json
import re
import random

def leeArchivoTweets(archivo):
    with open(archivo, 'r') as f:
        tweets = json.load(f)
    return tweets
 
emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE | re.UNICODE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE | re.UNICODE)

def eliminaTildes(s):
     return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    
def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c.encode('ascii') for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def strip_less_than_3_chars(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if len(c)>3)
    return ''.join(stripped)

def tokenize(s):
    return tokens_re.findall(s)
 
def preprocesa(s):
    try: 
        sinTildes = eliminaTildes(s)
        ascii_string = strip_non_ascii(sinTildes)
        tokens = tokenize(ascii_string)
        tokens = [token.lower() for token in tokens if len(token) > 3 and not token.startswith('http')]
        return tokens
    except TypeError:
        return None

def preprocesaTweets(tweets, periodico):
    """ El sentimiento inicial de los tweets es aleatorio"""
    return [(preprocesa(tweet[1]),random.choice(['positive', 'negative'])) for tweet in tweets[periodico]]   

def preprocesaTweet(tweet, sentimiento):
    """ Esta funcion espera un tweet en formato ascii"""
    tokens = tokenize(tweet)
    tokens = [token.lower() for token in tokens if len(token) > 3 and not token.startswith('http')]
    return (tokens,sentimiento)