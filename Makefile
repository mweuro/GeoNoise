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


.PHONY: convert_to_tensor
convert_to_tensor:
	echo $(REPO_ROOT)
	mkdir -p $(REPO_ROOT)/data_to_train
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/convert_to_tensor.py


.PHONY: train_eval
train_eval:
	echo $(REPO_ROOT)
	mkdir -p $(REPO_ROOT)/model
	mkdir -p $(REPO_ROOT)/model/val
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/train_eval.py


.PHONY: test
test:
	echo $(REPO_ROOT)
	mkdir -p $(REPO_ROOT)/model
	mkdir -p $(REPO_ROOT)/model/test
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT) python src/test.py