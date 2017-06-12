import sys
import gi

import config

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

if Gtk.get_major_version() < 3 or Gtk.get_minor_version() < 2:
    sys.exit('Gtk 3.2 is required')

class AppWindow(Gtk.ApplicationWindow):
    """Main application window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(800, 600)

        builder = Gtk.Builder()
        builder.add_from_file("ui/app-window.glade")
        builder.connect_signals(self)

        header_bar = builder.get_object("header_bar")
        self.set_titlebar(header_bar)

        # Display connection list
        box_connect = builder.get_object("box_connect")
        connections = config.get_connections()

        for row in connections:
            button = Gtk.Button(label=row[0])
            button.connect("clicked", self.btn_connect_saved)
            box_connect.pack_start(button, True, True, 0)

        if connections:
            separator = Gtk.Separator(valign="center")
            box_connect.pack_start(separator, True, True, 0)

        add_button = builder.get_object("btn_add_connection")
        box_connect.pack_start(add_button, True, True, 0)

        self.add(box_connect)

        self.set_icon_name("applications-development")
        self.show_all()

        self.connect('delete-event', self.on_destroy)

    def btn_connect_saved(self, button):
        """Connect to saved server on button click"""
        print(button.get_label())

    def btn_add_connection(self, button):
        """Show Add Connection modal on button click"""
        add_dialog = AddConnectionWindow(transient_for=self, modal=True,
                                         skip_taskbar_hint=True)
        add_dialog.present()

    @classmethod
    def on_destroy(self, widget=None, *data):
        config.commit()

class Application(Gtk.Application):
    """Core application class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.phpizza.opensqlpro",
                         **kwargs)

        self.window = None

    def do_startup(self):
        """"""
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        builder = Gtk.Builder()
        builder.add_from_file("ui/app-menu.glade")
        # builder.connect_signals(self)

        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        """Create/raise main window on activate"""
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppWindow(application=self, title="OpenSQL Pro")

        self.window.present()

    def on_about(self, action, param):
        """Show About dialog"""
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_program_name("OpenSQL Pro")
        about_dialog.set_version("0.0.1")
        about_dialog.set_copyright("© Alan Hardman")
        about_dialog.set_comments("A powerfully simple database client")
        # about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file("battery.png"))
        about_dialog.present()

    @staticmethod
    def on_quit(self, action, param):
        """Quit application, saving the config database"""
        # TODO: save application window state
        config.commit()
        self.quit()


class AddConnectionWindow(Gtk.Window):
    """Add connection modal window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/add-dialog.glade")
        self.builder.connect_signals(self)

        header_bar = self.builder.get_object("header_bar")
        self.set_titlebar(header_bar)

        input_grid = self.builder.get_object("input_grid")
        self.add(input_grid)

    def btn_cancel(self, button):
        """Cancel adding a connection from button click"""
        self.close()

    def btn_save(self, button):
        """Save new connection from button click"""
        name = self.builder.get_object("text_name").get_text()
        host = self.builder.get_object("text_host").get_text()
        port = self.builder.get_object("text_port").get_text()
        user = self.builder.get_object("text_user").get_text()
        password = self.builder.get_object("text_pass").get_text()
        config.add_connection(name, host, port, user, password)
        self.close()


if __name__ == "__main__":
    config.init()
    app = Application()
    app.run()
