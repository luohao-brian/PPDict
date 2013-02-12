import os
import sys
import gtk
from prefs import prefs
from appenv import env, log
from appmain import appmain
from messages import *


class cls_prefsdlg(object):
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file( os.path.join(env.get_ui_dir(),
                           'prefsdlg.glade'))
        builder.connect_signals(self)

        self.window = builder.get_object('window')
        self.window.set_transient_for(appmain.get_root_window())

        self.transparency = builder.get_object('transparency')
        transparency = prefs.getint('transparency')
        self.transparency.set_value(transparency)

        self.btn_viewvalc = builder.get_object('btn_valc')
        self.btn_viewvalc.set_active(not prefs.getbool('viewvalcabuary'))

        self.btn_viewtooltip = builder.get_object('btn_tooltip')
        self.btn_viewtooltip.set_active(not prefs.getbool('viewtooltip'))

        self.fltwinopts = builder.get_object('cb_fltwinopts')
        cell = gtk.CellRendererText()
        self.fltwinopts.pack_start(cell, True)
        self.fltwinopts.add_attribute(cell, 'text', 0)
        self.liststore = gtk.ListStore(str)
        self.liststore.append([messages[MSGID_BY_SEL_RECEIVED]])
        self.liststore.append([messages[MSGID_BY_HOTKEY]])
        self.fltwinopts.set_model(self.liststore)
        self.fltwinopts.set_active(0)

        self.btn_monitor = builder.get_object('btn_monitor')
        self.btn_monitor.set_active(prefs.getbool('monitorsel'))

        if not self.btn_monitor.get_active():
            self.fltwinopts.set_sensitive(False)

        self.btn_autostart = builder.get_object('btn_autostart')
        self.btn_autostart.set_active(prefs.getbool('autostart'))

        self.btn_tray = builder.get_object('btn_trayicon')
        self.btn_tray.set_active(prefs.getbool('tray'))

    def show(self):
        self.window.show_all()

    def delete_event(self, widget, data=None):
        prefs.save()

    def popup_changed(self, widget, data=None):
        active = widget.get_active()
        prefs.set('popupopt', active)

    def transparency_changed(self, widget, data=None):
        transparency = int(widget.get_value())
        appmain.set_transparency(transparency)
        prefs.set('transparency', transparency)

    def hide_valc_toggled(self, widget, data=None):
        hide = widget.get_active()
        if hide:
            appmain.hide_valcabuary()
        else:
            appmain.show_valcabuary()

        prefs.set('viewvalcabuary', not hide)

    def hide_tooltip_toggled(self, widget, data=None):
        hide = widget.get_active()
        if hide:
            appmain.hide_tooltip()

        prefs.set('viewtooltip', not hide)

    def trayicon_toggled(self, widget, data=None):
        tray = widget.get_active()
        prefs.set('tray', tray)
        appmain.set_tray(tray)

    def autostart_toggled(self, widget, data=None):
        autostart = widget.get_active()
        prefs.set('autostart', autostart)
        appmain.set_autostart(autostart)

    def monitor_toggled(self, widget, data=None):
        monitor = widget.get_active()
        prefs.set('monitorsel', monitor)
        self.fltwinopts.set_sensitive(monitor)

if __name__ == "__main__":
    dlg = cls_prefsdlg()
    dlg.show()
    gtk.main()


