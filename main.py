import sqlite3

db_name = "bugbot.db"
db_setup = """
CREATE TABLE IF NOT EXISTS messages(
	id      STRING  PRIMARY KEY,
	room    STRING  NOT NULL,
	time    INTEGER NOT NULL,
	session STRING  NOT NULL,
	name    STRING  NOT NULL,
	content STRING  NOT NULL,
	parent  STRING
);

CREATE TABLE IF NOT EXISTS sessions(
	id         STRING PRIMARY KEY,
	user_id    STRING NOT NULL,
	is_staff   INTEGER,
	is_manager INTEGER
);

CREATE TABLE IF NOT EXISTS rooms(
	name STRING PRIMARY KEY
);
"""

def main():
	# make sure the tables are set up correctly
	with sqlite3.connect(db_name) as db:
		db.executescript(db_setup)
		db.commit()

if __name__ == "__main__":
	main()