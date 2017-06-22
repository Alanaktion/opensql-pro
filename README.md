# OpenSQL Pro

## Setup

OpenSQL Pro is built on Python 3 with PyGObject. It requires Gtk 3.20+ with GtkSourceView to be installed.

### Arch Linux

```bash
sudo pacman -S python pygobject-devel gtk3
sudo -H pip install pymysql appdirs
python .
```

### macOS

```bash
brew install python3 gtk+3 gtksourceview
brew install pygobject3 --with-python3
pip3 install pymysql appdirs
python3 .
```
