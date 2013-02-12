import gtk
import pango
import cairo
import gobject
import math

class cls_tooltip_view(gtk.EventBox):
    __gsignals__ = { 
      'clicked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )), 
    } 

    def __init__(self):
        gtk.EventBox.__init__(self)
        self.set_app_paintable(True)
        self.set_events(gtk.gdk.BUTTON_RELEASE |
                        gtk.gdk.ENTER_NOTIFY |
                        gtk.gdk.LEAVE_NOTIFY |
                        gtk.gdk.BUTTON_PRESS)
        self.connect("expose-event", self.expose_event)
        self.connect('enter_notify_event', self.mouse_over)
        self.connect('leave_notify_event', self.mouse_leave)
        self.connect('button_press_event', self.button_press)
        self.connect('button_release_event', self.button_release)

        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_single_line_mode(True)
        self.label.modify_fg(gtk.STATE_NORMAL,
                            gtk.gdk.Color(0xcccc, 0xcccc, 0xcccc))
        self.add(self.label)

    def set_text(self, text):
        self.label.set_text(text)
        w, h = self.label.get_layout().get_size()
        self.set_size_request(w/pango.SCALE + 4, h/pango.SCALE + 4)

    def set_markup(self, markup):
        self.label.set_markup(markup)

    def mouse_over(self, widget, event, data=None):
        self.label.modify_fg(gtk.STATE_NORMAL,
                            gtk.gdk.Color(0xffff, 0xffff, 0xffff))
        return False

    def button_press(self, widget, event, data=None):
        self.label.modify_fg(gtk.STATE_NORMAL,
                            gtk.gdk.Color(0x0, 0x0, 0xcccc))
        self.label.set_markup('<b>%s</b>' % self.label.get_text())
        return False

    def button_release(self, widget, event, data=None):
        self.label.modify_fg(gtk.STATE_NORMAL,
                            gtk.gdk.Color(0xcccc, 0xcccc, 0xcccc))
        self.label.set_text(self.label.get_text())
        self.emit('clicked', self.label.get_text())
        return False

    def mouse_leave(self, widget, event, data=None):
        self.label.modify_fg(gtk.STATE_NORMAL,
                            gtk.gdk.Color(0xcccc, 0xcccc, 0xcccc))
        return False

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        #cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.set_source_rgba (0, 0, 0, 0.8)

        cr.rectangle(event.area)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        return False

class cls_tooltip(gtk.Window):
    __gsignals__ = { 
      'clicked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )), 
    } 

    def __init__(self):
        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_TOOLTIP)
        self.set_app_paintable(True)
        self.set_border_width(10)
        self.radius = 8
        self.view = cls_tooltip_view()
        self.view.connect('clicked', self.view_clicked)
        self.add(self.view)

        self.connect('expose-event', self.expose_event)
        self.connect('screen-changed', self.screen_changed)
        self.screen_changed(self, None, None)


    def set_text(self, text):
        self.view.set_text(text)

    def set_markup(self, markup):
        self.view.set_markup(markup)

    def expose_event(self, widget, event, data=None):
        ctx = widget.window.cairo_create()
        ctx.set_source_rgba (0, 0, 0, 0.8)

        ctx.rectangle(event.area)
        ctx.clip()


        # draw the background
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()

        # draw rounded coners around the window
        r = self.radius
        lw = ctx.set_line_width(3)

        w, h = widget.window.get_size()
        ctx.set_operator(cairo.OPERATOR_CLEAR)

        #   A****BQ 
        #  H      C 
        #  *      * 
        #  G      D 
        #   F****E 
        # Arc from B to C (-90 degrees to 0 degree)
        ctx.arc(w-r, r, r, -math.pi/2, 0 )
        # Move to B     
        ctx.move_to(w-r, 0)
        # straight line to Q
        ctx.line_to(w, 0)
        # straight line to C
        ctx.line_to(w, r)

        ctx.arc(w-r, h-r, r, 0, math.pi/2)
        ctx.move_to(w, h-r)
        ctx.line_to(w, h)
        ctx.line_to(w-r, h)

        ctx.arc(r, h-r, r, math.pi/2, math.pi)
        ctx.move_to(r, h)
        ctx.line_to(0, h)
        ctx.line_to(0, h-r)

        ctx.arc(r, r, r, math.pi, -math.pi/2)
        ctx.move_to(0, r)
        ctx.line_to(0, 0)
        ctx.line_to(r, 0)

        ctx.stroke()
        ctx.fill()

        return False

    def screen_changed(self, widget, old_screen, data=None):
        screen = widget.get_screen()
        self.colormap = screen.get_rgba_colormap()
        widget.set_colormap(self.colormap)

    def view_clicked(self, widget, data):
        self.emit('clicked', data)

if __name__ == '__main__':
    tooltip = cls_tooltip()
    tooltip.set_position(gtk.WIN_POS_CENTER)
    tooltip.set_text('world hello hello')
    tooltip.show_all()
    gtk.main()
