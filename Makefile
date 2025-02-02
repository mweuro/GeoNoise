REPO_ROOT=$(shell git rev-parse --show-toplevel)


.PHONY: load_data
load_data:
	echo $(REPO_ROOT)
	mkdir -p $(REPO_ROOT)/data
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/download_data.py
	PYTHONPATH=$(REPO_ROOT) python src/s2_grid.py
	PYTHONPATH=$(REPO_ROOT) python src/download_buildings_data.py


.PHONY: preprocess_data
preprocess_data:
	echo $(REPO_ROOT)
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/preprocessing.py


.PHONY: aggregate_data
aggregate_data:
	echo $(REPO_ROOT)
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/aggregation.py