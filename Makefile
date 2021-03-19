PY := python3.9
target := pban

all:

.PHONY: clean test install uninstall
clean:
	rm -rf __pycache__/

install:
	cp $(target).py /usr/bin/pban
	chmod +x /usr/bin/pban

uninstall:
	rm -f /usr/bin/$(target)

test:
	$(PY) -m doctest pban.py