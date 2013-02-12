# this is copied from http://norvig.com/spell-correct.html

import gzip
import collections
from appenv import log, env

class cls_corrector(object):
    def __init__(self):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.model = collections.defaultdict(lambda: 1)
        try:
            with gzip.open(env.get_correctordb(), 'r') as db:
                for line in db.readlines():
                    word, count = line.split(':')
                    self.model[word] = count
                db.close()
        except IOError:
            log.warn('cannot open corrector db %s' % env.get_correctordb())
            return

    def edits1(self, word):
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)
    
    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.model)

    def known(self, words): 
        return set(w for w in words if w in self.model)

    def candidates(self, word):
        return self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
    
    def correct(self, word):
        return max(self.candidates(word), key=self.model.get)

corrector = cls_corrector()

if __name__ == "__main__":
    word = 'abor'
    res = corrector.candidates(word)
    print res
