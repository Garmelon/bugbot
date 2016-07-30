import sys
import time
import logging
import sqlite3
import threading

import bugbot


THREAD_LIMIT = 10
DB_NAME = "logs.db"
DB_SETUP = """
CREATE TABLE IF NOT EXISTS messages(
	id      STRING  NOT NULL,
	room    STRING  NOT NULL,
	time    INTEGER NOT NULL,
	session STRING  NOT NULL,
	name    STRING  NOT NULL,
	content STRING  NOT NULL,
	parent  STRING,
	PRIMARY KEY (id, room)
);

CREATE TABLE IF NOT EXISTS sessions(
	id         STRING PRIMARY KEY,
	user_id    STRING NOT NULL,
	is_staff   INTEGER,
	is_manager INTEGER
);

CREATE TABLE IF NOT EXISTS rooms(
	name     STRING PRIMARY KEY,
	password STRING
);
"""
HELP_TEXT = """
Usage: python3 main.py action[ parameters]

Actions:
    help[ action name]          -> Display help.
    list                        -> List rooms saved in the db.
    add roomname[ password]     -> Add a room to the db.
    remove roomname[ roomnames] -> Remove a room and all its messages from the db.
                                   WARNING: This action is irreversible!
    reset roomname[ roomnames]  -> Remove a room's messages, but not the room.
                                   This way, the room's log will be downloaded again
                                   the next time you update it.
                                   WARNING: This action is irreversible!
    update[ roomnames]          -> Update a room's log.
                                   If no room is specified, all logs will be updated.
    redownload[ roomnames]      -> Redownload a room's log
                                   If no room is specified, all logs will be redownloaded.
    readable[ roomnames]        -> Convert a room's log to a readable format.
                                   If no room is specified, all logs will be converted.
"""


def listrooms():
	"""
	List all rooms and passwords.
	"""
	
	with sqlite3.connect(DB_NAME) as db:
		rooms = db.execute("SELECT * FROM rooms")
		for room in rooms:
			if room[1] is not None:
				print("name: {:20} pw: {}".format(room[0], room[1]))
			else:
				print("name: {}".format(room[0]))


def loadrooms(names):
	"""
	Load rooms/passwords from db.
	"""
	
	rooms = {}
	
	if names:
		with sqlite3.connect(DB_NAME) as db:
			for name in names:
				pw = db.execute("SELECT password FROM rooms WHERE name=?", (name,)).fetchone()
				rooms[name] = pw[0] if pw else None
	else:
		with sqlite3.connect(DB_NAME) as db:
			r = db.execute("SELECT * FROM rooms")
			for room in r:
				rooms[room[0]] = room[1]
	
	return rooms


def addroom(room, pw=None):
	"""
	Add a room and pw to the db.
	"""
	
	with sqlite3.connect(DB_NAME) as db:
		db.execute("INSERT OR REPLACE INTO rooms VALUES(?,?)", (room, pw))
		db.commit()


def removerooms(rooms):
	"""
	Remove rooms from the db.
	"""
	
	resetrooms(rooms)
	
	with sqlite3.connect(DB_NAME) as db:
		for room in rooms:
			db.execute("DELETE FROM rooms WHERE name=?", (room,))
			db.commit()


def resetrooms(rooms):
	"""
	Remove all messages of the rooms from the db.
	"""
	
	with sqlite3.connect(DB_NAME) as db:
		for room in rooms:
			db.execute("DELETE FROM messages WHERE room=?", (room,))
			db.commit()


def updaterooms(rooms):
	"""
	Update rooms' logs.
	"""
	
	for room in rooms:
		while not threading.active_count() < THREAD_LIMIT:
			time.sleep(1)
		bugbot.download.Downloader(room, DB_NAME, password=rooms[room]).launch()
		print("Started download: {}".format(room))
	
	print("Started all downloads")


def readable(rooms):
	print("This action is currently not available.")


def main(action, *argv):
	# initialize logging for all other modules
	logging.basicConfig(level=logging.INFO,
	                    format="[%(levelname)s] (%(threadName)-20s) %(message)s")
	
	# make sure the tables are set up correctly
	with sqlite3.connect(DB_NAME) as db:
		db.executescript(DB_SETUP)
		db.commit()
	
	if action == "help":
		print(HELP_TEXT)
	
	elif action == "list":
		listrooms()
	
	elif action == "add":
		if len(argv) == 1:
			addroom(argv[0])
		elif len(argv) == 2:
			addroom(argv[0], pw=argv[1])
		else:
			print("Usage: addroom roomname[ password]")
	
	elif action == "remove":
		removerooms(argv)
	
	elif action == "reset":
		resetrooms(argv)
	
	else:
		rooms = loadrooms(argv)
		
		if action == "update":
			updaterooms(rooms)
		
		elif action == "redownload":
			resetrooms(rooms)
			updaterooms(rooms)
		
		elif action == "readable":
			readable(rooms)
		
		else:
			print(HELP_TEXT)

if __name__ == "__main__":
	main(*sys.argv[1:])
	
	print("Done")
