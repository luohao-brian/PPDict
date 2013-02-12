import gtk
import pango
from iconmgr import iconmgr

welcome = '  Welcome to PPdict!\n\n'
usage = '\tPress Ctrl+Q to quit; Press Alt+H to hide; Selecting a word on screen will pop up a float window to translate it.\n\n'
infomation = '\tFor more information or reporting a bug, welcome to PPdict homepage '
homepage =  'https://github.com/luohao-brian/ppdict'

class cls_welcomeview(gtk.TextView):
    def __init__(self):
        gtk.TextView.__init__(self)
        self.buf = gtk.TextBuffer()
        self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.set_buffer(self.buf)
        self.set_left_margin(10)
        self.set_right_margin(10)
        self.set_editable(False)
        self.set_cursor_visible(True)
        self.tags = dict()
        self.tags['welcome'] = self.buf.create_tag(None,
                                        rise = 4*1024)
        self.tags['homepage'] = self.buf.create_tag(None, 
                                        foreground = 'blue',
                                        underline=pango.UNDERLINE_SINGLE)
        self.tags['homepage'].connect("event", self.homepage_event)

    def update(self):
        self.buf.set_text('')
        pos = self.buf.get_end_iter()
        pixbuf = iconmgr.get_pixbuf('welcome', gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.buf.insert_pixbuf(pos, pixbuf)
        self.buf.insert_with_tags(pos, welcome, self.tags['welcome'])
        self.buf.insert(pos, usage)
        self.buf.insert(pos, infomation)
        self.buf.insert_with_tags(pos, homepage, self.tags['homepage']) 
        self.buf.insert(pos, '.\n\n')

    def homepage_event(self, tag, widget, event, iter):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from platform import platform
            import subprocess
            browser = platform.get_web_browser()
            subprocess.call([browser, homepage])
        #elif event.type == gtk.gdk.MOTION_NOTIFY:
        #    self.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
