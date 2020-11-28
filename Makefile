
DATA_DIR ?= "test"

TRANSFER_DIR ?= "test/upload"

test:
	./pyphori.py -d ${DATA_DIR} -t ${TRANSFER_DIR} --database pyphori.db
	

export:
	./pyphori.py -e database.txt --database pyphori.db

script:
	./pyphori.py -s script.sh --database pyphori.db
	chmod +x script.sh
	
	