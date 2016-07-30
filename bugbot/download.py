import logging

from . import log
from . import connection

class Downloader():
	"""
	Update or redownload a room's log.
	"""
	
	def __init__(self, room, db_name, password=None):
		"""
		room     - name of the room to download the log of
		db_name  - name of the db to download the log to
		password - password of said room, optional
		"""
		
		self.password = password
		self.con = connection.Connection(room)
		self.log = log.Log(db_name, room)
		
		self.downloading = True # still downloading new messages
		self.truncated = 0 # messages still truncated
		
		self.con.add_callback("ping-event",        self._handle_ping_event       )
		self.con.add_callback("bounce-event",      self._handle_bounce_event     )
		self.con.add_callback("auth-reply",        self._handle_auth_reply       )
		self.con.add_callback("disconnect-event",  self._handle_disconnect_event )
		self.con.add_callback("snapshot-event",    self._handle_snapshot_event   )
		self.con.add_callback("get-message-reply", self._handle_get_message_reply)
		self.con.add_callback("log-reply",         self._handle_log_reply        )
	
	def _handle_ping_event(self, data):
		"""
		_handle_ping_event(data) -> None
		
		Pong!
		"""
		
		self.con.send_packet("ping-reply", time=data["time"])
		logging.debug("Ping-reply on {}, expected next on {}.".format(data["time"], data["next"]))
	
	def _handle_bounce_event(self, data):
		"""
		_handle_bounce_event(data) -> None
		
		Authenticate if possible, otherwise give up and stop.
		"""
		
		if self.password:
			self.con.send_packet("auth", type="passcode", passcode=self.password)
			logging.info("Bounce! Authenticating with {}".format(self.password))
		else:
			self.log.close()
			self.con.stop()
			logging.warn("Bounce! Could not authenticate :/")
	
	def _handle_auth_reply(self, data):
		"""
		_handle_auth_reply(data) -> None
		
		Disconnect if authentication unsucessful.
		"""
		
		if data["success"]:
			logging.debug("Successfully authenticated")
		else:
			logging.warn("Error authenticating: '{}'".format(data["reason"]))
			self.log.close()
			self.con.stop()
	
	def _handle_disconnect_event(self, data):
		"""
		_handle_disconnect_event(data) -> None
		
		Immediately disconnect.
		"""
		
		logging.warn("Disconnecting: '{}'".format(data["reason"]))
		self.log.close()
		self.con.stop()
	
	def _handle_snapshot_event(self, data):
		"""
		_handle_snapshot_event(data) -> None
		
		Save messages and request further messages.
		"""
		
		self.add_messages(data["log"])
	
	def _handle_get_message_reply(self, data):
		"""
		_handle_get_message_reply(data) -> None
		
		Replace truncated message by untruncated message.
		"""
		
		logging.debug("Untruncate! {}".format(data["id"]))
		self.log.add_message(data)
		self.truncated -= 1
		
		if self.truncated <= 0 and not self.downloading:
			logging.debug("Last untruncated message received - stopping now")
			self.log.close()
			self.con.stop()
		
	def _handle_log_reply(self, data):
		"""
		_handle_log_reply(data) -> None
		
		Save messages and request further messages.
		"""
		
		self.add_messages(data["log"])
	
	def add_messages(self, msgs):
		"""
		add_mesages(messages) -> None
		
		Save messages to the db and request further messages.
		"""
		
		logging.info("Processing messages")
		
		if len(msgs) == 0:
			logging.info("End of log - empty")
			self.log.close()
			self.con.stop()
			return
		
		for msg in msgs[::-1]:
			logging.debug("Testing '{}' from {}".format(msg["id"], msg["sender"]["name"]))
			
			if msg["id"] <= self.newmsg:
				logging.info("End of log - too old")
				self.log.close()
				self.con.stop()
				return
			
			else:
				logging.debug("Adding message: {}".format(msg["id"]))
				self.log.add_message(msg)
				logging.info("Untruncating message: {}".format(msg["id"]))
				self.con.send_packet("get-message", id=msg["id"])
		
		else:
			self.log.commit()
			logging.info("Requesting more messages")
			self.con.send_packet("log", n=1000, before=msgs[0]["id"])
	
	def launch(self):
		"""
		launch() -> None
		
		Start the download in a separate thread.
		"""
		
		self.con.launch(self._on_launch)
	
	def _on_launch(self):
		"""
		_on_launch() -> None
		
		Gets called in the new thread.
		"""
		
		self.log.open()
		self.newmsg = self.log.get_newest() or ""
