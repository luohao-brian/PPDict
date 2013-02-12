import gtk
import pango
import cairo
import gobject
import os
import math
from appenv import env
from prefs import prefs
from valcabuary import valcabuary
from prefixdb import prefixdb
from corrector import corrector
from tooltip import cls_tooltip
from simpledb import simpledb
from contentmgr import cls_contentmgr
from iconmgr import iconmgr
from messages import *

class cls_appmain(object):
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(env.get_ui_dir(), 
                                   'mainwindow.glade'))
        self.builder.connect_signals(self)
        # window
        self.window = self.builder.get_object('window')
        # treeview
        self.treeview = self.builder.get_object('treeview')
        # notebook & content manager
        self.notebook = self.builder.get_object('notebook')
        self.contentmgr = cls_contentmgr(self.notebook)
        self.contentmgr.go_for_welcome()
        # init 3 buttons
        self.btnprefs = self.builder.get_object('btnprefs')
        self.btnprefs.connect_object('event', 
                                    self._btnprefs_pressed, 
                                    self.btnprefs)
        self.btncheck = self.builder.get_object('btncheck')
        self.btnhit = self.builder.get_object('btnhit')
        # status bar
        self.statusbar = self.builder.get_object('statusbar')
        self.statusbar.push(MSGID_COPYRIGHT, 
                            messages[MSGID_COPYRIGHT])
        # input entry
        self.entry = self.builder.get_object('entry')
        self.id_entrychanged = self.entry.connect('changed', 
                                               self._entry_changed)
        # hpaned
        self.hpaned = self.builder.get_object('hpaned')

        
        # init other stuffs
        self.__init_window()
        self.__init_acclgrps()
        self.__init_treeview()
        self.__init_menu()
        self.__init_tooltip()
        self.__init_monitor()
        self.__init_trayicon()
        
    def __init_window(self):
        # init app icon
        self.window.set_icon_from_file(iconmgr.get('ppdict'))

        # configure window according to prefs
        w, h = self.window.get_default_size()
        if h > 0 and w > 0:
            self.window.set_geometry_hints(min_height=h, min_width=w)

        sw = prefs.getint('savedwidth')
        sh = prefs.getint('savedheight')

        if sw < w:
            sw = w

        if sh < h:
            sh = h

        self.window.set_default_size(sw, sh)
        self.set_transparency(prefs.getint('transparency'))

    def __init_monitor(self):
        if not prefs.getbool('monitorsel'):
            return

        # pop up the window when clipboard updtes
        if prefs.getint('popupopt') == 0:
            self.start_monitor_clipboard()
        elif prefs.getint('popupopt') == 1:
            pass


    def __init_tooltip(self):
        # tooltip
        self.tooltip = cls_tooltip()
        self.tooltip.connect('clicked', self._tooltip_clicked)

    def __init_acclgrps(self):
        # init global accel group
        self.agr = gtk.AccelGroup()
        self.window.add_accel_group(self.agr)

        key, mod = gtk.accelerator_parse('<Alt>H')
        self.agr.connect_group(key, mod, gtk.ACCEL_VISIBLE, self._agr_tray_icon)

    def __init_menu(self):
        self.menu = gtk.Menu()

        dicts = gtk.ImageMenuItem(gtk.STOCK_EDIT, self.agr)
        dicts.set_always_show_image(True)
        dicts.set_label('%s...' % messages[MSGID_DICTIONARIES])
        key, mod = gtk.accelerator_parse('<Control>D')
        dicts.add_accelerator('activate', self.agr, 
                               key, mod, gtk.ACCEL_VISIBLE)
        dicts.connect('activate', self._menuitem_edit_dicts_activated)
        self.menu.append(dicts)

        props = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES, self.agr)
        props.set_always_show_image(True)
        props.set_label('%s...' % messages[MSGID_PREFS])
        key, mod = gtk.accelerator_parse('<Control>P')
        props.add_accelerator('activate', self.agr, 
                               key, mod, gtk.ACCEL_VISIBLE)
        props.connect('activate', self._menuitem_edit_props_activated)
        self.menu.append(props)

        sep = gtk.SeparatorMenuItem()
        self.menu.append(sep)

        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT, self.agr)
        about.set_always_show_image(True)
        about.set_label(messages[MSGID_ABOUT])
        key, mod = gtk.accelerator_parse('<Control>B')
        about.add_accelerator('activate', self.agr, 
                               key, mod, gtk.ACCEL_VISIBLE)
        about.connect('activate', self._menuitem_about_activated)
        self.menu.append(about)

        sep = gtk.SeparatorMenuItem()
        self.menu.append(sep)

        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT, self.agr)
        quit.set_always_show_image(True)
        quit.set_label(messages[MSGID_QUIT])
        key, mod = gtk.accelerator_parse('<Control>Q')
        quit.add_accelerator('activate', self.agr, 
                              key, mod, gtk.ACCEL_VISIBLE)
        quit.connect('activate', self._menuitem_quit_activated)
        self.menu.append(quit)
        self.menu.show_all()

        
    def __init_treeview(self):
        self.liststore = gtk.ListStore(str)
        for word in valcabuary:
            self.liststore.append([word])

        self.treeview.append_column(
                        gtk.TreeViewColumn(
                            None, 
                            gtk.CellRendererText(), 
                            text=0))

        self.treeview.set_model(self.liststore)
        self.treeview.set_cursor_on_cell(0)
        self.treeview.connect('row-activated', 
                                self._treeview_row_activated)

        self.id_cursorchanged = self.treeview.connect(
                                'cursor-changed', 
                                self._treeview_cursor_changed)


    def __init_trayicon(self):
        pixbuf = iconmgr.get_pixbuf('ppdict', gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.trayicon = gtk.status_icon_new_from_pixbuf(pixbuf)
        self.trayicon.connect('popup-menu', self._tryicon_menu_popup)
        self.trayicon.connect('activate', self._menuitem_resume_activated)
        self.set_tray(prefs.getbool('tray'))

    def _agr_tray_icon(self, agr, accel, key, mod):
        self.window.emit('delete-event', None)

    def _tryicon_menu_popup(self, widget, button, time, data=None):
        menu = gtk.Menu()

        resume = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        resume.set_always_show_image(True)
        resume.set_label(messages[MSGID_RESUME])
        resume.connect('activate', self._menuitem_resume_activated)
        menu.append(resume)
        
        menu.append(gtk.SeparatorMenuItem())

        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit.set_always_show_image(True)
        quit.set_label(messages[MSGID_QUIT])
        quit.connect('activate', self._menuitem_quit_activated)
        menu.append(quit)

        menu.show_all()
        menu.popup(None, None, None, button, time, None)
        
    def _entry_focus_out_event(self, widget, data=None):
        self.hide_tooltip()

    #(double clicked or press enter key) within the word list
    def _treeview_row_activated(self, widget, path, column, data=None):
        model = widget.get_model()
        wordsel = model[path[0]][0]
        self.entry.disconnect(self.id_entrychanged)
        self.entry.set_text(wordsel)
        self.id_entrychanged = self.entry.connect('changed', self._entry_changed)
        self.contentmgr.go_for_details(wordsel)

    def _treeview_cursor_changed(self, widget, data=None):
        sel = self.treeview.get_selection()
        model, iter = sel.get_selected()

        if not iter:
            return

        word = model.get(iter, 0)[0]
        self.entry.disconnect(self.id_entrychanged)
        self.entry.set_text(word)
        self.contentmgr.go_for_brief(word)
        self.id_entrychanged = self.entry.connect('changed', self._entry_changed)

       
    def _reposition_menu(self, widget, data=None):    
        # wmenu refers to the width of the menu;
        # widget.allocation will not work at the first call,
        # so widget.requisition is required
        wmenu = widget.requisition.width

        # coordinates of right-bottom corner of prefs button,
        # the menu should not go across the right of that line.
        (x, y) = self.btnprefs.translate_coordinates(self.window, 
                                self.btnprefs.requisition.width, 
                                self.btnprefs.requisition.height)

        # self.window.window refers to gtk.gdk.window
        (xwin, ywin) = self.window.window.get_position() 

        return (xwin+x-wmenu-2, ywin+y+2, True)

    def _btnprefs_pressed(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.menu.popup(None, None, self._reposition_menu, 
                            event.button, event.time)
            return True

        return False
        

    def _btncheck_released(self, widget, data=None):
        word = self.entry.get_text()
        word = word.strip()

        if not word:
            return

        pos = valcabuary.hit(word)
        if pos >= 0:
            return

        corrected = corrector.correct(word)
        if corrected != word:
            self.entry.set_text(corrected)

    def _btnhit_released(self, widget, data=None):
        sel = self.treeview.get_selection()
        model, iter = sel.get_selected()

        if not iter:
            return

        word = model.get(iter, 0)[0]
        self.contentmgr.go_for_details(word)


    def _btnhit_activated(self, widget, data=None):
        self._btnhit_released(widget, data)

    def _tooltip_clicked(self, widget, data):
        self.entry.set_text(data)

    def _entry_changed(self, widget, data=None):
        pos = -1
        word = self.entry.get_text()
        if word:
            pos = valcabuary.hit(word)
            if pos < 0:
                pos = valcabuary.auto_complete(word)

        if pos < 0:
            self.contentmgr.go_for_welcome()
            pos = 0
            self.hide_tooltip()
        else:
            word = valcabuary[pos]
            self.contentmgr.go_for_brief(word)
            self.present_tooltip(word)
            
        # update treeview if it is visible
        if prefs.getbool('viewvalcabuary'):
            self.treeview.disconnect(self.id_cursorchanged)
            self.treeview.set_cursor_on_cell(pos)
            self.treeview.scroll_to_cell(pos, None, True, 0, 0.0)
            self.id_cursorchanged = self.treeview.connect(
                                'cursor-changed', 
                                self._treeview_cursor_changed)

    def _delete_event(self, widget, data=None):
        if prefs.getbool('tray'):
            self.set_tray(True)
            self.window.hide()
            return True

        return False

    def _window_destroy(self, widget, data=None):
        w, h = self.window.get_size()
        prefs.set('savedwidth', w)
        prefs.set('savedheight', h)
        prefs.save()
        gtk.main_quit()

    def _menuitem_resume_activated(self, widget, data=None):
        self.show()

    def _menuitem_quit_activated(self, widget, data=None):
        self.window.emit('destroy')

    def _menuitem_about_activated(self, widget, data=None):
        from aboutdlg import cls_aboutdlg
        dlg = cls_aboutdlg()
        dlg.run()
        dlg.destroy()

    def _menuitem_edit_dicts_activated(self, widget, data=None):
        from dbmgrdlg import cls_dbmgrdlg
        dlg = cls_dbmgrdlg()
        dlg.show()

    def _menuitem_edit_props_activated(self, widget, data=None):
        from prefsdlg import cls_prefsdlg
        dlg = cls_prefsdlg()
        dlg.show()


    def _clipboard_changed(self, clipboard, event):
        text = clipboard.wait_for_text()
        if not text:
            return

        text = text.lower()
        pos = valcabuary.hit(text)
        if pos < 0:
            return

        # retrieve mouse postion
        screen = self.window.get_screen()
        rootwin = screen.get_root_window()
        mousex, mousey, mods = rootwin.get_pointer()

        from floatwin import cls_floatwin
        flwin = cls_floatwin()
        flwin.update(text)

        # present the float window
        flwin.move(mousex, mousey)
        flwin.composited_show()

    def show(self):
        self.window.show_all()
        if not prefs.getbool('viewvalcabuary'):
            self.hide_valcabuary()

    # reposition and show tooltip if it is enabled 
    def present_tooltip(self, word):
        if not prefs.getbool('viewtooltip'):
            return

        x, y = self.entry.translate_coordinates(self.window, 
                                    0, 
                                    self.entry.requisition.height)
        xwin, ywin = self.window.window.get_position()
        self.tooltip.move(xwin + x + 16, ywin + y)
        self.tooltip.set_text(word)
        self.tooltip.show_all()

    def hide_tooltip(self):
        self.tooltip.hide()

    def set_transparency(self, trans):
        if trans > 100 or trans < 0:
            return

        opacity = float(100-trans)/100.0
        self.window.set_opacity(opacity)

    def run(self):
        gtk.main()

    def set_tray(self, enabled):
        self.trayicon.set_visible(enabled)

    def get_root_window(self):
        return self.window

    def show_valcabuary(self):
        self.hpaned.set_position(100)

    def hide_valcabuary(self):
        self.hpaned.set_position(0)

    def start_monitor_clipboard(self):
        clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
        self.id_monitorcb = clipboard.connect('owner-change', self._clipboard_changed)

    def stop_monitor_clipboard(self):
        self.disconnect(self.id_monitorcb)

    def set_autostart(self, enabled):
        from platform import platform
        platform.set_autostart(enabled)

appmain = cls_appmain()

if __name__ == '__main__':
    appmain.show()
    appmain.run()

