SOURCE="./src/maze"
TARGET="/usr/bin/maze"


all: install

install:
	install -m 755 $(SOURCE) $(TARGET)

uninstall:
	rm $(TARGET)
