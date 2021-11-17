from senpy.plugins import AnalysisPlugin
from senpy.models import Response, Entry
from liwc import load_token_parser
import re
from collections import Counter


class Liwc(AnalysisPlugin):
    '''
    A plugin to easily use LIWC dictionary.
    '''
    name = "liwc"
    author = "@dveni"
    version = "0.1"

    extra_params = {
        "language": {
            "aliases": ["language", "lang", "l"],
            "required": True,
            "options": ["en", "de", "es"],
            "default": "en"
        }
    }
    

    # liwc_dictionary_path = "LIWC2015Dictionary.dic"

    def _load_dictionary(self, liwc_dictionary_path):
        print(liwc_dictionary_path)
        self.liwc_path = self.find_file(liwc_dictionary_path)
        self.log.debug('Usin LIWC dictionary at: %s.' % self.liwc_path)
        parse, category_names = load_token_parser(self.liwc_path)
        return parse, category_names

    def _tokenize(self, text):
        # you may want to use a smarter tokenizer
        for match in re.finditer(r'\w+', text, re.UNICODE):
            yield match.group(0)


    def analyse_entry(self, entry, params):
        self.log.debug('Analysing with the liwc plugin.')
        
        language = params.params['language']
        liwc_dictionary_path = 'LIWCDictionary-{}.dic'.format(language)
        
        parse, category_names = self._load_dictionary(liwc_dictionary_path)

        text = entry.text
        tokens = self._tokenize(text.lower())
        counter = Counter(category for token in tokens for category in parse(token))
        
        entry['liwc:result']=dict(counter)

        yield entry


    test_cases = [{
        'input': '''Four score and seven years ago our fathers brought forth on
              this continent a new nation, conceived in liberty, and dedicated to the
              proposition that all men are created equal. Now we are engaged in a great
              civil war, testing whether that nation, or any nation so conceived and so
              dedicated, can long endure. We are met on a great battlefield of that war.
              We have come to dedicate a portion of that field, as a final resting place
              for those who here gave their lives that that nation might live. It is
              altogether fitting and proper that we should do this.''',
        'expected': {
            'liwc:result': {'number': 2,
                          'drives': 13,
                          'reward': 3,
                          'function': 53,
                          'conj': 9,
                          'relativ': 17,
                          'time': 5,
                          'focuspast': 5,
                          'pronoun': 18,
                          'ppron': 6,
                          'we': 5,
                          'social': 12,
                          'affiliation': 6,
                          'family': 1,
                          'male': 2,
                          'verb': 17,
                          'motion': 2,
                          'prep': 10,
                          'space': 10,
                          'ipron': 12,
                          'article': 6,
                          'adj': 8,
                          'affect': 8,
                          'posemo': 5,
                          'quant': 3,
                          'cogproc': 8,
                          'certain': 2,
                          'auxverb': 9,
                          'focuspresent': 11,
                          'cause': 1,
                          'achiev': 1,
                          'compare': 2,
                          'adverb': 4,
                          'negemo': 3,
                          'anger': 3,
                          'power': 3,
                          'death': 2,
                          'work': 1,
                          'interrog': 2,
                          'differ': 2,
                          'tentat': 3,
                          'leisure': 1,
                          'they': 1,
                          'bio': 2,
                          'health': 2,
                          'focusfuture': 1,
                          'discrep': 1}
                                }
                            }]