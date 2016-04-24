import sqlite3

class Log():
	"""
	Connect to the db and store/retrieve message and session information.
	"""
	
	def __init__(self, name, room):
		"""
		name - name of the db
		room - name of the room
		"""
		self.name = name
		self.room = room
	
	def get_newest(self):
		"""
		get_newest() -> message_id
		
		Returns id of newest message found.
		Returns None if no message was found.
		"""
		
		with sqlite3.connect(self.name) as db:
			message = db.execute(
				"SELECT id FROM messages WHERE room=? ORDER BY id DESC LIMIT 1",
				(self.room,)
			)
		
		result = message.fetchone()
		return result[0] if result
	
	def get_top_level(self):
		"""
		get_top_level() -> list of messages
		
		Returns a full list of top-level messages' ids.
		"""
		
		with sqlite3.connect(self.name) as db:
			message = db.execute(
				"SELECT id FROM messages WHERE parent ISNULL AND room=?",
				(self.room,)
			)
		
		result = message.fetchall()
		return [entry[0] for entry in result] if result
	
	def get_message(self, mid):
		"""
		get_message(message_id) -> message
		
		Returns message with that id.
		"""
		
		with sqlite3.connect(self.name) as db:
			message = db.execute(
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
		
		with sqlite3.connect(self.name) as db:
			message = db.execute(
				"SELECT parent FROM messages WHERE id=? AND room=?",
				(mid, self.room)
			)
		
		result = message.fetchone()
		return result[0] if result
	
	def get_children(self, mid):
		"""
		get_children(message_id) -> list of message_ids
		
		Returns a list of the message's childrens' ids.
		"""
		
		with sqlite3.connect(self.name) as db:
			message = db.execute(
				"SELECT id FROM messages WHERE parent=? AND room=?",
				(mid, self.room)
			)
		
		result = message.fetchall()
		return [entry[0] for entry in result] if result
	
	def add_message(self, msg):
		"""
		add_message(message) -> None
		
		Add a message to the db.
		"""
		
		with sqlite3.connect(self.name) as db:
			# insert or update message
			db.execute(
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
			db.execute(
				"INSERT OR REPLACE INTO sessions VALUES(?,?,?,?)",
				(
					msg["sender"]["session_id"],
					msg["sender"]["id"],
					1 if "is_staff" in msg["sender"] and msg["sender"]["is_staff"] else None,
					1 if "is_manager" in msg["sender"] and msg["sender"]["is_manager"] else None
				)
			)
