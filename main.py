import os
import time
import tkinter
import pygame
import vlc
from random import randint
from tkinter.filedialog import askdirectory
from tkinter import ttk
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from datetime import datetime

year = datetime.now().strftime("%Y")

print(
    """
 _____  ____      _     ____   _____  _   _  ____    _   _  _____ _   _  _         _    
| ____||  _ \    / \   / ___| |_   _|| | | |/ ___|  | \ | ||__  /| | | || |       / \   
|  _|  | |_) |  / _ \  \___ \   | |  | | | |\___ \  |  \| |  / / | | | || |      / _ \  
| |___ |  _ <  / ___ \  ___) |  | |  | |_| | ___) | | |\  | / /_ | |_| || |___  / ___ \ 
|_____||_| \_\/_/   \_\|____/   |_|   \___/ |____/  |_| \_|/____| \___/ |_____|/_/   \_\ 
    
    """
)

print("\n****************************************************************")
print(
    """
* This is an open player project.
* Feel free to make any alterations to suit your interest.
* Any damage that may result from this program or its alteration
    the owner is not to be held liable.
    """
)
print(f"* Copyright - Erastus Nzula, {year} *")
print("\n****************************************************************")

pygame.init()
instance = vlc.Instance()


class Player(tkinter.Tk):
    """A class to hold all player functionalities."""

    def __init__(self):
        """Initialize the class attributes."""
        super(Player, self).__init__()
        self.title("")
        self.geometry("1350x690+0+0")
        self.protocol('WM_DELETE_WINDOW', self.exit_player)

        for folder, subFolder, files in os.walk('.'):
            for file in files:
                if file == "icon.ico":  # search for icon.ico file.
                    self.root.iconbitmap(file)
            else:
                pass

        # Ttk style to style the progress bar.
        style = ttk.Style()
        style.theme_use('alt')
        style.configure("Blue.Horizontal.TProgressbar")

        # Binding keyboard keys.
        self.bind("<Double-Button>", self.play_file)
        self.bind("<Return>", self.play_file)
        self.bind("<n>", self.play_next_file)
        self.bind("<p>", self.play_previous_file)
        self.bind("<i>", self.increase_volume)
        self.bind("<d>", self.decrease_volume)
        self.bind("<r>", self.view_playlist_control)
        self.bind("<f>", self.view_playlist_control)
        self.bind("<m>", self.mute_file)
        self.bind("<Escape>", self.exit_player)

        # The default font.
        self.font = "Times 13"

        # Declared variables.
        self.add_files_directory_image = None
        self.play_file_image = None
        self.playing_file_image = None
        self.stop_image = None
        self.playlist_image = None
        self.mute_image = None
        self.shuffle_image = None
        self.order_image = None
        self.play_next_file_image = None
        self.play_previous_file_image = None
        self.repeat_image = None
        self.sound_image = None
        self.file = None
        self.player = None
        self.total_length = None
        self.total_length_formatted = None
        self.volume = None
        self.loops = 1
        self.previous_volume = []
        self.favourite = []
        self.video_file_playing = False
        self.view_playlist = False
        self.pause = False
        self.video_file_pause = False
        self.repeat_current_file = False
        self.shuffle = False
        self.mute = False
        self.display_current_file = tkinter.StringVar()
        self.file_start = tkinter.StringVar(value="00 : 00")
        self.file_end = tkinter.StringVar(value="00 : 00")

        # Load buttons.
        self.load_buttons_images()

        # Labels and frames.
        self.label = tkinter.Label(self, text="EMU-PLAYER", background="Light Grey", bd=5, relief=tkinter.GROOVE,
                                   font="Times 13 bold")
        self.label.pack(fill=tkinter.BOTH)
        self.current_file = tkinter.Label(self, textvariable=self.display_current_file, background="White", bd=5,
                                          relief=tkinter.GROOVE,
                                          font=self.font)
        self.current_file.pack(fill=tkinter.BOTH)

        self.playlist_frame = tkinter.Frame(self)
        self.playlist_frame.pack(fill=tkinter.BOTH)
        self.playlist_scroll = tkinter.Scrollbar(self.playlist_frame, orient=tkinter.VERTICAL)
        self.playlist_scroll.pack(fill=tkinter.Y, side=tkinter.RIGHT)
        self.playlist_box = tkinter.Listbox(self.playlist_frame, background="Light Grey", width=70, height=25,
                                            yscrollcommand=self.playlist_scroll.set,
                                            selectmode=tkinter.EXTENDED, font=self.font)
        self.playlist_box.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
        self.playlist_scroll.config(command=self.playlist_box.yview)

        self.video_files_frame = tkinter.Frame(self.playlist_frame, bd=5,
                                               relief=tkinter.GROOVE)
        self.video_files_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.video_files_label = tkinter.Label(self.video_files_frame, bd=5, background="Light Grey", width=100,
                                               height=25, font=self.font)
        self.video_files_label.pack(fill=tkinter.BOTH)

        self.buttons_frame = tkinter.Frame(self, relief=tkinter.GROOVE, bd=5, background="Light Grey")
        self.buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH)

        self.duration_frame = tkinter.Frame(self, relief=tkinter.GROOVE, bd=5, background="White")
        self.duration_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH)
        self.file_start_label = tkinter.Label(self.duration_frame, textvariable=self.file_start)
        self.file_start_label.pack(side=tkinter.LEFT)

        self.file_progress_label = ttk.Progressbar(self.duration_frame,
                                                   orient=tkinter.HORIZONTAL, mode="determinate", length=1255)
        self.file_progress_label.pack(fill=tkinter.X, side=tkinter.LEFT, padx=5)

        self.file_end_label = tkinter.Label(self.duration_frame, textvariable=self.file_end)
        self.file_end_label.pack(side=tkinter.LEFT)

        # Buttons.
        self.add_files_directory_button = tkinter.Button(self.buttons_frame, text="Add",
                                                         command=self.add_files_directory,
                                                         image=self.add_files_directory_image)
        self.play_file_button = tkinter.Button(self.buttons_frame, text="Play", command=self.play_file,
                                               image=self.play_file_image)
        self.play_next_file_button = tkinter.Button(self.buttons_frame, text="Play Next", command=self.play_next_file,
                                                    image=self.play_next_file_image)
        self.play_previous_file_button = tkinter.Button(self.buttons_frame, text="Play Previous",
                                                        command=self.play_previous_file,
                                                        image=self.play_previous_file_image)
        self.stop_button = tkinter.Button(self.buttons_frame, text="Stop", command=self.stop, image=self.stop_image)

        self.mute_button = tkinter.Button(self.buttons_frame, text="Mute", command=self.mute_file,
                                          image=self.mute_image)
        self.order_button = tkinter.Button(self.buttons_frame, text="Order", command=self.loops_control,
                                           image=self.order_image, background="Pink")
        self.shuffle_button = tkinter.Button(self.buttons_frame, text="Shuffle", command=self.shuffle_mode,
                                             image=self.shuffle_image)

        self.view_playlist_button = tkinter.Button(self.buttons_frame, text="View Playlist", image=self.playlist_image,
                                                   command=self.view_playlist_control)

        self.favourite_button = tkinter.Button(self.buttons_frame, text="-Add to Favourite-",
                                               command=self.add_to_favorite, font=self.font)
        self.delete_button = tkinter.Button(self.buttons_frame, text="-Delete-",
                                            command=self.delete, font=self.font)
        self.clear_button = tkinter.Button(self.buttons_frame, text="-Clear-",
                                           command=self.clear, font=self.font)

        # Volume scale.
        self.volume_scale = tkinter.Scale(self.buttons_frame, width=10, sliderlength=20, length=100,
                                          orient=tkinter.HORIZONTAL, command=self.get_volume)
        self.volume_scale.set(80)

        # Pack the buttons.
        self.add_files_directory_button.pack(side=tkinter.LEFT)
        self.play_previous_file_button.pack(side=tkinter.LEFT)
        self.play_file_button.pack(side=tkinter.LEFT)
        self.play_next_file_button.pack(side=tkinter.LEFT)
        self.mute_button.pack(side=tkinter.LEFT)
        self.order_button.pack(side=tkinter.LEFT)
        self.shuffle_button.pack(side=tkinter.LEFT)
        self.stop_button.pack(side=tkinter.LEFT)
        self.view_playlist_button.pack(side=tkinter.LEFT)
        self.favourite_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.delete_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.clear_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.volume_scale.pack(side=tkinter.RIGHT)

    def load_buttons_images(self):
        """Load image buttons into tkinter."""
        self.add_files_directory_image = ImageTk.PhotoImage(Image.open("Buttons/add.jpg").resize((40, 27)))
        self.play_file_image = ImageTk.PhotoImage(Image.open("Buttons/play.jpg").resize((40, 27)))
        self.play_next_file_image = ImageTk.PhotoImage(Image.open("Buttons/next.jpg").resize((40, 27)))
        self.play_previous_file_image = ImageTk.PhotoImage(Image.open("Buttons/previous.jpg").resize((40, 27)))
        self.playing_file_image = ImageTk.PhotoImage(Image.open("Buttons/playing.jpg").resize((40, 27)))
        self.stop_image = ImageTk.PhotoImage(Image.open("Buttons/stop.jpg").resize((40, 27)))
        self.mute_image = ImageTk.PhotoImage(Image.open("Buttons/sound.jpg").resize((40, 27)))
        self.sound_image = ImageTk.PhotoImage(Image.open("Buttons/mute.jpg").resize((40, 27)))
        self.order_image = ImageTk.PhotoImage(Image.open("Buttons/order.jpg").resize((40, 27)))
        self.shuffle_image = ImageTk.PhotoImage(Image.open("Buttons/shuffle.jpg").resize((40, 27)))
        self.playlist_image = ImageTk.PhotoImage(Image.open("Buttons/playlist.png").resize((40, 27)))
        self.repeat_image = ImageTk.PhotoImage(Image.open("Buttons/repeat.png").resize((40, 27)))

    def add_files_directory(self):
        """Add files into the playlist."""
        try:
            directory = askdirectory()
            os.chdir(directory)
            for files in os.listdir():
                if not (
                        (files.endswith(".mp4")) or
                        (files.endswith(".mp3")) or
                        (files.endswith(".webm")) or
                        (files.endswith(".mkv")) or
                        (files.endswith(".VOB")) or
                        (files.endswith(".avi")) or
                        (files.endswith(".wav"))
                ):
                    continue
                self.playlist_box.insert(tkinter.END, files)
        except OSError:
            pass

    def play_file(self, *args):
        """
        Check if the file is an audio or a video and
        initiate the necessary play method.
        """
        if self.playlist_box.curselection():
            self.file = self.playlist_box.get(tkinter.ACTIVE)
            self.playlist_box.selection_set(tkinter.ACTIVE)
            if (
                    (self.file.endswith(".mp4")) or
                    (self.file.endswith(".webm")) or
                    (self.file.endswith(".mkv")) or
                    (self.file.endswith(".VOB")) or
                    (self.file.endswith(".avi")) or
                    (self.file.endswith(".wav"))
            ):
                self.play_video_file()
            else:
                if not self.video_file_playing:
                    self.play_audio_file()
                else:
                    self.player.stop()
                    self.play_audio_file()
                    self.play_file_button.config(image=self.playing_file_image)
            self.display_current_file.set(self.file)
            self.play_file_button.config(image=self.playing_file_image)

    def play_audio_file(self):
        """Play audio files."""
        self.pause = False
        self.video_file_playing = False
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play(loops=self.loops)
        file = MP3(self.file)
        self.total_length_formatted = time.strftime("%M : %S", time.gmtime(file.info.length))
        self.total_length = file.info.length
        self.audio_file_duration()
        self.play_file_button.config(image=self.playing_file_image, command=self.pause_audio_file)
        self._video_playlist_frames_restoration()
        self.view_playlist_button.config(state=tkinter.DISABLED)
        self.bind("<space>", self.pause_audio_file)
        self.video_files_label.config(text=self.file)
        if self.total_length <= 0:
            self.play_next_file()

    def audio_file_duration(self):
        """Track audio files duration."""
        if self.playlist_box.curselection() and not self.video_file_playing:
            self.video_file_playing = False
            file_play_time = pygame.mixer.music.get_pos() / 1000
            self.file_progress_label.config(value=file_play_time / self.total_length * 100)
            file_play_time_formatted = time.strftime("%M : %S", time.gmtime(file_play_time))
            if round(self.file_progress_label.cget('value')) == 100 and self.loops == 1:
                if self.playlist_box.size() - 1 == self.playlist_box.curselection()[0]:
                    self.playlist_box.selection_clear(tkinter.ACTIVE)
                    self.playlist_box.selection_set(0)
                    self.playlist_box.activate(0)
                    self.play_file()

                else:
                    self.play_next_file()
            elif round(self.file_progress_label.cget('value')) == 100 and self.loops == -1:
                self.play_file()
            elif round(self.file_progress_label.cget('value')) == 100 and self.loops == 0:
                self.play_in_shuffle_mode()
            self.file_start.set(str(file_play_time_formatted))
            self.file_end.set(str(self.total_length_formatted))
            self.file_start_label.after(1000, self.audio_file_duration)

    def play_video_file(self):
        """Play video files."""
        self.video_file_playing = True
        self.video_file_pause = False
        self.stop()
        self.player = instance.media_player_new()
        file = instance.media_new(self.file)
        self.player.set_hwnd(self.video_files_label.winfo_id())
        self.player.set_media(file)
        self.player.play()
        volume = self.volume_scale.get()
        self.player.audio_set_volume(volume)
        time.sleep(0.5)
        self.video_file_duration()
        self.play_file_button.config(image=self.playing_file_image, command=self.pause_video_file)
        self._video_playlist_frames_enlargement()
        self.view_playlist_button.config(state=tkinter.ACTIVE)
        self.bind("<space>", self.pause_video_file)
        if self.player.get_length() <= 0:
            self.play_next_file()

    def video_file_duration(self):
        """Track video files duration."""
        if self.playlist_box.curselection() and self.video_file_playing:
            video_total_length = self.player.get_length() / 1000
            file_play_time = self.player.get_position()
            file_play_time_formatted = time.strftime("%M : %S", time.gmtime(file_play_time * video_total_length))
            self.file_start.set(file_play_time_formatted)
            total_length_formatted = time.strftime("%M : %S", time.gmtime(video_total_length))
            self.file_end.set(total_length_formatted)
            self.file_progress_label.config(value=file_play_time * 100)
            if round(self.file_progress_label.cget('value')) == 100 and self.loops == 1:
                if self.playlist_box.size() - 1 == self.playlist_box.curselection()[0]:
                    self.playlist_box.selection_clear(tkinter.ACTIVE)
                    self.playlist_box.selection_set(0)
                    self.playlist_box.activate(0)
                    self.play_file()

                else:
                    self.play_next_file()
            elif round(self.file_progress_label.cget('value')) == 100 and self.loops == -1:
                self.play_file()
            elif round(self.file_progress_label.cget('value')) == 100 and self.loops == 0:
                self.play_in_shuffle_mode()
            self.file_start_label.after(1000, self.video_file_duration)

    def _video_playlist_frames_enlargement(self):
        """Screen enlargement."""
        self.playlist_frame.place(x=0, y=0)
        # self.playlist_box.config(height=50, width=192)
        self.video_files_frame.pack()
        self.video_files_label.config(height=30, width=150)
        self.view_playlist = False
        self.title(self.file)

    def _video_playlist_frames_restoration(self):
        """Restore default screen size."""
        self.playlist_frame.pack(fill=tkinter.BOTH)
        self.playlist_box.config(width=70, height=25)
        self.video_files_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.video_files_label.config(height=25, width=100)
        self.view_playlist = True
        self.title("")

    def add_to_favorite(self):
        """Store favourite files."""
        if self.playlist_box.curselection():
            favourite = self.playlist_box.curselection()
            get_favourite = self.playlist_box.get(favourite)
            if get_favourite not in self.favourite:
                self.favourite.append(get_favourite)
            print(self.favourite)

    def view_playlist_control(self, *args):
        """Facilitate screen enlargement and restoration."""
        if self.video_file_playing:
            if self.view_playlist:
                self._video_playlist_frames_enlargement()
                self.view_playlist = False
            else:
                self._video_playlist_frames_restoration()
                self.view_playlist = True

    def loops_control(self):
        """Facilitate change in loops."""
        if self.repeat_current_file and (self.loops == -1 or self.loops == 0):
            self.loops = 1

            self.order_button.config(image=self.order_image, background="Pink")
            self.shuffle_button.config(background="Light Grey")
            self.repeat_current_file = False
        else:
            self.loops = -1

            self.order_button.config(image=self.repeat_image, background="Pink")
            self.shuffle_button.config(background="Light Grey")
            self.repeat_current_file = True

    def shuffle_mode(self):
        """Facilitate changes in shuffle."""
        if self.shuffle:
            self.loops = 1
            self.order_button.config(image=self.order_image, background="Pink")
            self.shuffle_button.config(background="Light Grey")
            self.shuffle = False
        else:
            self.loops = 0
            self.order_button.config(image=self.order_image, background="Light Grey")
            self.shuffle_button.config(background="Pink")
            self.shuffle = True

    def mute_file(self, *args):
        """Mute playing file."""
        if self.mute:
            pygame.mixer.music.set_volume(self.previous_volume[0] / 100)
            self.volume_scale.set(self.previous_volume[0])
            self.mute = False
            self.mute_button.config(image=self.mute_image)
        else:
            del self.previous_volume[:]
            volume = self.volume_scale.get()
            self.previous_volume.append(volume)
            pygame.mixer.music.set_volume(0)
            self.volume_scale.set(0)
            self.mute_button.config(image=self.sound_image)
            self.mute = True

    def play_next_file(self, *args):
        """Play the next file."""
        if self.playlist_box.curselection():
            current_file = self.playlist_box.curselection()
            self.playlist_box.selection_clear(tkinter.ACTIVE)
            file = current_file[0] + 1
            self.playlist_box.selection_set(file)
            self.playlist_box.activate(file)
            self.play_file()

    def play_previous_file(self, *args):
        """Play the previous file."""
        if self.playlist_box.curselection():
            current_file = self.playlist_box.curselection()
            self.playlist_box.selection_clear(tkinter.ACTIVE)
            file = current_file[0] - 1
            self.playlist_box.selection_set(file)
            self.playlist_box.activate(file)
            self.play_file()

    def play_in_shuffle_mode(self):
        """Initiate shuffle mode."""
        if self.playlist_box.curselection():
            self.playlist_box.selection_clear(tkinter.ACTIVE)
            file = randint(0, self.playlist_box.size())
            self.playlist_box.selection_set(file)
            self.playlist_box.activate(file)
            self.play_file()

    def pause_audio_file(self, *args):
        """Pause playing audio file."""
        if self.pause:
            pygame.mixer.music.unpause()
            self.pause = False
            self.play_file_button.config(image=self.playing_file_image)
        else:
            pygame.mixer.music.pause()
            self.pause = True
            self.play_file_button.config(image=self.play_file_image)

    def pause_video_file(self, *args):
        """Pause playing video file."""
        if self.video_file_pause:
            self.player.play()
            self.video_file_pause = False
            self.play_file_button.config(image=self.playing_file_image)
        else:
            self.player.pause()
            self.video_file_pause = True
            self.play_file_button.config(image=self.play_file_image)

    def stop(self):
        """Stop playing file."""
        self._video_playlist_frames_restoration()
        try:
            pygame.mixer.music.stop()
            self.player.stop()
            self.play_file_button.config(image=self.play_file_image, command=self.play_video_file)
        except AttributeError:
            pygame.mixer.music.stop()
            self.play_file_button.config(image=self.play_file_image, command=self.play_audio_file)

    def get_volume(self, volume):
        """Set volume."""
        try:
            self.volume = float(volume) / 100
            pygame.mixer.music.set_volume(self.volume)
            self.player.audio_set_volume(int(self.volume * 100))
        except AttributeError:
            pass

    def increase_volume(self, *args):
        """Increase volume."""
        current_volume = self.volume_scale.get()
        volume = int(current_volume)
        volume += 1
        self.volume_scale.set(volume)

    def decrease_volume(self, *args):
        """Decrease volume."""
        current_volume = self.volume_scale.get()
        volume = int(current_volume)
        volume -= 1
        self.volume_scale.set(volume)

    def clear(self):
        """Clear playlist."""
        self.stop()
        self.playlist_box.delete(0, tkinter.END)
        self._video_playlist_frames_restoration()
        self.display_current_file.set("")
        self.file_start.set("00 : 00")
        self.file_end.set("00 : 00")
        self.file_progress_label.config(value=0)

    def delete(self):
        """Delete a file."""
        files = self.playlist_box.curselection()
        for file in files:
            file_ = self.playlist_box.get(file)
            if file_ == self.file:
                self.stop()
                self.playlist_box.delete(file)
            else:
                self.playlist_box.delete(file)

    def exit_player(self, *args):
        """The exit protocol."""
        self.destroy()
        self.quit()


if __name__ == "__main__":
    player = Player()
    player.mainloop()
