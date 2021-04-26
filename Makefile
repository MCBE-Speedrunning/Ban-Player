INSTALL := /usr/local/bin
PY      := python3.9

src    := pban.py
target := pban

all:

.PHONY: clean format install uninstall test
clean:
	rm -rf __pycache__/

format:
	$(PY) -m isort $(src)
	$(PY) -m black $(src)
	@unexpand -t 4 --first-only $(src) >temp
	@mv temp $(src)
	@chmod +x $(src)

install:
	cp $(src) $(INSTALL)/$(target)
	chmod +x $(INSTALL)/$(target)

uninstall:
	rm -f $(INSTALL)/$(target)

test:
	$(PY) -m doctest $(src)
