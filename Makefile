SOURCE="./maze.py"
TARGET="/usr/bin/maze"


all: install

install:
	install -m 755 $(SOURCE) $(TARGET)

uninstall:
	rm $(TARGET)
