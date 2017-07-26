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
brew install python3 gtk+3 gtksourceview3
brew install pygobject3 --with-python3
pip3 install pymysql appdirs
python3 .
```

### Ubuntu 17.10

Since switching to Gnome, Ubuntu is much easier to support out of the box now!

```bash
sudo apt install python3-pip
sudo -H pip3 install pymysql appdirs
python3 .
```

### Windows

In theory, it is possible to run this project on Windows, but getting PyGObject to work properly isn't worth the trouble. Try SQLyog instead!
