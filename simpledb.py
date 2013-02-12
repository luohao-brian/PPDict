import gzip
import re, collections
from appenv import env, log
from errors import NotFoundError, InvalidDictError

class cls_simpledb(dict):
    def __init__(self):
        self.uri = env.get_simpledb()

        log.info('initialize simple database %s' % self.uri)
        try:
            self.load()
        except IOError:
            log.warn('cannot open %s for reading' % uri)
            pass

    def load(self):
        self.clear()

        with gzip.open(self.uri, 'r') as db:
            data = db.read().decode('utf-8')
            for line in data.splitlines():
                elems = line.split(u'*')
                if len(elems) != 3:
                    continue

                word = elems[0].encode('utf-8')
                phonetic = elems[1].encode('utf-8')
                desc = elems[2].encode('utf-8')

                self[word] = (phonetic, desc)

            db.close()
 
    def get_valcabuary(self):
        return sorted(self.keys())

    def query(self, word):
        if word in self.keys():
            return self[word]

        return None

    def dump(self):
        try:
            with gzip.open(env.get_simpledb(), 'w') as db:
                for w in self.get_valcabuary():
                    db.write('%s*%s*%s\n' % (w, self[w][0], self[w][1]))
                db.close()
        except IOError:
            log.warn('cannot write to %s' % env.get_simpledb())
            return False

        log.info('regenerate simpledb successfully')
        return True

        
    def regenerate_valcabuary_db(self):
        try:
            with gzip.open(env.get_valcabuarydb(), 'w') as db:
                for w in self.get_valcabuary():
                    db.write('%s\n' % w)
                db.close()
        except IOError:
            log.warn('cannot write to %s' % env.get_valcabuarydb())
            return False

        log.info('regenerate valcabuary database successfully')
        return True

   
    def regenerate_corrector_db(self):
        res = env.get_corrector_res()
        log.info('producing corrector database based on %s' % res)

        model = collections.defaultdict(lambda: 1)

        try:
            with gzip.open(res, 'r') as hres:
                features = re.findall('[a-z]+', hres.read().lower())
                for feature in features:
                    model[feature] += 1
                hres.close()
        except IOError:
            log.warn('regenerate corrector database failed')
            return False

        try:
            with gzip.open(env.get_correctordb(), 'w') as db:
                for f in model.keys():
                    db.write('%s:%d\n' % (f, model[f]))
                db.close()
        except IOError:
            log.warn('cannot write to %s' % env.get_correctordb())
            return False

        log.info('regenerate corrector database successfully')
        return True

    def regenerate_prefix_db(self, nmin=1, nmax=5):
        index = 0
        cache = dict()
        
        for word in self.get_valcabuary():
            word = word.lower()

            for n in range(nmin, nmax+1):
                if len(word) >= n:
                    prefix = word[:n]
                    if not cache.has_key(prefix):
                        cache[prefix] = index

            index += 1

        try:
            with gzip.open(env.get_prefixdb(), 'w') as db:
                for prefix in sorted(cache.keys()):
                    db.write('%s:%d\n' % (prefix, cache[prefix]))
            db.close()
            log.info('learned %d items to prefix db %s' % 
                    (len(cache), env.get_prefixdb()))
        except IOError:
            log.warn('cannot write to %s' % env.get_prefixdb())


simpledb = cls_simpledb()

if __name__ == "__main__":
    print "regenerating simpledb."
    simpledb.dump()

    print "regenerating valcabuary database."
    simpledb.regenerate_valcabuary_db()

    print "regenerating corrector database."
    simpledb.regenerate_corrector_db()

    print 'regenerating prefix database.'
    simpledb.regenerate_prefix_db()
