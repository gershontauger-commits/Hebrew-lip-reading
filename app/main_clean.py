import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import numpy as np

class LipReadingApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Hebrew Lip Reading')
        self.root.geometry('900x700')
        self.recording = False
        self.out = None
        self.dataset_dir = 'dataset_samples'
        if not os.path.exists(self.dataset_dir):
            os.makedirs(self.dataset_dir)
        self.video_label = tk.Label(root)
        self.video_label.pack(pady=10)
        self.text_label = tk.Label(root, text='Recognized Hebrew Text: ', font=('Arial', 16), anchor='w', justify='left')
        self.text_label.pack(pady=10, fill='x')
        self.segment_entry = tk.Entry(root, font=('Arial', 14), width=40, justify='left')
        self.segment_entry.pack(pady=5)
        self.add_segment_button = tk.Button(root, text='Add Hebrew Segment', command=self.add_segment)
        self.add_segment_button.pack(pady=5)
        self.segment_listbox = tk.Listbox(root, font=('Arial', 14), width=40, height=6, justify='left')
        self.segment_listbox.pack(pady=5)
        self.start_button = tk.Button(root, text='Start Camera', command=self.start_camera)
        self.start_button.pack(pady=10)
        self.record_button = tk.Button(root, text='Start Recording', command=self.toggle_recording)
        self.record_button.pack(pady=10)
        self.refresh_recordings_button = tk.Button(root, text='Refresh Recordings', command=self.refresh_recordings)
        self.refresh_recordings_button.pack(pady=5)
        self.recordings_listbox = tk.Listbox(root, font=('Arial', 12), width=60, height=8, justify='left')
        self.recordings_listbox.pack(pady=5)
        self.play_button = tk.Button(root, text='Play Selected', command=self.play_selected)
        self.play_button.pack(pady=2)
        self.delete_button = tk.Button(root, text='Delete Selected', command=self.delete_selected)
        self.delete_button.pack(pady=2)
        self.edit_label_button = tk.Button(root, text='Edit Label', command=self.edit_label)
        self.edit_label_button.pack(pady=2)
        self.rerecord_button = tk.Button(root, text='Re-record Selected', command=self.rerecord_selected)
        self.rerecord_button.pack(pady=2)
        self.cap = None
        self.update_job = None
        self.hebrew_segments = []
        self.model = self.load_lip_reading_model()
        self.refresh_recordings()

    def add_segment(self):
        segment = self.segment_entry.get().strip()
        if segment:
            self.hebrew_segments.append(segment)
            self.segment_listbox.insert(tk.END, segment)
            self.segment_entry.delete(0, tk.END)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def toggle_recording(self):
        if not self.recording:
            label = self.segment_entry.get().strip()
            if not label:
                messagebox.showerror('Error', 'Please enter a Hebrew label before recording.')
                return
            import time
            timestamp = int(time.time())
            video_path = os.path.join(self.dataset_dir, f'{timestamp}.avi')
            self.out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
            with open(os.path.join(self.dataset_dir, f'{timestamp}.txt'), 'w', encoding='utf-8') as f:
                f.write(label)
            self.recording = True
            self.record_button.config(text='Stop Recording')
        else:
            self.recording = False
            if self.out:
                self.out.release()
                self.out = None
            self.record_button.config(text='Start Recording')

    def refresh_recordings(self):
        self.recordings_listbox.delete(0, tk.END)
        for fname in os.listdir(self.dataset_dir):
            if fname.endswith('.avi'):
                base = fname[:-4]
                label_path = os.path.join(self.dataset_dir, f'{base}.txt')
                label = ''
                if os.path.exists(label_path):
                    with open(label_path, encoding='utf-8') as f:
                        label = f.read().strip()
                self.recordings_listbox.insert(tk.END, f'{base}: {label}')

    def play_selected(self):
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror('Error', 'No recording selected.')
            return
        item = self.recordings_listbox.get(selection[0])
        base = item.split(':')[0]
        video_path = os.path.join(self.dataset_dir, f'{base}.avi')
        cap = cv2.VideoCapture(video_path)
        playback_window = tk.Toplevel(self.root)
        playback_window.title('Playback')
        playback_label = tk.Label(playback_window)
        playback_label.pack()
        def show_frame():
            global playback_imgtk
            ret, frame = cap.read()
            if not ret:
                cap.release()
                playback_window.destroy()
                return
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            playback_imgtk = ImageTk.PhotoImage(image=img)
            playback_label.configure(image=playback_imgtk)
            playback_window.after(30, show_frame)
        show_frame()

    def delete_selected(self):
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror('Error', 'No recording selected.')
            return
        item = self.recordings_listbox.get(selection[0])
        base = item.split(':')[0]
        video_path = os.path.join(self.dataset_dir, f'{base}.avi')
        label_path = os.path.join(self.dataset_dir, f'{base}.txt')
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(label_path):
            os.remove(label_path)
        self.refresh_recordings()

    def edit_label(self):
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror('Error', 'No recording selected.')
            return
        item = self.recordings_listbox.get(selection[0])
        base = item.split(':')[0]
        label_path = os.path.join(self.dataset_dir, f'{base}.txt')
        new_label = simpledialog.askstring('Edit Label', 'Enter new Hebrew label (LTR):')
        if new_label is not None:
            with open(label_path, 'w', encoding='utf-8') as f:
                f.write(new_label)
            self.refresh_recordings()

    def rerecord_selected(self):
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror('Error', 'No recording selected.')
            return
        item = self.recordings_listbox.get(selection[0])
        base = item.split(':')[0]
        label_path = os.path.join(self.dataset_dir, f'{base}.txt')
        video_path = os.path.join(self.dataset_dir, f'{base}.avi')
        current_label = ''
        if os.path.exists(label_path):
            with open(label_path, encoding='utf-8') as f:
                current_label = f.read().strip()
        new_label = simpledialog.askstring('Re-record', 'Enter new Hebrew label (LTR):', initialvalue=current_label)
        if new_label is None:
            return
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(label_path):
            os.remove(label_path)
        self.segment_entry.delete(0, tk.END)
        self.segment_entry.insert(0, new_label)
        self.toggle_recording()

    def load_lip_reading_model(self):
        try:
            import keras
            model = keras.models.load_model('model.h5')
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def update_frame(self):
        global main_imgtk
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if ret:
            if self.recording and self.out:
                self.out.write(frame)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            main_imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.configure(image=main_imgtk)
            recognized_text = self.lip_reading_model(frame)
            best_match = self.match_segment(recognized_text)
            self.text_label.config(text=f'Recognized Hebrew Text: {recognized_text}\nBest Match: {best_match}')
        self.update_job = self.root.after(30, self.update_frame)

    def match_segment(self, recognized_text):
        if not self.hebrew_segments:
            return "(אין קטעים להשוואה)"
        matches = [(segment, self.simple_similarity(recognized_text, segment)) for segment in self.hebrew_segments]
        matches.sort(key=lambda x: x[1], reverse=True)
        best_segment, score = matches[0]
        return best_segment if score > 0 else "(לא נמצאה התאמה)"

    def simple_similarity(self, a, b):
        return sum(1 for x, y in zip(a, b) if x == y)

    def lip_reading_model(self, frame):
        if self.model is None:
            return "(הטקסט המזוהה יוצג כאן)"
        input_img = cv2.resize(frame, (224, 224))
        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        input_img = input_img / 255.0
        input_img = np.expand_dims(input_img, axis=(0, -1))
        try:
            preds = self.model.predict(input_img)
            text = "(תוצאת המודל כאן)"
            return text
        except Exception as e:
            print(f"Model inference error: {e}")
            return "(שגיאת מודל)"

    def lip_reading_stub(self, frame):
        return self.lip_reading_model(frame)

    def on_closing(self):
        if self.cap:
            self.cap.release()
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LipReadingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
