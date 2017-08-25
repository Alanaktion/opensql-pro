"""
Helper module for working with PyMySQL data sets

Handles converting PyMySQL objects to Gtk-compatible structures and types
"""
import datetime
import pymysql

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def int_to_type(type_id):
    """Convert PyMySQL field type to GType"""
    # TODO: Verify how NULL type actually appears and handle it better
    type_map = {
        pymysql.constants.FIELD_TYPE.TINY: int,
        pymysql.constants.FIELD_TYPE.SHORT: int,
        pymysql.constants.FIELD_TYPE.LONG: int,
        pymysql.constants.FIELD_TYPE.INT24: int,
        pymysql.constants.FIELD_TYPE.YEAR: int,
        pymysql.constants.FIELD_TYPE.DECIMAL: float,
        pymysql.constants.FIELD_TYPE.FLOAT: float,
        pymysql.constants.FIELD_TYPE.DOUBLE: float,
        pymysql.constants.FIELD_TYPE.LONGLONG: float,
        pymysql.constants.FIELD_TYPE.NEWDECIMAL: float,
        pymysql.constants.FIELD_TYPE.NULL: None,
        pymysql.constants.FIELD_TYPE.VARCHAR: str,
        pymysql.constants.FIELD_TYPE.BIT: str,
        pymysql.constants.FIELD_TYPE.JSON: str,
        pymysql.constants.FIELD_TYPE.ENUM: str,
        pymysql.constants.FIELD_TYPE.SET: str,
        pymysql.constants.FIELD_TYPE.TINY_BLOB: str,
        pymysql.constants.FIELD_TYPE.MEDIUM_BLOB: str,
        pymysql.constants.FIELD_TYPE.LONG_BLOB: str,
        pymysql.constants.FIELD_TYPE.BLOB: str,
        pymysql.constants.FIELD_TYPE.VAR_STRING: str,
        pymysql.constants.FIELD_TYPE.STRING: str,
        pymysql.constants.FIELD_TYPE.GEOMETRY: str,
        pymysql.constants.FIELD_TYPE.TIMESTAMP: str,
        pymysql.constants.FIELD_TYPE.DATE: str,
        pymysql.constants.FIELD_TYPE.TIME: str,
        pymysql.constants.FIELD_TYPE.DATETIME: str,
        pymysql.constants.FIELD_TYPE.NEWDATE: str,
    }
    return type_map.get(type_id, str)

def value_to_renderable(val):
    """Convert a PyMySQL result value to a renderable format"""
    if isinstance(val, datetime.datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, datetime.date):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, bytes):
        return '<BINARY>'
    return val

def result_to_liststore(result, description, treeview=None, editable=False):
    """Convert PyMySQL result to GtkListStore"""
    cols = []
    for i, col in enumerate(description):
        cols = cols + [int_to_type(col[1])]
        if treeview:
            control = Gtk.CellRendererText(editable=editable, ellipsize='end',
                                           single_paragraph_mode=True)
            label = col[0].replace('_', '__')
            column = Gtk.TreeViewColumn(label, control, text=i)
            column.set_resizable(True)
            treeview.append_column(column)

    result_list = Gtk.ListStore(*cols)
    for row in result:
        rowfinal = []
        for val in row.values():
            displayval = value_to_renderable(val)
            rowfinal.append(displayval)
        result_list.append(rowfinal)

    return result_list

def escape_identifier(identifier):
    """Escape MySQL identifier"""
    return "`%s`" % identifier.replace('`', '``')
