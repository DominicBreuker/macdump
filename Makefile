
.PHONY: build-executable
build-executable:
	pyinstaller --onefile --name macdump --strip --console --key=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1) src/macdump/__main__.py

.PHONY: build-script
build-script:
	stickytape src/macdump/__main__.py --add-python-path src --output-file macdump.py
