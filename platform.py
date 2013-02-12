import os
from appenv import log, env

XINITRC_START = '#START PPDICT AUTOSTART(DO NOT REMOVE THIS LINE)'
XINITRC_END = '#END PPDICT AUTOSTART(DO NOT REMOVE THIS LINE)'

class cls_platform(object):
    def __init__(self):
        sysinfo = os.uname()
        self.sysname = sysinfo[0] 
        self.distro = sysinfo[1]

    def get_sysname(self):
        return self.sysname

    def get_distro(self):
        return self.distro

    def get_web_browser(self):
        if self.sysname == 'Linux' and self.distro == 'ubuntu':
            return os.path.join('/etc', 'alternatives', 'x-www-browser')

    def set_autostart(self, enabled):
        xinitrc = os.path.join(env.get_home_dir(), '.xinitrc')
        lines = list()

        try:
            with open(xinitrc, 'r') as fp:
                lines = fp.readlines()                
                fp.close()
        except IOError:
            pass

        start = end = -1

        pos = 0
        for line in lines:
            if line.startswith(XINITRC_START):
                start = pos
            elif line.startswith(XINITRC_END):
                end = pos

            pos += 1

        if start >= 0 and end > start and not enabled:
            a=start
            b=start+1
            c=start+2
            del lines[a:b:c]
        elif start < 0 and end < 0 and enabled:
            lines.append('%s\n' % XINITRC_START)
            lines.append('ppgui\n')
            lines.append('%s\n' % XINITRC_END)
            
        try:    
            with open(xinitrc, 'w') as fp:
                fp.writelines(lines)                
                fp.close()
        except IOError:
            pass
        
platform = cls_platform()
