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
from gi.repository import Gio, Gtk, Gdk, GtkSource, Pango

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

        self.connect('key_press_event', self.on_key_press)
        self.connect('delete-event', self.on_destroy)

    def on_key_press(self, widget, event, user_data=None):
        """Handle key press"""
        key = Gdk.keyval_name(event.keyval)
        if key == 'F5':
            self.run_editor_query()
            return True
        if key == 'F9':
            self.run_editor_query()
            return True
        return False

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
                                       'Error connecting to server')
            dialog.format_secondary_text(err.__str__())
            dialog.set_title('Connection Error')
            dialog.run()
            dialog.destroy()
            return

        # Set subtitle
        header_bar = self.builder.get_object('header_bar')
        header_bar.set_subtitle(conndata[4] + '@' + conndata[2])

        # Remove connection UI
        self.builder.get_object('box_connect').destroy()

        # Update database list
        combo_db = self.builder.get_object('combo_db')
        cursor = self.db_connection.cursor()
        cursor.execute('SHOW DATABASES')
        db_result = cursor.fetchall()
        db_store = Gtk.ListStore(str)
        for row in db_result:
            db_store.append(row.values())
        combo_db.set_model(db_store)
        combo_db.connect('changed', self.on_db_change)
        combo_db.set_sensitive(True)

        # TODO: Restore last used database for each connection

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

        results_scroll = self.builder.get_object('results_scroll')
        if results_scroll.get_child():
            results_scroll.remove(results_scroll.get_child())

        results_tree = Gtk.TreeView(enable_grid_lines=True, enable_search=False)
        fontdesc = Pango.FontDescription("monospace 9")
        results_tree.modify_font(fontdesc)

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
            rowfinal = []
            for val in row.values():
                if isinstance(val, str):
                    # Truncate strings to 60 chars, one line max
                    oneline = val.replace('\r', '').replace('\n', '¶')
                    if len(oneline) > 59:
                        rowfinal.append(oneline[:59] + '…')
                    else:
                        rowfinal.append(oneline)
                else:
                    rowfinal.append(val)
            result_list.append(rowfinal)

        results_tree.set_model(result_list)
        results_scroll.add(results_tree)
        results_scroll.show_all()

    def show_message(self, message):
        """Show message result from query"""
        print(message)

    def btn_run(self, button):
        """Run query on button click"""
        self.run_editor_query()

    def on_db_change(self, combo):
        """Select database from combo box"""
        tree_iter = combo.get_active_iter()
        if tree_iter == None:
            return

        # Select new database
        model = combo.get_model()
        db = model[tree_iter][0]
        self.db_connection.select_db(db)

        # Update table list
        cursor = self.db_connection.cursor()
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()

        table_scroll = self.builder.get_object('table_scroll')
        if table_scroll.get_child():
            table_scroll.remove(table_scroll.get_child())

        table_tree = Gtk.TreeView(enable_grid_lines=True, enable_search=False)
        fontdesc = Pango.FontDescription("monospace 9")
        table_tree.modify_font(fontdesc)

        control = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Tables', control, text=0)
        table_tree.append_column(column)
        table_list = Gtk.ListStore(str)
        for row in tables:
            table_list.append(row.values())

        table_tree.set_model(table_list)
        table_scroll.add(table_tree)
        table_scroll.show_all()

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

        action = Gio.SimpleAction.new('preferences', None)
        action.connect('activate', self.on_preferences)
        self.add_action(action)

        action = Gio.SimpleAction.new('quit', None)
        action.connect('activate', self.on_quit)
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

            # Bind F9 to Run
            # action = Gio.SimpleAction.new('run', None)
            # action.connect('activate', self.window.run_editor_query)
            # self.set_accels_for_action('run', ['F9'])
            # self.add_action(action)

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

    def on_preferences(self, action, param):
        """Show Preferences dialog"""
        dialog = PreferencesWindow(transient_for=self.window, modal=True,
                                   skip_taskbar_hint=True)
        dialog.present()

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

        self.connect('key_press_event', self.on_key_press)

    def on_key_press(self, widget, event, user_data=None):
        """Handle key press"""
        key = Gdk.keyval_name(event.keyval)
        if key == 'Escape':
            self.close()
            return True
        if key == 'Enter':
            self.save_connection()
            return True
        return False

    def save_connection(self):
        """Save connection and close window"""
        name = self.builder.get_object('text_name').get_text()
        host = self.builder.get_object('text_host').get_text()
        port = self.builder.get_object('text_port').get_text()
        user = self.builder.get_object('text_user').get_text()
        password = self.builder.get_object('text_pass').get_text()
        cid = config.add_connection(name, host, port, user, password)

        data = config.get_connection(cid)
        app.window.add_connection_btn(data, True)

        self.close()

    def btn_cancel(self, button):
        """Cancel adding a connection from button click"""
        self.close()

    def btn_save(self, button):
        """Save new connection from button click"""
        self.save_connection()


class PreferencesWindow(Gtk.Window):
    """Preferences modal window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui/preferences-dialog.glade')
        self.builder.connect_signals(self)

        header_bar = self.builder.get_object('header_bar')
        self.set_titlebar(header_bar)

        input_grid = self.builder.get_object('input_grid')
        self.add(input_grid)

        self.connect('key_press_event', self.on_key_press)

    def on_key_press(self, widget, event, user_data=None):
        """Handle key press"""
        key = Gdk.keyval_name(event.keyval)
        if key == 'Escape':
            self.close()
            return True
        if key == 'Enter':
            self.save_connection()
            return True
        return False

    def btn_cancel(self, button):
        """Cancel adding a connection from button click"""
        self.close()

    def btn_save(self, button):
        """Save new connection from button click"""

        # TODO: save and apply new settings

        self.close()


if __name__ == '__main__':
    config.init()
    app = Application()
    app.run()
