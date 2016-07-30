import logging
import sqlite3

class Log():
	"""
	Connect to the db and store/retrieve message and session information.
	"""
	
	def __init__(self, name, room):
		"""
		name - name of the db
		room - name of the room
		
		This also opens a connection to the db - make sure to close that later!
		"""
		self.name = name
		self.room = room
	
	def open(self):
		"""
		open() -> None
		
		Open the connection to the db.
		"""
		
		self.con = sqlite3.connect(self.name)
	
	def close(self):
		"""
		close() -> None
		
		Close the connection to the db.
		"""
		self.con.commit()
		self.con.close()
	
	def get_newest(self):
		"""
		get_newest() -> message_id
		
		Returns id of newest message found.
		Returns None if no message was found.
		"""
		
		message = self.con.execute(
			"SELECT id FROM messages WHERE room=? ORDER BY id DESC LIMIT 1",
			(self.room,)
		)
		
		result = message.fetchone()
		return result[0] if result else None
	
	def get_top_level(self):
		"""
		get_top_level() -> list of messages
		
		Returns a full list of top-level messages' ids.
		"""
		
		message = self.con.execute(
			"SELECT id FROM messages WHERE parent ISNULL AND room=?",
			(self.room,)
		)
		
		result = message.fetchall()
		return [entry[0] for entry in result] if result else None
	
	def get_message(self, mid):
		"""
		get_message(message_id) -> message
		
		Returns message with that id.
		"""
		
		message = self.con.execute(
			"SELECT * FROM messages WHERE id=? AND room=?",
			(mid, self.room)
		)
		
		result = message.fetchone()
		return {
			"id":      result[0],
			"room":    result[1],
			"time":    result[2],
			"session": result[3],
			"name":    result[4],
			"content": result[5],
			"parent":  result[6]
		}
	
	def get_parent(self, mid):
		"""
		get_parent(message_id) -> message_id
		
		Returns the message's parent's id.
		"""
		
		message = self.con.execute(
			"SELECT parent FROM messages WHERE id=? AND room=?",
			(mid, self.room)
		)
		
		result = message.fetchone()
		return result[0] if result else None
	
	def get_children(self, mid):
		"""
		get_children(message_id) -> list of message_ids
		
		Returns a list of the message's childrens' ids.
		"""
		
		message = self.con.execute(
			"SELECT id FROM messages WHERE parent=? AND room=?",
			(mid, self.room)
		)
		
		result = message.fetchall()
		return [entry[0] for entry in result] if result else None
	
	def add_message(self, msg):
		"""
		add_message(message) -> None
		
		Add a message to the db.
		"""
		
		# insert or update message
		self.con.execute(
			"INSERT OR REPLACE INTO messages VALUES(?,?,?,?,?,?,?)",
			(
				msg["id"],
				self.room,
				msg["time"],
				msg["sender"]["session_id"],
				msg["sender"]["name"],
				msg["content"],
				msg["parent"] if "parent" in msg else None
			)
		)
		
		# insert or update session
		self.con.execute(
			"INSERT OR REPLACE INTO sessions VALUES(?,?,?,?)",
			(
				msg["sender"]["session_id"],
				msg["sender"]["id"],
				1 if "is_staff" in msg["sender"] and msg["sender"]["is_staff"] else None,
				1 if "is_manager" in msg["sender"] and msg["sender"]["is_manager"] else None
			)
		)
	
	def commit(self):
		"""
		commit() -> None
		
		Write all the changes to the db.
		"""
		
		self.con.commit()
