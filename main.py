import json
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import pygame
import threading
from PIL import ImageEnhance
import webbrowser
import random

#--Lotto Number Generation Part--
with open("data.json", "r") as file:
    DATA = json.load(file)

class Numbers:
    def __init__(self):
        pass

    def generate(self):
        prediction = set()
        while len(prediction) < 6:
            pick = random.choices(range(1, 59), DATA)[0]
            prediction.add(pick)
        
        return prediction
    
    def append_data(self, data: list):
        for n in data:
            DATA[n-1] += 1
        
        with open("data.json", "w") as file:
            json.dump(DATA, fp=file)
            

#----------GUI Part----------
#--------TITLE SCREEN--------
def play_music(): #bgmusic
    pygame.mixer.init()
    pygame.mixer.music.load("assets/audio/music.mp3")
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(-1) #4ever loop
class LottoApp:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap("assets/icons/logo.ico")
        self.root.title("Lotto Predictor") #name of window
        self.root.geometry("800x600") #pixelz
        self.root.resizable(False, False) #disable resizing window
        self.scratch_sound = pygame.mixer.Sound("assets/audio/scratch.wav") #pre-loading ksi may delay
        self.scratch_sound.set_volume(0.3)  

        #to load bg
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)  #change num to change opacity
        self.bg_photo = ImageTk.PhotoImage(blended)

        #creates canvas and places bg
        self.canvas = Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        #says the bg music
        self.music_credit = self.canvas.create_text(
            10, 590,
            text="Music: 'Don't Take The Money' by Bleachers (Piano cover)",
            font=("Helvetica", 9, "underline"),
            fill="white",
            anchor="sw"
        )
        #bg music creds is clickable
        self.canvas.tag_bind(self.music_credit, "<Button-1>", self.open_music_link)
        self.canvas.tag_bind(self.music_credit, "<Enter>", lambda e: self.canvas.itemconfig(self.music_credit, fill="yellow"))
        self.canvas.tag_bind(self.music_credit, "<Leave>", lambda e: self.canvas.itemconfig(self.music_credit, fill="white"))

        #title txt img
        original_image = Image.open("assets/images/title.png")
        resized_image = original_image.resize((500, 300))  #width,height
        self.title_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(400, 180, image=self.title_image, anchor="center")

        #scratch button: normal and pressed
        self.lp_button_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button.png").resize((300, 150)))
        self.lp_button_pressed_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button_scratched.png").resize((300, 150)))
        #the LP button
        self.predict_btn = self.canvas.create_image(400, 400, image=self.lp_button_img, anchor="center")

        #scratch effect + fade music
        def press_predict(e):
            self.canvas.itemconfig(self.predict_btn, image=self.lp_button_pressed_img)
            self.scratch_sound.play()
            pygame.mixer.music.fadeout(2000)
            #after 3.5 seconds, fade to black
            self.root.after(2500, self.fade_to_black)
            print("Let's Predict clicked!")
        self.canvas.tag_bind(self.predict_btn, "<Button-1>", press_predict)
    
    def fade_to_black(self):
        self.fade_level = 0
        self._fade_step()
    def _fade_step(self):
        if self.fade_level <= 255:
            # Create a black transparent rectangle
            fade_overlay = Image.new("RGBA", (800, 600), (0, 0, 0, self.fade_level))
            self.fade_photo = ImageTk.PhotoImage(fade_overlay)
            self.fade_item = self.canvas.create_image(0, 0, anchor="nw", image=self.fade_photo)
            self.fade_level += 15  # Adjust for speed (lower = slower)
            self.root.after(50, self._fade_step)
    def open_music_link(self, event=None):
        webbrowser.open("https://www.youtube.com/watch?v=703Tr9I8ZR4")


#run
if __name__ == "__main__":
    #starts music in bg
    threading.Thread(target=play_music, daemon=True).start()
    root = tk.Tk()
    app = LottoApp(root)
    root.mainloop()
#yan muna for now habang wala pa yung 6 numbers generated hehe