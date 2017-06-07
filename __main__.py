import os
import sys
import gi

import config

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

if Gtk.get_major_version() < 3 or Gtk.get_minor_version() < 2:
    sys.exit('Gtk 3.2 is required')

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        builder = Gtk.Builder()
        builder.add_from_file("ui/app-window.glade")

        header_bar = builder.get_object("header_bar")
        self.set_titlebar(header_bar)

        # Add connections to menu
        menu_connect = builder.get_object("menu_connect")
        menu_connections = builder.get_object("menu_connect_connections")

        for row in config.cursor().execute('SELECT * FROM connections'):
            button = Gtk.ModelButton(label=row[1])
            # button.connect("clicked", self.on_button_clicked)
            menu_connections.pack_start(button, True, True, 0)

        # Bind connection menu
        btn_connect = builder.get_object("btn_connect")
        btn_connect.set_popover(menu_connect)

        self.set_icon_name("applications-development")
        self.show_all()
        # self.maximize()

class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.phpizza.opensqlpro",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN,
                         **kwargs)

        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        builder = Gtk.Builder()
        builder.add_from_file("ui/app-menu.glade")
        # builder.connect_signals(self)

        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppWindow(application=self, title="OpenSQL Pro")

        self.window.present()

    def do_open(self, file):
        print("file opened yay")

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        # about_dialog.set_program_name("OpenSQL Pro")
        about_dialog.set_version("0.0.1")
        about_dialog.set_copyright("© Alan Hardman")
        about_dialog.set_comments("A powerfully simple database client")
        # about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file("battery.png"))
        about_dialog.present()

    def on_quit(self, action, param):
        config.commit()
        self.quit()

if __name__ == "__main__":
    config.init()
    app = Application()
    app.run()
