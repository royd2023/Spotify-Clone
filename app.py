import random
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image 
from just_playback import Playback
from tkinter import Listbox, filedialog

import os




# Function to create a frame with the given options and pack it to the left of the parent widget
def create_frame(parent, **options):
    frame = tk.Frame(parent, **options)
    frame.pack(side = "left", padx = 10)
    return frame




playback = Playback()

song_slider = None
slider_update_id = None



# loads the music and sets up the slider bar
def load_music(song_name, frame):
    playback.load_file(song_name)
    create_song_slider(frame)

# creates the song slider
def create_song_slider(frame):
    global song_slider, slider_update_id
    if song_slider is not None:
        if slider_update_id is not None:
            song_slider.after_cancel(slider_update_id)
        song_slider.destroy()

    song_slider = Scale(frame, orient='horizontal', from_= 0, to=playback.duration, length=300)
    song_slider.pack()
    song_slider.bind("<ButtonRelease-1>", update_slider)
    update_slider_position()

# updates the slider bar when user drags it
# the parameter 'event' is not used
def update_slider(event):
    value = song_slider.get() # Get the current slider value
    playback.seek(float(value))
    #print("Seeking to:", playback.curr_pos)
  

def update_slider_position():
    global slider_update_id
    # Get the current playback position and update the slider
    curr_pos = playback.curr_pos
    song_slider.set(curr_pos)    
    # Schedule the next update
    if playback.curr_pos < playback.duration - 1.25 :
        slider_update_id = song_slider.after(1000, update_slider_position)
    

    if playback.curr_pos >= playback.duration - 1.5 :
        if autoplay == True:
            play_next_song()
        else:
            print("Song is done playing")

    
def skip_right_clicked():
    playback.seek(float(playback.curr_pos + 10))
    print("Skipping right to:", playback.curr_pos)

def skip_left_clicked():
    playback.seek(float(playback.curr_pos - 10))
    print("Skipping left to:", playback.curr_pos)


# Function to handle the play/pause button click event
def play_button_clicked():
    if playback.playing and playback.active:
        playback.pause()
        print("Paused at:",playback.curr_pos, "sec")
    else:
        if playback.curr_pos == 0:   
            playback.play()
            print("Starting the song")
            update_slider_position()
        else:
            playback.resume()
            print("Resuming the song")



def download_button_clicked():
    global song_listbox
    
    print("Downloading the song")
    song = filedialog.askopenfilename(initialdir = "songs/", title = "Select a File", filetypes = (("mp3 files", "*.mp3"), ("all files", "*.*")))

    song_downloaded = False
    # Check if the song is already downloaded
    for i in range(song_listbox.size()):
        if song_listbox.get(i) == song:
            # Eventually add a popup message
            print("Song already downloaded")
            song_downloaded = True

    if song and not song_downloaded:
        print("Loading the song from:", song)
        song_listbox.insert(tk.END, song)
        # Ensures that downloading a song won't interrupt the current playback
        if not playback.playing:
            load_music(song, music_frame)
            music_name_label.config(text=song)

# Function to handle the selection of a song from the listbox
def on_song_select(event):
    global song_listbox
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        song = event.widget.get(index)
        print("Selected song:", song)
        music_name_label.config(text=song)
        load_music(song, music_frame)



autoplay = False
# turns on autoplay
def turn_on_autoplay():
    global autoplay
    if autoplay == False:
        autoplay = True
        print("Autoplay is on")
    else: 
        autoplay = False
        print("Autoplay is off")

# handles playing the next song after a current song is done. 
def play_next_song():
    global song_listbox
    current_selection = song_listbox.curselection()
    if current_selection:
        next_index = current_selection[0] + 1

        if shuffle == True:
            select_random_song()
        else:
            if next_index < song_listbox.size():
                
                select_next_song(next_index)
            else:
                # go back to the top of the list
                select_next_song(0)

def select_next_song(index):
    song_listbox.selection_clear(0, tk.END)  # Clear previous selection
    song_listbox.selection_set(index)  # Select the next song
    song_listbox.activate(index)  # Highlight the next song
    song = song_listbox.get(index)
    print("Playing next song:", song)
    music_name_label.config(text=song)
    # temporary solution to prevent the slider from updating after the song is done playing
    if song_slider is not None:
        if slider_update_id is not None:
            song_slider.after_cancel(slider_update_id)
        song_slider.destroy()
    load_music(song, music_frame)
    play_button_clicked()



