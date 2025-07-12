import json
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from PIL import ImageEnhance
import pygame
import threading
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
#----------BG MUSIC----------
def play_music(volume=0.3): #bgmusic
    pygame.mixer.init()
    pygame.mixer.music.load("assets/audio/music.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1) #4ever loop

#-----REST OF THE CODE------
class LottoApp:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap("assets/icons/logo.ico")
        self.root.title("Lotto Predictor")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.canvas = Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        #audio stuffs
        self.scratch_sound = pygame.mixer.Sound("assets/audio/scratch.wav")
        self.scratch_sound.set_volume(0.3)
        self.ding_sound = pygame.mixer.Sound("assets/audio/ding.wav")
        self.ding_sound.set_volume(0.3) #adjust volume
        self.roll_sound = pygame.mixer.Sound("assets/audio/rolling.wav")
        self.roll_sound.set_volume(0.3)
        self.annoyed_sound = pygame.mixer.Sound("assets/audio/annoyed_sound.wav")
        self.annoyed_sound.set_volume(0.01) #volume
        self.music_volume = 0.15  #default value
        #img stuffs
        self.slot_machine_img = ImageTk.PhotoImage(
            Image.open("assets/images/slot_machine.png").resize((800, 500))
        )
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)
        self.bg_photo = ImageTk.PhotoImage(blended)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        original_image = Image.open("assets/images/title.png")
        resized_image = original_image.resize((500, 300))
        self.title_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(400, 180, image=self.title_image, anchor="center")
        self.lp_button_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button.png").resize((300, 150)))
        self.lp_button_pressed_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button_scratched.png").resize((300, 150)))
        self.predict_btn = self.canvas.create_image(400, 400, image=self.lp_button_img, anchor="center")
        self.goodluck_img = ImageTk.PhotoImage(Image.open("assets/images/goodluck.png").resize((250, 60)))
        self.press_lever_img = ImageTk.PhotoImage(Image.open("assets/images/press_lever.png").resize((300, 80)))
        self.return_to_title_screen()
        self.clear_spam_count = 0
        self.clear_spam_reset_job = None
        self.annoyed_overlay = None
        self.annoyed_img = ImageTk.PhotoImage(
            Image.open("assets/images/annoyed_overlay.png").resize((800, 600))
        )
        #layer png
        self.back_btn_img = ImageTk.PhotoImage(Image.open("assets/images/back_button.png").resize((120, 80)))
        self.current_frame = 0
        self.animate_gif()
        #def stuff
        def press_predict(e):
            self.canvas.itemconfig(self.predict_btn, image=self.lp_button_pressed_img)
            self.scratch_sound.play()
            pygame.mixer.music.fadeout(2000)
            self.root.after(1200, self.fade_to_black_and_transition)
            print("Let's Predict clicked!")
        self.canvas.tag_bind(self.predict_btn, "<Button-1>", press_predict)
        #making invisible rectangle
        rect_id = self.canvas.create_rectangle(
            700, 180, 750, 330,
            outline="", fill=""
        )
        self.canvas.itemconfig(rect_id, state="normal", width=0)
        self.canvas.tag_bind(rect_id, "<Button-1>", self.pull_lever)
    
    def open_music_link(self, event=None): #music credits
        webbrowser.open("https://www.youtube.com/watch?v=703Tr9I8ZR4")

    def fade_to_black_and_transition(self): #title screen fade
        self.fade_level = 0
        def continue_to_next():
            self.show_slot_machine_screen()
        self._fade_step(callback=continue_to_next)

    def _fade_step(self, callback=None):
        if self.fade_level <= 255:
            fade_overlay = Image.new("RGBA", (800, 600), (0, 0, 0, self.fade_level))
            self.fade_photo = ImageTk.PhotoImage(fade_overlay)
            self.fade_item = self.canvas.create_image(0, 0, anchor="nw", image=self.fade_photo)
            self.fade_level += 15
            self.root.after(50, lambda: self._fade_step(callback))
        elif callback:
            callback()

    def show_settings_screen(self):
        self.canvas.delete("all")
        #title screen
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)
        self.bg_photo = ImageTk.PhotoImage(blended)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        #settings layout
        self.settings_bg_img = ImageTk.PhotoImage(
            Image.open("assets/images/settings_screen.png").resize((800, 600))
        )
        self.canvas.create_image(0, 0, anchor="nw", image=self.settings_bg_img)
        #volume knob
        self.slider_knob_img = ImageTk.PhotoImage(
            Image.open("assets/images/slider_knob.png").resize((90, 80), Image.Resampling.LANCZOS)
        )
        #initial volume
        self.music_volume = 0.2
        self.sfx_volume = 0.3
        #volume bar range
        music_start_x = 500
        music_end_x = 630
        music_y = 280
        sfx_start_x = 390
        sfx_end_x = 530
        sfx_y = 360
        #mixer volumes
        pygame.mixer.music.set_volume(self.music_volume)
        for sound in [self.scratch_sound, self.roll_sound, self.ding_sound, self.annoyed_sound]:
            sound.set_volume(self.sfx_volume)
        #position knobs 30%
        music_x = music_start_x + int(self.music_volume * (music_end_x - music_start_x))
        sfx_x = sfx_start_x + int(self.sfx_volume * (sfx_end_x - sfx_start_x))
        #draw knobs
        self.music_knob = self.canvas.create_image(music_x, music_y, image=self.slider_knob_img, anchor="center")
        self.sfx_knob = self.canvas.create_image(sfx_x, sfx_y, image=self.slider_knob_img, anchor="center")
        self.canvas.tag_bind(self.music_knob, "<B1-Motion>", lambda e: self.update_volume_knob(e, "music"))
        self.canvas.tag_bind(self.sfx_knob, "<B1-Motion>", lambda e: self.update_volume_knob(e, "sfx"))
        #back button
        self.back_button = self.canvas.create_image(50, 40, image=self.back_btn_img, anchor="center")
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda e: self.return_to_title_screen())

    def sync_music_volume(self):
        pygame.mixer.music.set_volume(self.music_volume)
        if hasattr(self, 'ambience') and self.ambience:
            self.ambience.set_volume(self.music_volume)

    def update_volume_knob(self, event, target):
        #customize hitbox and knob position
        music_start_x = 390
        music_end_x = 600
        music_y = 400
        sfx_start_x = 390
        sfx_end_x = 600
        sfx_y = 360
        if target == "music":
            x = min(max(event.x, music_start_x), music_end_x)
            percent = (x - music_start_x) / (music_end_x - music_start_x)
            self.music_volume = percent
            pygame.mixer.music.set_volume(self.music_volume)
            self.canvas.coords(self.music_knob, x, 280)
        elif target == "sfx":
            x = min(max(event.x, sfx_start_x), sfx_end_x)
            percent = (x - sfx_start_x) / (sfx_end_x - sfx_start_x)
            self.sfx_volume = percent
            for sound in [self.scratch_sound, self.roll_sound, self.ding_sound, self.annoyed_sound]:
                sound.set_volume(self.sfx_volume)
            self.canvas.coords(self.sfx_knob, x, 360)

    def pull_lever(self, event=None):
        if hasattr(self, 'lever_prompt_item') and self.lever_prompt_item:
            self.blink_visible = False
            self.canvas.delete(self.lever_prompt_item)
            self.lever_prompt_item = None
        #delete 'goodluck' if still thereee
        if self.goodluck_item:
            self.canvas.delete(self.goodluck_item)
            self.goodluck_item = None
        print("Lever pulled!")
        self.generator = Numbers()
        final_numbers = list(self.generator.generate())
        final_numbers.sort()
        self.roll_numbers(final_numbers)

    def show_music_credit(self):
        self.music_credit = self.canvas.create_text(
            10, 590,
            text="Music: 'Don't Take The Money' by Bleachers (Piano cover)",
            font=("Helvetica", 9, "underline"),
            fill="white",
            anchor="sw"
        )
        self.canvas.tag_bind(self.music_credit, "<Button-1>", self.open_music_link)
        self.canvas.tag_bind(self.music_credit, "<Enter>", lambda e: self.canvas.itemconfig(self.music_credit, fill="yellow"))
        self.canvas.tag_bind(self.music_credit, "<Leave>", lambda e: self.canvas.itemconfig(self.music_credit, fill="white"))

    def set_music_volume(self, value):
        pygame.mixer.music.set_volume(int(value)/100)

    def set_sfx_volume(self, value):
        volume = int(value) / 100

        if hasattr(self, 'scratch_sound') and self.scratch_sound:
            self.scratch_sound.set_volume(volume)
        if hasattr(self, 'ding_sound') and self.ding_sound:
            self.ding_sound.set_volume(volume)
        if hasattr(self, 'roll_sound') and self.roll_sound:
            self.roll_sound.set_volume(volume)
        if hasattr(self, 'annoyed_sound') and self.annoyed_sound:
            self.annoyed_sound.set_volume(volume)
        if hasattr(self, 'ambience') and self.ambience:
            self.ambience.set_volume(volume)

    def exit_settings_screen(self):
        self.return_to_title_screen()

    def return_to_title_screen(self):
        #stops ambience
        if hasattr(self, 'ambience') and self.ambience:
            self.ambience.stop()
            self.ambience = None
        #resets canvas
        self.canvas.delete("all")
        self.goodluck_item = None
        #bg setup
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)
        self.bg_photo = ImageTk.PhotoImage(blended)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        #title logo
        original_image = Image.open("assets/images/title.png")
        resized_image = original_image.resize((500, 300))
        self.title_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(400, 180, image=self.title_image, anchor="center")
        #predict button
        self.lp_button_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button.png").resize((300, 150)))
        self.lp_button_pressed_img = ImageTk.PhotoImage(Image.open("assets/images/lp_button_scratched.png").resize((300, 150)))
        self.predict_btn = self.canvas.create_image(400, 400, image=self.lp_button_img, anchor="center")
        def press_predict(e):
            self.canvas.itemconfig(self.predict_btn, image=self.lp_button_pressed_img)
            self.scratch_sound.play()
            pygame.mixer.music.fadeout(2000)
            self.root.after(1200, self.fade_to_black_and_transition)
            print("Let's Predict clicked!")
        self.canvas.tag_bind(self.predict_btn, "<Button-1>", press_predict)
        #dev button
        self.devs_btn_img = ImageTk.PhotoImage(Image.open("assets/images/devs_button.png").resize((120, 80)))
        self.devs_btn = self.canvas.create_image(50, 40, image=self.devs_btn_img, anchor="center")
        self.canvas.tag_bind(self.devs_btn, "<Button-1>", lambda e: self.show_devs_screen())
        self.show_music_credit() #music credits (title screen and devs screen)
        #starts background music if not playing
        if not pygame.mixer.music.get_busy():
            threading.Thread(target=play_music, args=(self.music_volume,), daemon=True).start()
        else:
            pygame.mixer.music.set_volume(self.music_volume)  #syncs volume
        self.settings_btn_img = ImageTk.PhotoImage(Image.open("assets/images/settings_button.png").resize((120, 80)))
        self.settings_btn = self.canvas.create_image(740, 40, image=self.settings_btn_img, anchor="center")
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", lambda e: self.show_settings_screen())

    def show_slot_machine_screen(self):
        self.canvas.delete("all")
        #bg animation
        self.slot_frames = []
        try:
            gif = Image.open("assets/images/casino_loop.gif")
            while True:
                frame = gif.copy().resize((800, 600))
                self.slot_frames.append(ImageTk.PhotoImage(frame))
                gif.seek(len(self.slot_frames))
        except EOFError:
            pass
        self.slot_bg_item = self.canvas.create_image(0, 0, anchor="nw", image=self.slot_frames[0])
        self.current_frame = 0
        self.animate_gif()
        #ambience sound
        pygame.mixer.music.stop()
        self.ambience = pygame.mixer.Sound("assets/audio/ambience.mp3")
        self.ambience.set_volume(self.music_volume)
        self.ambience.play(-1)
        #slot machine png
        raw_slot_img = Image.open("assets/images/slot_machine.png").resize((800, 500))
        enhancer = ImageEnhance.Contrast(raw_slot_img)
        contrast_img = enhancer.enhance(1.0)
        enhancer = ImageEnhance.Brightness(contrast_img)
        bright_img = enhancer.enhance(1.0)
        self.slot_machine_cover_img = ImageTk.PhotoImage(bright_img)
        self.canvas.create_image(400, 280, image=self.slot_machine_cover_img, anchor="center")
        #each generated numbers
        self.slot_texts = []
        slot_positions = [
            (170, 340),  #1
            (260, 340),  #2
            (350, 340),  #3
            (438, 340),  #4
            (524, 340),  #5
            (613, 340)   #6
        ]
        for x, y in slot_positions:
            text_ids = []
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                shadow = self.canvas.create_text(x + dx, y + dy, text="--", font=("Courier", 32, "bold"), fill="black")
                text_ids.append(shadow)
            center = self.canvas.create_text(x, y, text="--", font=("Courier", 32, "bold"), fill="white")
            text_ids.append(center)
            self.slot_texts.append(text_ids)
        #back button img
        self.back_button = self.canvas.create_image(50, 40, image=self.back_btn_img, anchor="center")
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda e: self.return_to_title_screen())
        #clear button img
        self.clear_btn_img = ImageTk.PhotoImage(Image.open("assets/images/clear_button.png").resize((120, 80)))
        self.clear_button = self.canvas.create_image(760, 40, image=self.clear_btn_img, anchor="center")
        self.canvas.tag_bind(self.clear_button, "<Button-1>", lambda e: self.clear_numbers())
        #lever hitbox
        rect_id = self.canvas.create_rectangle(700, 180, 750, 330, outline="", fill="", width=0)
        self.canvas.tag_bind(rect_id, "<Button-1>", self.pull_lever)
        self.goodluck_item = None  #goodluck message
        #'press the lever' button
        self.show_press_lever_prompt()
        self.lever_enabled = True  #to enable

    def clear_numbers(self):
        #increment spam count
        self.clear_spam_count += 1
        #cancel previous spam timer
        if self.clear_spam_reset_job:
            self.root.after_cancel(self.clear_spam_reset_job)
        self.clear_spam_reset_job = self.root.after(5000, self.reset_clear_spam_count)
        #show annoyed overlay and sound
        if self.clear_spam_count >= 3 and not self.annoyed_overlay:
            self.annoyed_overlay = self.canvas.create_image(0, 0, image=self.annoyed_img, anchor="nw")
            self.annoyed_sound.play()
            self.root.after(2000, self.remove_annoyed_overlay)  #show for 2secs
        #clear slot numbers
        for text_group in self.slot_texts:
            for text_id in text_group:
                self.canvas.itemconfig(text_id, text="--")
        #removes 'goodluck' message
        if self.goodluck_item:
            self.canvas.delete(self.goodluck_item)
            self.goodluck_item = None
        #reset lever prompt
        self.show_press_lever_prompt()
        self.lever_enabled = True

    def animate_gif(self):
        if hasattr(self, "slot_frames") and self.slot_frames:
            self.current_frame = (self.current_frame + 1) % len(self.slot_frames)
            self.canvas.itemconfig(self.slot_bg_item, image=self.slot_frames[self.current_frame])
            self.root.after(100, self.animate_gif)  #can adjust delay speed

    def roll_numbers(self, final_numbers):
        #start roll sound once
        if hasattr(self, 'roll_channel') and self.roll_channel:
            self.roll_channel.stop()  #stops any previous roll if running
        self.roll_channel = self.roll_sound.play(-1)
        def roll_single(index, delay):
            count = 0
            def update():
                nonlocal count
                if count < 20:
                    rand_num = random.randint(1, 58)
                    for text_id in self.slot_texts[index]:
                        self.canvas.itemconfig(text_id, text=str(rand_num))
                    count += 1
                    self.root.after(40 + delay, update)
                else:
                    for text_id in self.slot_texts[index]:
                        self.canvas.itemconfig(text_id, text=str(final_numbers[index]))
                    if index == 5:  #last number
                        if self.roll_channel:
                            self.roll_channel.fadeout(1000) #fade out rolling sound
                        self.ding_sound.play() #chime
                        self.show_goodluck() #shows 'good luck'

            update()
        for i in range(6):
            self.root.after(i * 200, lambda idx=i: roll_single(idx, i * 10))

    def show_goodluck(self):
        if self.goodluck_item:
            self.canvas.delete(self.goodluck_item)
        self.goodluck_item = self.canvas.create_image(
            400, 560, image=self.goodluck_img, anchor="center"
        )

    def show_press_lever_prompt(self):
        #cancel any existing blinking loop
        if hasattr(self, 'blink_job') and self.blink_job:
            self.root.after_cancel(self.blink_job)
            self.blink_job = None
        #delete old prompt
        if hasattr(self, 'lever_prompt_item') and self.lever_prompt_item:
            self.canvas.delete(self.lever_prompt_item)
        self.lever_prompt_item = self.canvas.create_image(
            400, 560, image=self.press_lever_img, anchor="center"
        )
        self.blink_visible = True
        self.blink_prompt()  #starts new blinking loop

    def blink_prompt(self):
        #exit if prompt is not there
        if not hasattr(self, 'lever_prompt_item') or self.lever_prompt_item is None:
            return
        try:
            state = "hidden" if self.blink_visible else "normal"
            self.canvas.itemconfig(self.lever_prompt_item, state=state)
            self.blink_visible = not self.blink_visible
            self.blink_job = self.root.after(500, self.blink_prompt)
        except tk.TclError:
            self.blink_job = None

    def reset_clear_spam_count(self):
        self.clear_spam_count = 0
        self.clear_spam_reset_job = None
    def remove_annoyed_overlay(self):
        if self.annoyed_overlay:
            self.canvas.delete(self.annoyed_overlay)
            self.annoyed_overlay = None

    def show_devs_screen(self):
        self.canvas.delete("all")
        #background setup
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)
        self.bg_photo = ImageTk.PhotoImage(blended)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        #devs info img
        self.dev_image = ImageTk.PhotoImage(Image.open("assets/images/dev_info.png").resize((800, 600)))
        self.canvas.create_image(400, 300, image=self.dev_image, anchor="center")
        #back button
        if not hasattr(self, "back_btn_img"):
            self.back_btn_img = ImageTk.PhotoImage(Image.open("assets/images/back_button.png").resize((120, 80)))
        self.back_button = self.canvas.create_image(50, 40, image=self.back_btn_img, anchor="center")
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda e: self.return_to_title_screen())
        #music credits
        self.show_music_credit()

    def show_title_screen(self):
        self.canvas.delete("all")
        #bg stuff
        bg = Image.open("assets/images/background.jpg").resize((800, 600)).convert("RGBA")
        black_bg = Image.new("RGBA", bg.size, (0, 0, 0, 255))
        blended = Image.blend(black_bg, bg, alpha=0.75)
        self.bg_photo = ImageTk.PhotoImage(blended)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        #title img
        self.canvas.create_image(400, 180, image=self.title_image, anchor="center")
        #predict button
        self.predict_btn = self.canvas.create_image(400, 400, image=self.lp_button_img, anchor="center")
    
#run
if __name__ == "__main__":
    threading.Thread(target=play_music, daemon=True).start()
    root = tk.Tk()
    app = LottoApp(root)
    root.mainloop()