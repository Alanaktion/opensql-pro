"""
Helper module for common UI tasks
"""

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def add_spinner(parent_widget, empty=True):
    """Add a centered spinner to a widget"""

    if empty and parent_widget.get_child():
        parent_widget.remove(parent_widget.get_child())

    alignment = Gtk.Alignment(halign='center', valign='center')
    spinner = Gtk.Spinner()
    spinner.start()
    alignment.add(spinner)
    parent_widget.add(alignment)
    parent_widget.show_all()
