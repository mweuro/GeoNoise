REPO_ROOT=$(shell git rev-parse --show-toplevel)


.PHONY: load_data
load_data:
	echo $(REPO_ROOT)
	mkdir -p $(REPO_ROOT)/data
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/download_data.py