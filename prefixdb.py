import gzip
from appenv import env, log


class cls_prefixdb(dict):
    def __init__(self):
        log.info('initialze prefix db using %s' % env.get_prefixdb())

        try:
            self.load()
        except IOError:
            log.warn('cannot open %s' % env.get_prefixdb())
            pass

    def load(self):
        self.clear()
        with gzip.open(env.get_prefixdb(), 'r') as db:
            for line in db.readlines():
                prefix, start = line.split(':')
                self[prefix] = start
            db.close()

    def hit(self, prefix):
        prefix = prefix.lower()
        if self.has_key(prefix):
            return int(self[prefix])

        return -1


prefixdb = cls_prefixdb()

if __name__ == "__main__":
    prefixdb.learn()
    
