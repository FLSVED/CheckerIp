import vlc
import logging
from tkinter import messagebox

__version__ = "1.0.0"

class StreamManager:
    def __init__(self):
        pass

    def test_stream(self, stream_url, mac):
        try:
            instance = vlc.Instance()
            player = instance.media_player_new()
            media = instance.media_new(stream_url)
            player.set_media(media)

            player.play()
            time.sleep(2) # Réduit à 2 secondes pour une vérification rapide
            state = player.get_state()
            player.stop()

            return state == vlc.State.Playing
        except Exception as e:
            logging.error(f"Erreur lors du test du flux {stream_url} avec MAC {mac}: {e}")
            return False

    def play_with_vlc(self, stream_url):
        try:
            instance = vlc.Instance()
            player = instance.media_player_new()
            media = instance.media_new(stream_url)
            player.set_media(media)
            player.play()

            # Attendre que le flux commence à jouer
            while True:
                state = player.get_state()
                if state == vlc.State.Playing:
                    messagebox.showinfo("Info", "Lecture du flux en cours...")
                    break
                elif state in [vlc.State.Error, vlc.State.Ended]:
                    messagebox.showwarning("Avertissement", "Impossible de lire le flux.")
                    break
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du flux avec VLC: {e}")
            messagebox.showerror("Erreur", "Erreur lors de la tentative de lecture avec VLC.")
