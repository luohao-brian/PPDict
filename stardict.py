import os
import struct
import sys
import gzip
from appenv import env, log
from errors import NotFoundError, InvalidDictError

class cls_worditem(object):
    def __init__(self, word, offset, size):
        self.word = word
        self.offset = offset
        self.size = size

    def __str__(self):
        return '%s, offset: %d, size: %d' % (self.word, self.offset, self.size)

# this class is deprecated, 
# use ppdict::cls_ppdictmgr in place
class cls_stardictmgr(object):
    def __init__(self):
        self.dicts = []
        self.scan_dicts()

    def scan_dicts(self):
        if not os.path.isdir(env.get_dict_dir()):
            log.warn('dir %s not exists' % env.get_data_dir())
            return
       
        for dirent in os.listdir(env.get_dict_dir()):
            uri = os.path.join(env.get_dict_dir(), dirent)
            if not os.path.isdir(uri):
                continue

            try:
                candidate = cls_stardict(uri)
                self.dicts.append(candidate)
            except NotFoundError, e:
                log.warn('not found: %s' % e)
                continue
            except InvaidDictError, e:
                log.warn('invalid dictionary: %s' % e) 
                continue

    def get_dicts(self):
        return self.dicts
            
            
class cls_stardict(object):
    def __init__(self, uri):
        self.uri = uri
        self.ifo = None
        self.idx = None
        self.data = None
        self.wordlist = []

        for entry in os.listdir(uri):
            if entry.endswith('.ifo'):
                self.ifo = os.path.join(uri, entry)
                #log.info('found stardict info file: %s' % self.ifo)
            elif entry.endswith('.idx'):
                self.idx = os.path.join(uri, entry)
                #log.info('found stardict index file: %s' % self.idx)
            elif entry.endswith('.dict.dz'):
                self.data = os.path.join(uri, entry)
                #log.info('found stardict data file: %s' % self.data)

        if not self.ifo:
            raise NotFoundError(self.ifo)

        if not self.idx:
            raise NotFoundError(self.idx)

        if not self.data:
            raise NotFoundError(self.data)

        #log.info('parse stardict info file %s' % self.ifo)
        
        self.metadata = dict()
        try:
            with open(self.ifo, 'r') as ifo:
                for line in ifo.readlines():
                    if line.find('=')<0:
                        continue

                    line = line[:-1]
                    k, v = line.split('=')
                    self.metadata[k] = v
                ifo.close()
        except IOError:
            raise InValidDictError('failed to open %s' % self.ifo)
        
        self.wordcount = 0
        self.name = None
        self.type = None
        self.desc = None

        if self.metadata.has_key('wordcount'):
            self.wordcount = int(self.metadata['wordcount'])
        else:
            raise InValidDictError('wordcount is missing in %s' 
                                    % self.ifo)

        if self.metadata.has_key('bookname'):
            self.name = self.metadata['bookname']
        else:
            raise InValidDictError('bookname is missing in %s' 
                                    % self.ifo)

        if self.metadata.has_key('sametypesequence'):
            self.type = self.metadata['sametypesequence']
        else:
            raise InValidDictError('sametypesequence is missing in %s' 
                                    % self.ifo)

        if self.metadata.has_key('description'):
            self.desc = self.metadata['description']

        #log.info("parse stardict index file %s" % self.idx)
        try:
            idx = open(self.idx, 'rb')
        except IOError:
            raise InValidDictError('failed to open %s' % self.idx)

        idxdata = idx.read()
        idx.close()

        start = 0
        for i in range(self.wordcount):
            pos = idxdata.find('\0', start, -1)
            fmt = "%ds" % (pos-start)
            wordstr = struct.unpack_from(fmt, idxdata, start)[0]
            start += struct.calcsize(fmt) + 1

            (off, size) = struct.unpack_from(">LL",idxdata, start)
            start += struct.calcsize(">LL")
            item = cls_worditem(wordstr, off, size)
            self.wordlist.append(item)

        log.info('found dictionary: %s, word count: %d' % 
                        (self.name, self.wordcount))

    def get_words(self):
        return [item.word for item in self.wordlist]

    def get_wordcount(self):
        return self.wordcount

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_description(self):
        return self.desc
        
    def query(self, word):
        start = 0
        end = self.wordcount-1

        while start <= end:
            mid = (start+end) >> 1
            res = cmp(word.lower(), self.wordlist[mid].word.lower())
            if res == 0:
                return self.wordlist[mid]
            elif res > 0:
                start = mid + 1
            else:
                end = mid - 1

        return None


    def get_result(self, worditem):
        if not worditem:
            return None

        try:
            f =  gzip.open(self.data, 'rb')
            f.seek(worditem.offset, 0)
        except IOError:
            return None

        text = f.read(worditem.size)
        f.close()

        return text

    def print_words(self):
        print '\n'. join(self.get_words())


if __name__ == "__main__":
    mgr = cls_stardictmgr()
    word = sys.argv[1]
    if not word:
        sys.exit(-1)

    for dic in mgr.get_dicts():
        item = dic.query(word)
        if item:
            print dic.get_result(item)

    
   
