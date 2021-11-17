from senpy.plugins import AnalysisPlugin
from senpy.models import Response, Entry
from liwc import load_token_parser
import re
from collections import Counter


class Liwc(AnalysisPlugin):
    '''
    A plugin to easily use MFT dictionary.
    '''
    name = "mft"
    author = "@ggarcia"
    version = "0.1"

    # extra_params = {
    #     "language": {
    #         "aliases": ["language", "lang", "l"],
    #         "required": True,
    #         "options": ["en", "de"],
    #         "default": "en"
    #     }
    # }
    

    def _load_dictionary(self, liwc_dictionary_path):
        print(liwc_dictionary_path)
        self.liwc_path = self.find_file(liwc_dictionary_path)
        self.log.debug('Usin MFT dictionary at: %s.' % self.liwc_path)
        parse, category_names = load_token_parser(self.liwc_path)
        return parse, category_names

    def _tokenize(self, text):
        # you may want to use a smarter tokenizer
        for match in re.finditer(r'\w+', text, re.UNICODE):
            yield match.group(0)


    def analyse_entry(self, entry, params):
        self.log.debug('Analysing with the MFT plugin.')
        
        liwc_dictionary_path = 'MFTDictionary.dic'
        
        parse, category_names = self._load_dictionary(liwc_dictionary_path)
        print(category_names)

        text = entry.text
        tokens = self._tokenize(text.lower())
        counter = Counter(category for token in tokens for category in parse(token))
        
        entry['mft:result']=dict(counter)

        yield entry