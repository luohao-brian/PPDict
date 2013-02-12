import gtk
import pango
import gobject
from simpledb import simpledb
from detailsview import cls_detailsview
from briefview import cls_briefview
from welcomeview import cls_welcomeview

class cls_contentmgr(object):
    def __init__(self, pages):
        self.pages = pages

        self.welcomeview = cls_welcomeview()
        self.welcomeview.update()
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.welcomeview)
        self.pages.append_page(scrolled)

        self.briefview = cls_briefview()
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.briefview)
        self.pages.append_page(scrolled)

        self.detailedview = cls_detailsview()
        self.pages.append_page(self.detailedview)

    def go_for_welcome(self):
        self.pages.set_current_page(0)

    def go_for_brief(self, word):
        self.pages.set_current_page(1)
        self.briefview.update(word)

    def go_for_details(self, word):
        self.pages.set_current_page(2)
        self.detailedview.update(word)
        
        
if __name__ == '__main__':
    pass
        
