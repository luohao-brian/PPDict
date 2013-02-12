import os
import ConfigParser
from appenv import env, log


class cls_prefs(object):
    def __init__(self):
        self.defaults = {
            'autostart':        True,
            'tray':             True,
            'viewtooltip':      True,
            'viewvalcabuary':   True, 
            'monitorsel':       True,
            'popupopt':         '0',
            'transparency':     '100',
            'savedwidth':       '600',
            'savedheight':      '400',
        }

        self.parser = ConfigParser.ConfigParser(self.defaults)
        try:
            self.load()
        except IOError:
            self.save()
            self.load()

    def load(self):
        with open(env.get_prefs_file(), 'r') as config:
            self.parser.readfp(config)
            config.close()

    def save(self):
        try:
            with open(env.get_prefs_file(), 'w') as config:
                self.parser.write(config)
                config.close()
        except IOError:
            log.warn('cannot write to %s' % env.get_prefs_file())
            pass

    def get(self, key):
        try:
            return self.parser.get('DEFAULT', key, vars=self.defaults)
        except ConfigParser.NoOptionError:
            log.warn('get unknow option %s' % key)
            return None
        except ConfigParser.NoSectionError:
            return None

    def getbool(self, key):
        if key not in self.defaults.keys():
            log.warn('get unknow option %s' % key)
            return None

        return self.parser.getboolean('DEFAULT', key)

    def getint(self, key):
        if key not in self.defaults.keys():
            log.warn('get unknow option %s' % key)
            return None

        return self.parser.getint('DEFAULT', key)

    def set(self, key, val):
        if key not in self.defaults.keys():
            log.warn('set unknow option %s' % key)
            return

        self.parser.set('DEFAULT', key, str(val))    


prefs = cls_prefs()

if __name__ == '__main__':
    print 'not exist: %s' % str(prefs.get('notexist'))
    tray = prefs.getbool('tray')
    print 'tray: %s' % str(prefs.getbool('tray'))

    prefs.set('tray', not tray)
    print 'tray: %s' % str(prefs.getbool('tray'))
    prefs.save()
