import vlc

import logging

import time

from tkinter import messagebox


__version__ = "2.0.0"


class StreamManager:

	def __init__(self):
		self.instance = vlc.Instance()
		self.player = self.instance.media_player_new()

	def test_stream(self, stream_url, mac):
		try:
			media = self.instance.media_new(stream_url)
			self.player.set_media(media)
			self.player.play()
			time.sleep(2)
			state = self.player.get_state()
			self.player.stop()
			return state == vlc.State.Playing
		except Exception as e:
			logging.error(f"Error testing stream {stream_url} with MAC {mac}: {e}")
			return False

	def play_with_vlc(self, stream_url):
		try:
			media = self.instance.media_new(stream_url)
			self.player.set_media(media)
			self.player.play()

			while True:
				state = self.player.get_state()
				if state == vlc.State.Playing:
					messagebox.showinfo("Info", "Stream is playing...")
					break
				elif state in [vlc.State.Error, vlc.State.Ended]:
					messagebox.showwarning("Warning", "Unable to play the stream.")
					break
		except Exception as e:
			logging.error(f"Error playing stream with VLC: {e}")
			messagebox.showerror("Error", "Error attempting to play with VLC.")
