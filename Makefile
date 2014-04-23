
build:
	ninja -v

targets:
	./make_targets.py src/*.cpp

clean:
	ninja -v -t clean

.PHONY: build targets clean
