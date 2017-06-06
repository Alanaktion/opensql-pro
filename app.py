import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

if Gtk.get_major_version() < 3 or Gtk.get_minor_version() < 2:
    sys.exit('Gtk 3.2 is required')


class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        builder = Gtk.Builder()
        builder.add_from_file("app-window.glade")

        hb = builder.get_object("header_bar")
        self.set_titlebar(hb)

        button_connections = builder.get_object("btn_connections")
        menu_connections = builder.get_object("menu_connections")
        button_connections.set_popover(menu_connections)

class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.phpizza.opensqlpro",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN,
                         **kwargs)
        self.window = None

        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
        #                      GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        builder = Gtk.Builder()
        builder.add_from_file("app-menu.glade")
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
        about_dialog.present()

    def onButtonPressed(self, button):
        print("Hello World!")


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
