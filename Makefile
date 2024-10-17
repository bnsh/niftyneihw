PYTHON=$(sort $(shell find . -type f -name '*.py' -print))
PYLINT3=$(join $(dir $(PYTHON)), $(addprefix ., $(notdir $(PYTHON:py=pylint3))))

all: pylint

pylint: $(PYLINT3)

.%.pylint3: %.py
	python3 -m pylint -r n $(^)
	@>$(@)
