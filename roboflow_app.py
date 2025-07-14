import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import threading
import pyttsx3
from inference_sdk import InferenceHTTPClient

ROBOFLOW_API_KEY = "iEfFnao2ER31Qs83nPcV"
ROBOFLOW_MODEL_ENDPOINT = "filament-idqwc/3"
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

SHAPE_TO_DIRECTION = {
    "x": "Continue right",
    "ucgen": "Continue left",
    "daire": "Go straight",
    "besgen": "Turn back"
}

class YonuBulApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cave Emergency Guidance System")
        self.root.geometry("850x700")
        self.root.state('zoomed')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.bg_gif = Image.open("C:\\Users\\Yıldız\\RoboflowApp\\magara.gif")
        self.bg_frames = []
        try:
            while True:
                frame = self.bg_gif.copy().resize((screen_width, screen_height))
                self.bg_frames.append(ImageTk.PhotoImage(frame))
                self.bg_gif.seek(len(self.bg_frames))
        except EOFError:
            pass

        self.bg_canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_bg_image = self.bg_canvas.create_image(0, 0, image=self.bg_frames[0], anchor="nw")

        def animate_bg(frame=0):
            self.bg_canvas.itemconfig(self.bg_bg_image, image=self.bg_frames[frame])
            self.root.after(100, animate_bg, (frame + 1) % len(self.bg_frames))
        animate_bg()

        self.bg_canvas.create_rectangle(screen_width//2-300, 20, screen_width//2+300, 90, fill="#000000", stipple="gray25", outline="")
        self.bg_canvas.create_text(screen_width//2+2, 72, text="Cave Emergency Guidance System ", font=("Comic Sans MS", 28, "bold"), fill="#000")
        self.bg_canvas.create_text(screen_width//2, 70, text=" Cave Emergency Guidance System ", font=("Comic Sans MS", 28, "bold"), fill="#ffe082")

        self.bat_img = ImageTk.PhotoImage(Image.open("C:\\Users\\Yıldız\\RoboflowApp\\yarasa.png").resize((50, 50)))
        self.bg_canvas.create_image(screen_width-80, 30, image=self.bat_img, anchor="nw")

        video_width, video_height = 700, 500
        self.video_label = tk.Label(root, bg="#2d2d2d", bd=3, relief="ridge")
        self.video_window = self.bg_canvas.create_window(
            (screen_width-video_width)//2, 120, anchor="nw",
            window=self.video_label, width=video_width, height=video_height
        )

        self.status_icon = ImageTk.PhotoImage(Image.open("status_icon.png").resize((24, 24)))
        self.status_label = tk.Label(
            root, text=" Status: Waiting...", image=self.status_icon, compound="left",
            font=("Comic Sans MS", 16, "bold"), bg="#263238", fg="#ffd600", bd=2, relief="groove", padx=10, pady=10
        )
        self.status_window = self.bg_canvas.create_window(
            screen_width//2, 650, anchor="center", window=self.status_label
        )

        def on_enter(e):
            e.widget['background'] = '#6d4c41'
        def on_leave(e):
            e.widget['background'] = '#3e2723'

        self.start_button = tk.Button(root, text="▶ Start Camera", command=self.start_camera, bg="#3e2723", fg="#ffe082", font=("Comic Sans MS", 14, "bold"), bd=3, relief="raised", activebackground="#6d4c41")
        self.start_button.bind("<Enter>", on_enter)
        self.start_button.bind("<Leave>", on_leave)
        self.bg_canvas.create_window(screen_width//2-100, 700, anchor="center", window=self.start_button)

        self.stop_button = tk.Button(root, text="■ Stop Camera", command=self.stop_camera, state=tk.DISABLED, bg="#b71c1c", fg="#fffde7", font=("Comic Sans MS", 14, "bold"), bd=3, relief="raised", activebackground="#e57373")
        self.bg_canvas.create_window(screen_width//2+100, 700, anchor="center", window=self.stop_button)

        self.engine = pyttsx3.init()
        self.set_english_voice()
        self.cap = None
        self.running = False
        self.last_direction = None

        self.bg_canvas.create_rectangle(0, 0, 850, 700, fill="#000000", stipple="gray25", outline="")

    def set_english_voice(self):
        for voice in self.engine.getProperty('voices'):
            if "en" in voice.languages or "English" in voice.name or "English" in voice.id:
                self.engine.setProperty('voice', voice.id)
                break

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Hata", "Kamera açılamadı!")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.update_frame, daemon=True).start()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Camera stopped.")

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            pil_img_resized = pil_img.resize((416, 416))
            pil_img_resized.save("temp.jpg")
            try:
                results = CLIENT.infer("temp.jpg", model_id=ROBOFLOW_MODEL_ENDPOINT)
                print("Roboflow API yanıtı:", results)
                direction = self.get_direction_from_predictions(results)
                self.status_label.config(text=f"Status: {direction}")
                if direction and direction != self.last_direction:
                    self.say_direction(direction)
                    self.last_direction = direction
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")
            tk_img = ImageTk.PhotoImage(pil_img.resize((500, 500)))
            self.video_label.imgtk = tk_img
            self.video_label.config(image=tk_img)
        if self.cap:
            self.cap.release()

    def get_direction_from_predictions(self, predictions):
        preds = predictions.get("predictions", [])
        if not preds:
            return "No shape detected"
        best = max(preds, key=lambda x: x.get("confidence", 0))
        label = best.get("class", "").lower()
        return SHAPE_TO_DIRECTION.get(label, f"Unknown shape: {label}")

    def say_direction(self, direction):
        self.engine.say(direction)
        self.engine.runAndWait()

if __name__ == "__main__":
    root = tk.Tk()
    app = YonuBulApp(root)
    root.mainloop()