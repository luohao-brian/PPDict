import os
import sys
import gtk
import pango
import gobject
from appenv import env, log
from appmain import appmain
from ppdict import ppdictmgr


class cls_dbmgrdlg(object):
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file( os.path.join(env.get_ui_dir(), 
                           'dbmgrdlg.glade'))
        builder.connect_signals(self)

        self.window = builder.get_object('window')
        self.window.set_transient_for(appmain.get_root_window())

        self.treeview = builder.get_object('treeview')
        self.treeview.set_has_tooltip(False)
        render = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn(None, render, pixbuf=0)
        column.set_expand(False)
        self.treeview.append_column(column)

        render = gtk.CellRendererText()
        render.set_property('ellipsize', pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn(None, render, text=1)
        column.set_expand(True)
        self.treeview.append_column(column)

        render = gtk.CellRendererToggle()
        render.connect('toggled', self.on_item_toggled)
        column = gtk.TreeViewColumn(None, render, active=2)
        column.set_expand(False)
        self.treeview.append_column(column)

        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING, 
                                       gobject.TYPE_BOOLEAN)

        for dic in ppdictmgr.get_dicts():
            name = dic.get_name()
            disabled = ppdictmgr.get_disabled(name)
            logo = dic.get_logo()
            pixbuf = gtk.image_new_from_file(logo).get_pixbuf()
            w, h = gtk.icon_size_lookup(gtk.ICON_SIZE_LARGE_TOOLBAR)
            pixbuf = pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)

            self.liststore.append([pixbuf, name, not disabled])

        self.treeview.set_model(self.liststore)

    def show(self):
        self.window.show_all()

    def on_item_toggled(self, cell, path, data=None):
        #iter = self.liststore.get_iter(path)
        #checked = self.liststore.get_value(iter, 0)
        #checked = not checked
        #self.liststore.set(iter, 0, checked)
        pass

    def on_down_released(self, widget, data=None):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return

        next = model.iter_next(iter)
        if not next:
            return

        model.swap(iter, next)

    def on_up_released(self, widget, data=None):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return

        # see pygtk FAQ section 13.51
        def iter_prev(model, iter):
            path = model.get_path(iter)
            position = path[-1]
            if position == 0:
                return None
            prev_path = list(path)[:-1]
            prev_path.append(position - 1)
            prev = model.get_iter(tuple(prev_path))
            return prev

        prev = iter_prev(model, iter)
        if not prev:
            return

        model.swap(iter, prev)

    def on_window_deleted(self, widget, data=None):
        return False


if __name__ == "__main__":
    dlg = cls_dbmgrdlg()
    dlg.show()
    gtk.main()
