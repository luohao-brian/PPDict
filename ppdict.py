import os
import ConfigParser
from stardict import cls_stardict
from appenv import log, env
from errors import NotFoundError, InvalidDictError

class cls_ppdictmgr(object):
    def __init__(self):        
        self.conf = os.path.join(env.get_work_dir(), 'database.cf')
        self.status = dict()
        self.dicts = list()
        self.scan_dicts()
        try:
            self.load_status()
        except IOError:
            self.save_status()

    def scan_dicts(self):     
        if not os.path.isdir(env.get_dict_dir()):
            log.warn('dir %s not exists' % env.get_data_dir())
            return

        for dirent in os.listdir(env.get_dict_dir()):
            uri = os.path.join(env.get_dict_dir(), dirent)
            if not os.path.isdir(uri):
                continue

            try:
                candidate = cls_ppdict(uri)
                self.dicts.append(candidate)
            except NotFoundError, e:
                log.warn('not found: %s' % e)
                continue
            except InvalidDictError, e:
                log.warn('invalid dictionary: %s' % e)
                continue
   
    def load_status(self):
        for dic in self.dicts:
            self.status[dic.get_name()] = (0, False)
        
        parser = ConfigParser.ConfigParser()
        with open(self.conf, 'r') as fp:
            parser.readfp(fp)
            fp.close()

        for section in parser.sections():
            if section not in self.status.keys():
                continue

            seq = parser.getint(section, 'sequence')
            disabled = parser.getboolean(section, 'disabled')
            self.status[section] = (seq, disabled)
                

    def save_status(self):
        parser = ConfigParser.ConfigParser()
        for item in self.status.items():
            parser.add_section(item[0])
            parser.set(item[0], 'sequence', item[1][0])
            parser.set(item[0], 'disabled', item[1][1])

        try:
            with open(self.conf, 'w') as fp:
                parser.write(fp)
                fp.close()
        except IOError:
            log.warn('cannot write to %s' % self.conf)
            pass

    def get_dicts(self):
        return sorted(self.dicts, 
                    key=lambda x: self.status[x.get_name()][0])


    def get_seq(self, name):
        if name in self.status.keys():
            return self.status[name][0]

        return 0

    def get_disabled(self, name):
        if name in self.status.keys():
            return self.status[name][1]

        return True

    def set_seq(self, name, seq):
        if name in self.status.keys():
            self.status[name][0] = seq

    def set_disabled(self, name, disabled):
        if name in self.status.keys():
            self.status[name][1] = disabled
       

class cls_ppdict(cls_stardict):
    def __init__(self, uri):
        cls_stardict.__init__(self, uri)
        self.logo = None
        if self.metadata.has_key('logo'):
            self.logo = os.path.join(self.uri, self.metadata['logo'])

    def get_logo(self):
        return self.logo


ppdictmgr = cls_ppdictmgr()

if __name__ == "__main__":
    import sys
    mgr = cls_ppdictmgr()
    dicts = mgr.get_dicts()
    for dic in dicts:
        name = dic.get_name()
        print 'DICT: %s' % name
        print '  Sequence: %d' % mgr.get_seq(name)
        print '  Disabled: %s' % mgr.get_disabled(name)
        print '  Logo: %s' % dic.get_logo()
