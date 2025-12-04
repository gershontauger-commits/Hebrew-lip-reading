import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import cv2
from PIL import Image, ImageTk

class HebrewSegmentApp:
	def __init__(self, root):
		self.root = root
		self.root.title('Hebrew Segment Manager')
		self.root.geometry('600x450')
		self.dataset_dir = 'dataset_samples'
		if not os.path.exists(self.dataset_dir):
			os.makedirs(self.dataset_dir)
		
		self.entry = tk.Entry(root, font=('Arial', 14), width=30, justify='right')
		self.entry.pack(pady=10)
		
		self.add_btn = tk.Button(root, text='Add Segment', command=self.add_segment)
		self.add_btn.pack(pady=5)
		
		self.listbox = tk.Listbox(root, font=('Arial', 14), width=40, height=8, justify='right')
		self.listbox.pack(pady=10)
		
		self.edit_btn = tk.Button(root, text='Edit Selected', command=self.edit_segment)
		self.edit_btn.pack(pady=2)
		
		self.delete_btn = tk.Button(root, text='Delete Selected', command=self.delete_segment)
		self.delete_btn.pack(pady=2)
		
		self.record_btn = tk.Button(root, text='Start Recording', command=self.toggle_recording)
		self.record_btn.pack(pady=10)
		
		self.status_label = tk.Label(root, text='', font=('Arial', 12), anchor='e', justify='right')
		self.status_label.pack(pady=5, fill='x')
		
		self.video_label = tk.Label(root)
		self.video_label.pack(pady=5)
		
		self.recording = False
		self.out = None
		self.cap = None
		self.update_job = None
		self.refresh_segments()
	
	def toggle_recording(self):
		if not self.recording:
			label = self.entry.get().strip()
			if not label:
				messagebox.showerror('Error', 'Enter a Hebrew label before recording.')
				return
			import time
			timestamp = int(time.time())
			video_path = os.path.join(self.dataset_dir, f'{timestamp}.avi')
			self.out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
			with open(os.path.join(self.dataset_dir, f'{timestamp}.txt'), 'w', encoding='utf-8') as f:
				f.write(label)
			self.recording = True
			self.record_btn.config(text='Stop Recording')
			self.status_label.config(text='Recording...')
			self.start_camera()
		else:
			self.recording = False
			self.record_btn.config(text='Start Recording')
			self.status_label.config(text='')
			if self.out:
				self.out.release()
				self.out = None
			if self.cap:
				self.cap.release()
				self.cap = None
			if self.update_job:
				self.root.after_cancel(self.update_job)
			self.video_label.config(image='')
	def start_camera(self):
		self.cap = cv2.VideoCapture(0)
		self.update_frame()

	def update_frame(self):
		if self.cap is None:
			return
		ret, frame = self.cap.read()
		if ret:
			if self.recording and self.out:
				self.out.write(frame)
			cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			img = Image.fromarray(cv2image)
			imgtk = ImageTk.PhotoImage(image=img)
			self.video_label.imgtk = imgtk
			self.video_label.configure(image=imgtk)
		self.update_job = self.root.after(30, self.update_frame)

	def add_segment(self):
		segment = self.entry.get().strip()
		if segment:
			import time
			timestamp = int(time.time())
			# Add RTL marker for Hebrew text
			segment_rtl = '\u202B' + segment
			with open(os.path.join(self.dataset_dir, f'{timestamp}.txt'), 'w', encoding='utf-8') as f:
				f.write(segment_rtl)
			self.entry.delete(0, tk.END)
			self.refresh_segments()

	def refresh_segments(self):
		self.listbox.delete(0, tk.END)
		for fname in os.listdir(self.dataset_dir):
			if fname.endswith('.txt'):
				with open(os.path.join(self.dataset_dir, fname), encoding='utf-8') as f:
					label = f.read().strip()
				# Display RTL
				self.listbox.insert(tk.END, f'{fname[:-4]}: {label}')

	def edit_segment(self):
		selection = self.listbox.curselection()
		if not selection:
			messagebox.showerror('Error', 'No segment selected.')
			return
		item = self.listbox.get(selection[0])
		base = item.split(':')[0]
		label_path = os.path.join(self.dataset_dir, f'{base}.txt')
		with open(label_path, encoding='utf-8') as f:
			current_label = f.read().strip()
		new_label = simpledialog.askstring('Edit Segment', 'Enter new Hebrew label (RTL):', initialvalue=current_label)
		if new_label is not None:
			label_rtl = '\u202B' + new_label
			with open(label_path, 'w', encoding='utf-8') as f:
				f.write(label_rtl)
			self.status_label.config(text='...הקטע עודכן', fg='green')
			self.refresh_segments()

	def delete_segment(self):
		selection = self.listbox.curselection()
		if not selection:
			messagebox.showerror('Error', 'No segment selected.')
			return
		item = self.listbox.get(selection[0])
		base = item.split(':')[0]
		label_path = os.path.join(self.dataset_dir, f'{base}.txt')
		if os.path.exists(label_path):
			os.remove(label_path)
		self.refresh_segments()

	def on_closing(self):
		if self.cap:
			self.cap.release()
		if self.update_job:
			self.root.after_cancel(self.update_job)
		self.root.destroy()

def main():
	root = tk.Tk()
	app = HebrewSegmentApp(root)
	root.protocol("WM_DELETE_WINDOW", app.on_closing)
	root.mainloop()

if __name__ == '__main__':
	main()
