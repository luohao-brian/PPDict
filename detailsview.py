import gtk
import pango
from HTMLParser import HTMLParser
from ppdict import ppdictmgr
from messages import *

# ppdict content attempts to be compatible with html
#
# 1. ppdict magic
# <!--ppdict version 1.0-->
#
# 2. tags
# <b> bold <b>
# <i> italic </i>
# <u> underline </u>
# <a href=''> link </a>
# <br> break
# <ul> non-sequent list </ul>
# <ol> sequent list </ol>
# <li> list item </li>
# <span STYLE=styles> embedded </span>
# <font ATTRs></font>
# <hr>

# 3. span styles
# font-family
# font-size 
# font-weight 
# font
# background-color
# color
# text-align
# text-indent

# 4. font attrs
# color 

class cls_stack(list):
    def __init__(self):
        list.__init__(self)

    def push(self, item):
        self.insert(-1, item)

    def pop(self):
        del self[0]

    def get(self):
        return self[0]


class cls_htmlparser(HTMLParser):
    def __init__(self, textview):
        HTMLParser.__init__(self)
        self.tv = textview
        self.buf = textview.get_buffer()
        self.tags = cls_stack()
        self.reserved = dict()
        self.init_reserved_tags()
        self.applicable_tags = ['font', 'b', 'u', 'i']

    def init_reserved_tags(self):
        self.reserved['bold'] = self.buf.create_tag(None, weight = pango.WEIGHT_BOLD)
        self.reserved['italic'] = self.buf.create_tag(None, style = pango.STYLE_ITALIC)
        self.reserved['underline'] = self.buf.create_tag(None, underline = pango.UNDERLINE_SINGLE)

    def handle_data(self, data):
        self.buf.insert_with_tags(self.cur, data, *self.tags)

    def handle_starttag(self, tag, attrs):
        if tag == 'font':
            for attr in attrs:
                if isinstance(attr, tuple) and len(attr) == 2 and attr[0] == 'color':
                    color = gtk.gdk.color_parse(attr[1])
                    self.tags.push(self.buf.create_tag(None, foreground_gdk = color))
                    break
        elif tag == 'br':
            self.buf.insert(self.cur, '\n')
        elif tag == 'b':
            self.tags.push(self.reserved['bold'])
        elif tag == 'u':
            self.tags.push(self.reserved['underline'])
        elif tag == 'i':
            self.tags.push(self.reserved['italic'])
        
    def handle_endtag(self, tag):
        if tag in self.applicable_tags:
            self.tags.pop()

    def feed(self, data):
        self.cur = self.buf.get_end_iter()
        HTMLParser.feed(self, data)
        
class cls_textparser(object):
    def __init__(self, textview):
        self.tv = textview
        self.buf = textview.get_buffer()

    def feed(self, data):
        cur = self.buf.get_end_iter()
        self.buf.insert(cur, data)

class cls_ppdictview(gtk.TextView):
    def __init__(self):
        gtk.TextView.__init__(self)
        self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.buf = gtk.TextBuffer()
        self.set_buffer(self.buf)
        
        self.set_editable(False)
        self.set_cursor_visible(True)
        self.set_left_margin(10)
        self.set_right_margin(10)
        
        self.tags = dict()
        self.tags['name'] = self.buf.create_tag(None, 
                                weight = pango.WEIGHT_BOLD,
                                rise = 2*1024,
                                background = '#aaaaaa',
                                foreground = '#ffffff')

    def feed(self, word):
        # clean up the existing content first
        self.buf.set_text('') 

        # show cotent from every database 
        for db in ppdictmgr.get_dicts():
            name = db.get_name()

            # skip database that is disabled
            if ppdictmgr.get_disabled(name):
                continue

            # skip database in which word not found
            item = db.query(word)
            if not item:
                continue

            parser = None
            if db.get_type() == 'h':
                parser = cls_htmlparser(self)
            elif db.get_type() == 'm':
                parser = cls_textparser(self)
            else:
                continue

            # put dictionary header
            logo = db.get_logo()
            pixbuf = gtk.image_new_from_file(logo).get_pixbuf()
            w, h = gtk.icon_size_lookup(gtk.ICON_SIZE_SMALL_TOOLBAR)
            pixbuf = pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
            pos = self.buf.get_end_iter()
            self.buf.insert_pixbuf(pos, pixbuf)
            self.buf.insert(pos, '  ')
            self.buf.insert_with_tags(pos, ' %s ' % db.get_name(),
                                      self.tags['name'])
            self.buf.insert(pos, '\n')

            content = db.get_result(item)
            parser.feed(content)
            self.buf.insert(self.buf.get_end_iter(), '\n\n')
          
class cls_detailsview(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        self.set_show_border(True)
        self.set_show_tabs(True)
        self.popup_disable()
        self.init_ppdict_page()

    def update(self, word):
        self.ppdictview.feed(word)

    def init_ppdict_page(self):
        self.ppdictview = cls_ppdictview()

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.ppdictview)

        label = gtk.Label()
        label.set_use_markup(True)
        label.set_markup('<b>%s</b>' % messages[MSGID_DICTIONARIES])

        self.append_page_menu(scrolled, label, None)

