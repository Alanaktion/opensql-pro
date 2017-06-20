import sys
import gi

import config

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gio, Gtk, GtkSource

if Gtk.get_major_version() < 3 or Gtk.get_minor_version() < 2:
    sys.exit('Gtk 3.2 is required')

class AppWindow(Gtk.ApplicationWindow):
    """Main application window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(800, 600)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/app-window.glade")
        self.builder.connect_signals(self)

        header_bar = self.builder.get_object("header_bar")
        self.set_titlebar(header_bar)

        # Display connection list
        box_connect = self.builder.get_object("box_connect")
        connections = config.get_connections()

        for row in connections:
            button = Gtk.Button(label=row[0])
            button.connect("clicked", self.btn_connect_saved)
            box_connect.pack_start(button, True, True, 0)

        if connections:
            separator = Gtk.Separator(valign="center")
            box_connect.pack_start(separator, True, True, 0)

        add_button = self.builder.get_object("btn_add_connection")
        box_connect.pack_start(add_button, True, True, 0)

        self.add(box_connect)

        self.set_icon_name("applications-development")
        self.show_all()

        self.edit_query = None

        self.connect('delete-event', self.on_destroy)

    def btn_connect_saved(self, button):
        """Connect to saved server on button click"""
        # TODO: Actually connect to the server

        # Remove connection UI
        self.builder.get_object("box_connect").destroy()

        # Add editor UI
        edit_pane = self.builder.get_object("edit_pane")
        self.edit_query = GtkSource.View(wrap_mode="word-char", monospace=True,
                                    show_line_numbers=True)
        edit_pane.add1(self.edit_query)
        edit_results = self.builder.get_object("edit_results")
        edit_pane.add2(edit_results)

        # lang_manager = GtkSource.LanguageManager()
        # lang = lang_manager.guess_language("a.sql", None)
        # self.edit_query = self.builder.get_object("edit_query")
        # buffer = self.edit_query.get_buffer()
        # buffer.set_language(lang)

        self.add(edit_pane)
        edit_pane.show_all()

        # Run test query
        self.test_query()

    def test_query(self):
        """Test the query UI with the SQLite DB"""
        self.edit_query.get_buffer().set_text("SELECT * FROM connections;")
        # TODO: Set buffer contents to sample query

        result = config.get_connections()
        edit_results = self.builder.get_object("edit_results")
        result_list = Gtk.ListStore(str, str, str, str, str)
        if result:
            for i, key in enumerate(result[0].keys()):
                text = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(key, text, text=i)
                column.set_resizable(True)
                edit_results.append_column(column)
        for row in result:
            result_list.append(row)

        edit_results.set_model(result_list)
        edit_results.show_all()

    def run_editor_query(self):
        """Run the query currently in the editor"""
        query = self.edit_query.get_buffer().get_text()
        result = config.cursor().exec(query).fetchall()
        # TODO: figure out how to dynamically create a Gtk.ListStore

    def btn_add_connection(self, button):
        """Show Add Connection modal on button click"""
        add_dialog = AddConnectionWindow(transient_for=self, modal=True,
                                         skip_taskbar_hint=True)
        add_dialog.present()

    @classmethod
    def on_destroy(cls, widget=None, *data):
        config.commit()

class Application(Gtk.Application):
    """Core application class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.phpizza.opensqlpro",
                         **kwargs)

        self.window = None

    def do_startup(self):
        """"Initialize application"""
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
        about_dialog.present()

    @classmethod
    def on_quit(cls, action, param):
        """Quit application, saving the config database"""
        # TODO: save application window state
        config.commit()
        cls.quit()


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
