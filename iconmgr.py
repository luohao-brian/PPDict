import os
import gtk
from appenv import env

class cls_iconmgr(object):
    def __init__(self):
        self.icons = dict()
        iconsdir = env.get_icons_dir()

        for entry in os.listdir(iconsdir):
            if entry[-4:].lower() == '.png':
                self.icons[entry[:-4].lower()] = os.path.join(iconsdir, entry)


    def get(self, name):
        if self.icons.has_key(name):
            return self.icons[name]

        return None

    def get_pixbuf(self, name, icon_size=None):
        icon = self.get(name)
        if not icon:
            return None

        pixbuf = gtk.image_new_from_file(icon).get_pixbuf()
        if icon_size:
            w, h = gtk.icon_size_lookup(icon_size)
            pixbuf = pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)

        return pixbuf

    def debug(self):
        for item in self.icons.items():
            print item

iconmgr = cls_iconmgr()

if __name__ == "__main__":
    iconmgr.debug()            
