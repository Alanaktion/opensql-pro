"""
OpenSQL Pro
A powerfully simple database client
"""
import sys
import gi

import pymysql.cursors
import pymysql

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
        self.builder.add_from_file('ui/app-window.glade')
        self.builder.connect_signals(self)

        header_bar = self.builder.get_object('header_bar')
        self.set_titlebar(header_bar)

        # Display connection list
        box_connect = self.builder.get_object('box_connect')
        connections = config.get_connections()

        for row in connections:
            self.add_connection_btn(row)

        self.conn_separator = None
        if connections:
            self.conn_separator = Gtk.Separator(valign='center')
            box_connect.pack_end(self.conn_separator, True, True, 0)

        self.conn_add_button = self.builder.get_object('btn_add_connection')
        box_connect.pack_end(self.conn_add_button, True, True, 0)

        self.add(box_connect)

        self.set_icon_name('office-database')
        self.show_all()

        self.editor = None
        self.db_connection = None

        self.connect('delete-event', self.on_destroy)

    def add_connection_btn(self, data, show=False):
        """Add button for saved connection"""
        box_connect = self.builder.get_object('box_connect')
        button = Gtk.Button(label=data[1])
        button.connect('clicked', self.btn_connect_saved, data[0])
        box_connect.pack_start(button, True, True, 0)
        if show:
            # TODO: Move separator and add button back to bottom
            box_connect.show_all()

    def btn_connect_saved(self, button, data):
        """Connect to saved server on button click"""

        # Connect to server
        try:
            conndata = config.get_connection(data)
            self.db_connection = pymysql.connect(host=conndata[2],
                                                 user=conndata[4],
                                                 password=conndata[5],
                                                 charset='utf8mb4',
                                                 cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.Error as err:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "Error connecting to server")
            dialog.format_secondary_text(err.__str__())
            dialog.run()
            dialog.destroy()
            return

        # Remove connection UI
        self.builder.get_object('box_connect').destroy()

        # Add editor UI
        self.editor = GtkSource.View(wrap_mode='word-char', monospace=True,
                                     show_line_numbers=True)
        editor_scroll = self.builder.get_object('editor_scroll')
        editor_scroll.add(self.editor)

        lang_manager = GtkSource.LanguageManager()
        lang = lang_manager.guess_language(None, 'application/sql')
        buffer = self.editor.get_buffer()
        buffer.set_language(lang)

        edit_pane = self.builder.get_object('edit_pane')
        self.add(edit_pane)
        edit_pane.show_all()

        # Bind run button
        btn_run = self.builder.get_object('btn_run')
        btn_run.set_sensitive(True)
        btn_run.connect('clicked', self.btn_run)

    def run_editor_query(self):
        """Run the query currently in the editor"""
        buffer = self.editor.get_buffer()
        sel_range = buffer.get_selection_bounds()
        if not sel_range:
            sel_range = (buffer.get_start_iter(), buffer.get_end_iter())
        query = buffer.get_text(*sel_range, False)

        cursor = self.db_connection.cursor()
        try:
            cursor.execute(query)
        except pymysql.err.Error as err:
            self.show_message(err)
        else:
            result = cursor.fetchall()
            self.show_result(result, cursor.description)

    # @staticmethod
    # def type_id_to_type(type_id):
    #     """Return a type based on PyMySQL type_id value"""
    #     if type_id <= pymysql.constants.FIELD_TYPE.DOUBLE:
    #         return float
    #     return None

    def show_result(self, result, meta):
        """Show a result set in a TreeView"""
        cols = []

        results_tree = self.builder.get_object('results_tree')

        for i, col in enumerate(meta):
            # TODO: Get correct column types on empty result set
            cols = cols + [type(result[0][col[0]])]
            control = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col[0].replace('_', '__'), control,
                                        text=i)
            column.set_resizable(True)
            results_tree.append_column(column)

        result_list = Gtk.ListStore(*cols)
        for row in result:
            result_list.append(row.values())

        results_tree.set_model(result_list)
        results_tree.show_all()

    def show_message(self, message):
        """Show message result from query"""
        print(message)

    def btn_run(self, button):
        """Run query on button click"""
        self.run_editor_query()

    def btn_add_connection(self, button):
        """Show Add Connection modal on button click"""
        add_dialog = AddConnectionWindow(transient_for=self, modal=True,
                                         skip_taskbar_hint=True)
        add_dialog.present()

    def on_destroy(self, widget=None, *data):
        """Write config DB and close MySQL connections on quit"""
        # TODO: save window state
        config.commit()
        if self.db_connection:
            self.db_connection.close()

class Application(Gtk.Application):
    """Core application class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id='com.phpizza.opensqlpro',
                         **kwargs)

        self.window = None

    def do_startup(self):
        """'Initialize application"""
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new('about', None)
        action.connect('activate', self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder()
        builder.add_from_file('ui/app-menu.glade')
        self.set_app_menu(builder.get_object('app-menu'))

    def do_activate(self):
        """Create/raise main window on activate"""
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppWindow(application=self, title='OpenSQL Pro')

        self.window.present()

    def on_about(self, action, param):
        """Show About dialog"""
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_program_name('OpenSQL Pro')
        about_dialog.set_version('0.0.1')
        about_dialog.set_copyright('© Alan Hardman')
        about_dialog.set_comments('A powerfully simple database client')
        about_dialog.set_website('https://git.phpizza.com/alan/opensql-pro')
        about_dialog.set_logo_icon_name('office-database')
        about_dialog.set_authors(['Alan Hardman'])
        about_dialog.connect('response', self.on_about_close)
        about_dialog.present()

    def on_about_close(self, dialog, response):
        """Close About dialog on button click"""
        dialog.destroy()

    def on_quit(self, action, param):
        """Close main window, gracefully exiting"""
        self.window.close()


class AddConnectionWindow(Gtk.Window):
    """Add connection modal window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui/add-dialog.glade')
        self.builder.connect_signals(self)

        header_bar = self.builder.get_object('header_bar')
        self.set_titlebar(header_bar)

        input_grid = self.builder.get_object('input_grid')
        self.add(input_grid)

    def btn_cancel(self, button):
        """Cancel adding a connection from button click"""
        self.close()

    def btn_save(self, button):
        """Save new connection from button click"""
        name = self.builder.get_object('text_name').get_text()
        host = self.builder.get_object('text_host').get_text()
        port = self.builder.get_object('text_port').get_text()
        user = self.builder.get_object('text_user').get_text()
        password = self.builder.get_object('text_pass').get_text()
        cid = config.add_connection(name, host, port, user, password)

        data = config.get_connection(cid)
        app.window.add_connection_btn(data, True)

        self.close()


if __name__ == '__main__':
    config.init()
    app = Application()
    app.run()
