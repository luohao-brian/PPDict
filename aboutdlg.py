import gtk
from messages import *

class cls_aboutdlg(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        self.set_name(messages[MSGID_PPDICT])
        self.set_program_name(messages[MSGID_PPDICT])
        self.set_version('0.2')
        self.set_authors(['Brian Luo'])
        self.set_website('http://code.google.com/p/ppdict/')
        self.connect('close', lambda: self.destroy())
        self.set_size_request(300, 200)
