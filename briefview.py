import gtk
import pango
from simpledb import simpledb

class cls_briefview(gtk.TextView):
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

        self.tags['soundmark'] = self.buf.create_tag(None,
                                            foreground = '#888888',
                                            scale = pango.SCALE_MEDIUM)
        self.tags['keyword'] = self.buf.create_tag(None,
                                            weight = pango.WEIGHT_BOLD,
                                            scale = pango.SCALE_LARGE)


    def update(self, word):
        soundmark, desc = simpledb.query(word)
        self.buf.set_text('')
        cur = self.buf.get_start_iter()
        self.buf.insert_with_tags(cur, '%s ' % word, self.tags['keyword'])
        self.buf.insert_with_tags(cur, '%s' % soundmark, self.tags['soundmark'])
        self.buf.insert(cur, '\n%s' % desc)

