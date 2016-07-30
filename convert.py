import sys
import json
import sqlite3

def main(filename, roomname):
	with open(filename) as f:
		log = json.load(f)
	
	with sqlite3.connect("logs.db") as db:
		for msg in log:
			print("Adding {}".format(msg))
			
			# insert or update message
			db.execute(
				"INSERT OR REPLACE INTO messages VALUES(?,?,?,?,?,?,?)",
				(
					msg["id"],
					roomname,
					msg["time"],
					msg["sender"]["session_id"],
					msg["sender"]["name"],
					msg["content"],
					msg["parent"] if "parent" in msg else None
				)
			)
			
			# insert or update session
			db.execute(
				"INSERT OR REPLACE INTO sessions VALUES(?,?,?,?)",
				(
					msg["sender"]["session_id"],
					msg["sender"]["id"],
					1 if "is_staff" in msg["sender"] and msg["sender"]["is_staff"] else None,
					1 if "is_manager" in msg["sender"] and msg["sender"]["is_manager"] else None
				)
			)

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])