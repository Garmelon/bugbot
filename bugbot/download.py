import tempfile

import connection

class Downloader():
	"""
	Update or redownload a room's log.
	"""
	
	def __init__(self, room, logfile, password=None):
		"""
		room     - name of the room to download the logs of
		logfile  - path to the file to save the log in
		password - password of said room, optional
		"""
		
		pass
	
	def _handle_ping_event(self, data):
		"""
		_handle_ping_event(data) -> None
		
		Pong!
		"""
		
		pass
	
	def _handle_bounce_event(self, data):
		"""
		_handle_bounce_event(data) -> None
		
		Authenticate if possible, otherwise give up and stop.
		"""
		
		pass
	
	def _handle_auth_reply(self, data):
		"""
		_handle_auth_reply(data) -> None
		
		Disconnect if authentication unsucessful.
		"""
		
		pass
	
	def _handle_disconnect_event(self, data):
		"""
		_handle_disconnect_event(data) -> None
		
		Immediately disconnect.
		"""
		
		pass
	
	def _handle_snapshot_event(self, data):
		"""
		_handle_snapshot_event(data) -> None
		
		Save messages and request further messages
		"""
		
		pass
	
	def _handle_get_message_reply(self, data):
		"""
		_handle_get_message_reply(data) -> None
		
		Append untruncated message to log file and then continue
		transferring the messages from the temp file to the
		log file.
		"""
		
		pass
	
	def _handle_log_reply(self, data):
		"""
		_handle_log_reply(data) -> None
		
		Save messages received to temp file.
		"""
		
		pass
	
	def launch(self):
		"""
		launch() -> None
		
		Start the download in a separate thread.
		"""
		
		pass
	
	def transfer(self):
		"""
		transfer() -> None
		
		Transfer the messages from the temporary file to the log file.
		"""
		
		pass
