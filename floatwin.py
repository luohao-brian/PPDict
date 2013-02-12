import gtk
import pango
import cairo
import gobject
from simpledb import simpledb

class cls_floatview(gtk.TextView):
    def __init__(self):
        gtk.TextView.__init__(self)
        self.buf = gtk.TextBuffer()
        self.set_buffer(self.buf)
        self.set_left_margin(10)
        self.set_right_margin(10)
        color = gtk.gdk.Color(0x8888, 0x8888, 0x8888)
        self.tags = dict()
        self.tags['soundmark'] = self.buf.create_tag(None,
                                            foreground_gdk = color,
                                            scale = pango.SCALE_MEDIUM)
        self.tags['keyword'] = self.buf.create_tag(None,
                                            weight = pango.WEIGHT_BOLD,
                                            scale = pango.SCALE_LARGE)

    def update(self, word):
        soundmark, desc = simpledb.query(word)
        self.buf.set_text('')
        iter = self.buf.get_start_iter()
        self.buf.insert_with_tags(iter, '%s ' % word, self.tags['keyword'])
        self.buf.insert_with_tags(iter, '%s' % soundmark, self.tags['soundmark'])
        self.buf.insert(iter, '\n%s' % desc)

class cls_floatwin(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_TOOLTIP)
        self.set_app_paintable(True)
        self.set_border_width(10)
        self.view = cls_floatview()
        self.add(self.view)
        self.connect('expose-event', self.expose_event)
        self.connect('screen-changed', self.screen_changed)
        self.screen_changed(self, None, None)
        self.connect('leave_notify_event', self.mouse_leave)

    def expose_event(self, widget, event, data=None):
        # clear the parent backgroud, make it totally transparent
        cr = widget.window.cairo_create()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        region = gtk.gdk.region_rectangle(event.area)
        cr.region(region)
        cr.fill()

        return False

    def screen_changed(self, widget, old_screen, data=None):
        # recreate colormap
        screen = widget.get_screen()
        self.colormap = screen.get_rgba_colormap()
        widget.set_colormap(self.colormap)

    def mouse_leave(self, widget, event, data=None):
        self.destroy()

    def window_expose_event(self, widget, event):
        win = self.view.get_window(gtk.TEXT_WINDOW_WIDGET)
        cr = widget.window.cairo_create()
        cr.set_source_pixmap(win, *win.get_position())

        x, y = win.get_position()
        w, h = win.get_size()
        region = gtk.gdk.region_rectangle((x, y, w, h)) 
        r = gtk.gdk.region_rectangle(event.area)
        region.intersect(r)
        cr.region (region)
        cr.clip()

        cr.set_operator(cairo.OPERATOR_OVER)
        cr.paint_with_alpha(0.9)
        return False

    def update(self, word):
        self.view.update(word)

    def composited_show(self):
        gtk.Window.show_all(self)
        viewwidget = self.view.get_window(gtk.TEXT_WINDOW_WIDGET)
        viewwidget.set_composited(True)
        self.connect_after("expose-event", self.window_expose_event)


if __name__ == '__main__':
    fw = cls_floatwin()
    fw.update_word('hello')
    fw.show_all()
    gtk.main()