shuffle = False
def turn_on_shuffle():
    global shuffle
    if shuffle == False:
        shuffle = True
        print("Shuffle is on")
    else:
        shuffle = False
        print("Shuffle is off")

def select_random_song():
    global song_listbox
    song_count = song_listbox.size()
    if song_count > 1:  # Ensure there are at least two songs to choose from
        current_selection = song_listbox.curselection()
        if current_selection:
            current_index = current_selection[0]
            random_index = current_index
            # Ensure the next song is different from the current song
            while random_index == current_index:
                random_index = random.randint(0, song_count - 1)
            select_next_song(random_index)
        else:
            # If no song is currently selected, select a random song
            random_index = random.randint(0, song_count - 1)
            select_next_song(random_index)
    elif song_count == 1:
        select_next_song(0)  # Only one song available, select it
    



def main():
    global root, song_listbox, music_frame, song_slider, music_name_label
    # Create the main window
    root = tk.Tk()
    root.geometry('1280x720') # Set the window size
    root.title('Spotify Clone') # Set the window title
    
    
    # Create a label widget
    label = tk.Label(root, text='Spotify Clone')
    label.pack()

    main_frame = create_frame(root, height=500, width=500, bd = 2, relief = 'solid', highlightbackground="black", highlightthickness=2)
    main_frame.pack()

# --------------------------------------------------------------------------------------------------------------------------------------
    # Create a frame for the album/music art and the music controls
    music_frame = tk.Frame(main_frame, height=500, width=500, bd = 2, relief = 'solid', highlightbackground="black", highlightthickness=2)
    music_frame.pack(side = 'left')
    music_frame.pack_propagate(False)  # Prevents resizing to fit its contents

    
    #img = Image.open("doom_eternal.jpg")
    #img = img.resize((300, 300))  # Resize image to fit within the frame (adjust size as needed)
    #img = ImageTk.PhotoImage(img)  # Convert image to Tkinter format
    # reading the image 
    #panel = tk.Label(music_frame, image = img) 
  
    # setting the application 
    #panel.pack( fill = "both", expand = "yes") 

    music_control_frame = create_frame(music_frame, height=100, width=100, bd = 2, relief = 'solid', highlightbackground="black", highlightthickness=2)
    music_control_frame.pack(side = 'bottom')

    music_name_label = tk.Label(music_frame, text="Music Name")
    music_name_label.pack()

    play_pause_button = tk.Button(music_control_frame, text="Play/Pause", command=play_button_clicked)
    play_pause_button.pack()

    skip_right_button = tk.Button(music_control_frame, text=">>", command=skip_right_clicked)
    skip_right_button.pack(side = 'right')

    skip_left_button = tk.Button(music_control_frame, text="<<", command=skip_left_clicked)
    skip_left_button.pack(side = 'left')

# --------------------------------------------------------------------------------------------------------------------------------------
    # Create the frame for the list of downloaded songs

    list_frame = create_frame(main_frame, height=100, width=100, bd = 2, relief = 'solid', highlightbackground="black", highlightthickness=2)
    list_frame.pack()

    song_listbox = Listbox(list_frame, height=10, width=50)
    song_listbox.pack()
    song_listbox.bind('<<ListboxSelect>>', on_song_select)

    
# --------------------------------------------------------------------------------------------------------------------------------------
    # Create the frame for the other buttons

    other_frame = create_frame(main_frame, height=100, width=100, bd = 2, relief = 'solid', highlightbackground="red", highlightthickness=2)
    other_frame.pack()

    download_button = tk.Button(other_frame, text="Download", command=download_button_clicked)
    download_button.pack()

    autoplay_button = tk.Button(other_frame, text="Autoplay", command = turn_on_autoplay)
    autoplay_button.pack()

    shuffle_button = tk.Button(other_frame, text="Shuffle", command = turn_on_shuffle)
    shuffle_button.pack()

# --------------------------------------------------------------------------------------------------------------------------------------

   

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()