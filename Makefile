
DATA_DIR ?= "test"

test:
	./pyphori.py -d ${DATA_DIR} --database pyphori.db
	

export:
	./pyphori.py -e database.txt --database pyphori.db
