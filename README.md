# OpenSQL Pro

## Setup

OpenSQL Pro is built on Python 3 with PyGObject. It requires Gtk 3.20+ with GtkSourceView to be installed.

### Arch Linux

```bash
sudo pacman -S python pygobject-devel gtk3
sudo -H pip install pymysql appdirs
mkdir -p ~/.schemas
cp data/* ~/.schemas/
glib-compile-schemas ~/.schemas/
python .
```

### macOS

```bash
brew install python3 gtk+3 gtksourceview3
brew install pygobject3 --with-python3
pip3 install pymysql appdirs
python3 .
```

### Ubuntu

```bash
sudo apt install python3-pip
sudo -H pip3 install pymysql appdirs
mkdir -p ~/.schemas
cp data/* ~/.schemas/
glib-compile-schemas ~/.schemas/
python3 .
```

Ubuntu 16.04 works fine, but has a display issue where the source view starts completely collapsed. Ubuntu 17.10 daily builds do not have this issue.

### Windows

In theory, it is possible to run this project on Windows, but getting PyGObject to work properly isn't worth the trouble. Try SQLyog instead!
