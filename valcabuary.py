import os
import sys
import gzip
from appenv import env, log
from errors import NotFoundError
from simpledb import simpledb

class cls_valcabuary(list):
    def __init__(self):
        self.extend(simpledb.get_valcabuary())
        log.info('imported %d words from simpledb to valcabuary' % len(self))

    def hit(self, word):
        start = 0
        end = len(self) - 1

        while start <= end:
            mid = (start+end) >> 1
            res = cmp(word.lower(), self[mid].lower())
            if res == 0:
                return mid
            elif res > 0:
                start = mid + 1
            else:
                end = mid - 1

        return -1

    def auto_complete(self, word):
        from prefixdb import prefixdb
        
        n = len(word)
        while n > 0:
            prefix = word[:n]
            at = prefixdb.hit(prefix)
            if at >= 0:
                return at
            n -= 1

        return -1
        

valcabuary = cls_valcabuary()

if __name__ == "__main__":
    word = "exa"
    if valcabuary.hit(word) >= 0:
        print "hit word %s" % word
        sys.exit(0)

    idx = valcabuary.auto_complete(word)
    if idx:
        print "auto fill %s to %s" % (valcabuary[idx], word) 
    
