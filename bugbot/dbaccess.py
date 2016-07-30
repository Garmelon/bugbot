import sqlite3

import yaboli

class DBAccess():
	"""
	Takes care of opening and closing the connection to the db.
	"""
	
	def __init__(self, db):
		"""
		db - path to the db, or ":memory:"
		"""
		
		self._con = sqlite3.connect(db)
		self._con.row_factory = sqlite3.Row
	
	def execute(self, *args, **kwargs):
		return self._con.execute(*args, **kwargs)
	
	def close(self):
		self._con.close()
	
	def __del__(self):
		self.close()

class Log(DBAccess):
	"""
	More abstract way to access a room's messages in the db.
	"""
	
	def __init__(self, db, room):
		"""
		db   - path to the db, or ":memory:"
		room - name of the room
		"""
		
		super().__init__(self, db)
		self._room = room
	
	def get_session(self, sid):
		"""
		get_session(session_id) -> session
		
		Returns the session with that id.
		"""
		
		cur = self.execute("SELECT * FROM sessions WHERE id=?", (mid, self._room))
		result = cur.fetchone()
		if result:
			return yaboli.Message(
				# TODO: <Arguments go here>
			)
	
	def get_message(self, mid):
		"""
		get_message(message_id) -> message
		
		Returns the message with that id.
		"""
		
		cur = self.execute("SELECT * FROM messages WHERE id=? AND room=?", (mid, self._room))
		result = cur.fetchone()
		if result:
			return yaboli.Message(
				# TODO: <Arguments go here>
			)

class Rooms(DBAccess):
	pass