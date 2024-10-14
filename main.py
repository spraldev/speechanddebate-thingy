import os
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time
from playsound import playsound
import random
import threading
from deepface import DeepFace

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GUI App")
        self.last_emotion_sound_time = 0 
        self.geometry("1280x720")
        self.minsize(800, 600) 
        self.configure(bg='#2b2b2b') 

        self.is_dark_mode = True
        self.stopwatch_running = False
        self.elapsed_time = 0
        self.camera_index = 0

        self.is_running = False
        self.thread = None  

        self.create_widgets()
        self.setup_camera()
        self.after(0, self.update_camera_frame) 
        self.update_stopwatch()

    def create_widgets(self):
 
        self.style = ttk.Style(self)
        self.set_theme()

        
        self.rowconfigure(0, weight=1)  
        self.rowconfigure(1, weight=1)  
        self.rowconfigure(2, weight=1)  
        self.columnconfigure(0, weight=1)

        
        self.top_frame = ttk.Frame(self)
        self.top_frame.grid(row=0, column=0, sticky='nsew')

        self.camera_label = ttk.Label(self.top_frame)
        self.camera_label.pack(expand=True)

        
        self.middle_frame = ttk.Frame(self)
        self.middle_frame.grid(row=1, column=0, sticky='nsew')

        self.text_label = ttk.Label(
            self.middle_frame, text="hi", font=("Arial", 36), anchor='center'
        )
        self.text_label.pack(expand=True)

        
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=2, column=0, sticky='nsew')

        
        self.stopwatch_label = ttk.Label(
            self.bottom_frame, text="00:00:00", font=("Arial", 72)
        )
        self.stopwatch_label.pack(expand=True, pady=10)

        
        self.buttons_frame = ttk.Frame(self.bottom_frame)
        self.buttons_frame.pack(pady=10)

        
        for i in range(4):
            self.buttons_frame.columnconfigure(i, weight=1)

        button_style = {'padx': 5, 'pady': 5, 'ipadx': 10, 'ipady': 5, 'sticky': 'ew'}

        self.start_button = ttk.Button(
            self.buttons_frame, text="Start/Stop", command=self.toggle_stopwatch
        )
        self.start_button.grid(row=0, column=0, **button_style)

        self.reset_button = ttk.Button(
            self.buttons_frame, text="Reset Timer", command=self.reset_stopwatch
        )
        self.reset_button.grid(row=0, column=1, **button_style)

        
        self.theme_button = ttk.Button(
            self.buttons_frame, text="Toggle Light/Dark Mode", command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=2, **button_style)

        
        self.source_button = ttk.Button(
            self.buttons_frame, text="Switch Video Source", command=self.switch_camera
        )
        self.source_button.grid(row=0, column=3, **button_style)

    def set_theme(self):
        if self.is_dark_mode:
            self.style.theme_use('clam')
            self.style.configure(
                '.', background='#2b2b2b', foreground='white', fieldbackground='#2b2b2b'
            )
            self.configure(bg='#2b2b2b')
            
            self.style.configure('TButton', background='#444', foreground='white', font=('Arial', 14))
            self.style.map('TButton',
                           background=[('active', '#666')],
                           foreground=[('active', 'white')])
        else:
            self.style.theme_use('clam')
            self.style.configure(
                '.', background='white', foreground='black', fieldbackground='white'
            )
            self.configure(bg='white')
            
            self.style.configure('TButton', background='#ddd', foreground='black', font=('Arial', 14))
            self.style.map('TButton',
                           background=[('active', '#bbb')],
                           foreground=[('active', 'black')])

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.set_theme()

    def setup_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  

    def switch_camera(self):
        self.camera_index = (self.camera_index + 1) % 2  
        self.cap.release()
        self.setup_camera()

    def update_camera_frame(self):
        ret, frame = self.cap.read()
        if ret:
            
            original_frame = frame.copy()

                        
            if self.is_running:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

                for (x, y, w, h) in faces:
                    
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (89, 2, 236), 2)

                    
                    face_img = original_frame[y:y+h, x:x+w]

                    try:
                        
                        analyze = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)

                        
                        if isinstance(analyze, list):
                            analyze = analyze[0]  

                        
                        emotion = analyze['dominant_emotion']

                        current_time = time.time()
                        if emotion == "neutral":
                            if current_time - self.last_emotion_sound_time >= 5:  
                                playsound("more_emotion.mp3")
                                self.after(0, lambda: self.text_label.config(text="MORE EMOTION!!"))
                                self.last_emotion_sound_time = current_time  

                        
                        cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (224, 77, 176), 2)

                        print(emotion)
                    except Exception as e:
                        print('Error analyzing face:', e)



            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            
            img = Image.fromarray(frame_rgb)

            
            label_width = self.camera_label.winfo_width()
            label_height = self.camera_label.winfo_height()

            if label_width > 1 and label_height > 1:
                
                img.thumbnail((label_width, label_height), Image.LANCZOS)

                
                bg = Image.new('RGB', (label_width, label_height), 'black')

                
                img_x = (label_width - img.width) // 2
                img_y = (label_height - img.height) // 2
                bg.paste(img, (img_x, img_y))

                imgtk = ImageTk.PhotoImage(image=bg)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
        self.after(30, self.update_camera_frame)  

    def toggle_stopwatch(self):
        self.stopwatch_running = not self.stopwatch_running
        if self.stopwatch_running:
            self.stopwatch_start_time = time.time() - self.elapsed_time
            if not self.is_running:
                self.is_running = True
                self.thread = threading.Thread(target=self.start_stuff)
                self.thread.start()
        else:
            self.is_running = False
            if self.thread is not None:
                self.thread.join()

    def start_stuff(self):
        while self.is_running:
            time_to_s
            for _ in range(int(time_to_sleep * 10)):  
                if not self.is_running:
                    return
                time.sleep(0.1)
            if not self.is_running:
                return
            playsound('check_eyes.mp3')
            
            self.after(0, lambda: self.text_label.config(text="CHECK EYES!!"))

            time_to_sleep = random.randint(3, 7)
            for _ in range(int(time_to_sleep * 10)):
                if not self.is_running:
                    return
                time.sleep(0.1)
            if not self.is_running:
                return
            playsound('check_posture.mp3')
            
            self.after(0, lambda: self.text_label.config(text="CHECK POSTURE!!"))

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.elapsed_time = 0
        self.stopwatch_label.config(text="00:00:00")
        self.is_running = False
        if self.thread is not None:
            self.thread.join()
        
        self.text_label.config(text="hi")

    def update_stopwatch(self):
        if self.stopwatch_running:
            self.elapsed_time = time.time() - self.stopwatch_start_time
            elapsed_time_str = time.strftime(
                '%H:%M:%S', time.gmtime(self.elapsed_time)
            )
            self.stopwatch_label.config(text=elapsed_time_str)
        self.after(100, self.update_stopwatch)

    def on_closing(self):
        self.cap.release()
        self.is_running = False
        if self.thread is not None:
            self.thread.join()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    
