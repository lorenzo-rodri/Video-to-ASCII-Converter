from PIL import Image, ImageDraw, ImageFont, ImageTk
import cv2
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import threading
import time

# make sure that someone can just download and use without having to install libraries manyually and stuff

class VideoToASCIIApp:


    def __init__(self):
        self.file_path = None
        self.folder_path = None
        self.frame_path = None
        self.total_frames = 0
        self.frame_count = 0
        self.cap = None
        self.playing = False
        self.preview_thread = None

        # System Settings
        ctk.set_appearance_mode("System") # match system dark/light mode
        ctk.set_default_color_theme("blue") #set color theme

        # Prepare app frame
        self.app = ctk.CTk()
        self.app.geometry("800x400")
        self.app.title("Video to ASCII")

        # Create left and right frames
        self.left_frame = ctk.CTkFrame(self.app)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.left_content = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.left_content.pack(expand=True)

        self.right_frame = ctk.CTkFrame(self.app)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left Frame Widgets
        ascii_art = r"""
____   ____.__    .___               __              _____    __________________ .___.___ 
\   \ /   /|__| __| _/____  ____   _/  |_  ____     /  _  \  /   _____/\_   ___ \|   |   |
 \   Y   / |  |/ __ |/ __ \/  _ \  \   __\/  _ \   /  /_\  \ \_____  \ /    \  \/|   |   |
  \     /  |  / /_/ \  ___(  <_> )  |  | (  <_> ) /    |    \/        \\     \___|   |   |
   \___/   |__\____ |\___  >____/   |__|  \____/  \____|__  /_______  / \______  /___|___|
                   \/    \/                               \/        \/         \/          
"""
        self.title_label = ctk.CTkLabel(self.left_content, text=ascii_art, font=("Courier New", 7), justify="left")
        self.title_label.pack(pady=10)

        self.choose_file = ctk.CTkButton(self.left_content, text="Select source file", command=self.get_File) # select file button
        self.choose_file.pack(pady=10)

        self.choose_dest = ctk.CTkButton(self.left_content, text="Select output directory", command=self.get_Dest) 
        self.choose_dest.pack(pady=10)

        self.file_label = ctk.CTkLabel(self.left_content, text="Source File: ") # filepath label
        self.file_label.pack(pady=10)

        self.dest_label = ctk.CTkLabel(self.left_content, text="Output Directory: ") # output dest label
        self.dest_label.pack(pady=10)

        self.convert_video = ctk.CTkButton(
            self.left_content,
            text="Convert to ASCII",
            command=lambda: threading.Thread(target=self.convert, daemon=True).start()
        )
        self.convert_video.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self.left_content, width=400)
        self.progress.set(0)
        self.progress.pack(pady=10)

        # Right Frame Widgets
        self.video_label = ctk.CTkLabel(self.right_frame, text="No video loaded", width=400, height=300)
        self.video_label.pack(pady=10, padx=10, expand=True, fill="both")

        # Player controls
        self.controls_frame = ctk.CTkFrame(self.right_frame)
        self.controls_frame.pack(pady=10)

        self.play_btn = ctk.CTkButton(self.controls_frame, text="▶ Play", command=self.play_pause, width=100)
        self.play_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(self.controls_frame, text="⏹ Stop", command=self.stop, width=100)
        self.stop_btn.pack(side="left", padx=5)

    # Function to open file dialogue and get source directory
    def get_File(self):

        filetypes = (
            ('text files', '*.mp4'),
            ('All files', '*.*')
        )

        file_path = tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/', # Set the initial directory
            filetypes=filetypes
        )

        if file_path:

            vidcap = cv2.VideoCapture(file_path) # open the video file into interface

            if vidcap.get(cv2.CAP_PROP_FRAME_COUNT) > 1000:
                print("Error: Video too long (max 1000 frames)")
                tk.messagebox.showerror("Error", "Video too long (max 1000 frames)")
                return False
        
            self.file_path = file_path
            self.file_label.configure(text=f"Source: {os.path.basename(file_path)}")

            # Load video for preview
            self.load_video(file_path)


    # Function to open file dialogue and get destination folder
    def get_Dest(self):
    
        folder_path = tk.filedialog.askdirectory(
            title='Select Output Folder',
            initialdir=os.path.join(os.path.expanduser("~"), "Desktop") # start with desktop
        )

        if folder_path:
            self.folder_path = folder_path
            self.dest_label.configure(text=f"Source: {os.path.basename(folder_path)}")


    def load_video(self, path):

        # Halt any existing player
        self.stop()

        # Load new video
        self.cap = cv2.VideoCapture(path)

        if self.cap.isOpened():
            # Show first frame of video as preview
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to first frame
            self.video_label.configure(text="")  # Clear text
        else:
            self.video_label.configure(text="Error loading video")


    def display_frame(self, frame):
        # Convert from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit the label while maintaining aspect ratio
        height, width = frame.shape[:2]
        max_width = 400
        max_height = 300
        
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height))
        
        # Convert to ImageTk
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update label
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)


    def play_pause(self):
        if self.cap is None or not self.cap.isOpened():
            self.status_label.configure(text="Status: No video loaded")
            return
            
        if self.playing:
            self.playing = False
            self.play_btn.configure(text="▶ Play")
        else:
            self.playing = True
            self.play_btn.configure(text="⏸ Pause")
            if self.preview_thread is None or not self.preview_thread.is_alive():
                self.preview_thread = threading.Thread(target=self._play_video, daemon=True)
                self.preview_thread.start()


    def stop(self):
        self.playing = False
        self.play_btn.configure(text="▶ Play")
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # Show first frame
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


    def _play_video(self):
        while self.playing and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            
            if ret:
                self.display_frame(frame)
                time.sleep(0.033)  # about 30 fps
            else:
                # Video ended
                self.playing = False
                self.play_btn.configure(text="▶ Play")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                break


    # Function to convert video into individual frames
    def video_to_frames(self):

        vidcap = cv2.VideoCapture(self.file_path) # open the video file into interface

        if not vidcap.isOpened():
            print(f"Error: Could not open video file {self.file_path}")
            return False

        frame_count = 0

        success, image = vidcap.read()
        scale_factor_x = 0.1  # Scale by 10%
        scale_factor_y = 0.05  # Scale by 5% (vertically squished to account for ascii char height later)

        # Create frames directory if it doesnt exist
        os.makedirs("bin/frames", exist_ok=True)
        # Clear existing frames
        for f in os.listdir("bin/frames"):
            os.remove(os.path.join("bin/frames", f))

        while success:
            resized_image = cv2.resize(image, None, fx=scale_factor_x, fy=scale_factor_y)
            cv2.imwrite("bin/frames/frame%d.jpg" % frame_count, resized_image)
            success, image = vidcap.read()
            print("Read a new frame: ", success)
            frame_count += 1


    # Function to convert all frames to ASCII images
    def frames_to_ascii(self):

        # Get frame size
        frame = cv2.imread("bin/frames/frame0.jpg")
        self.total_frames = max(1, len(os.listdir("bin/frames")))

        if frame is None:
            print("Last frame reached or frames don't exist.")
        else:
            height, width, _ = frame.shape

        # Prepare to store output image of text
        try:
            fnt = ImageFont.truetype('C://Windows//Fonts//lucon.ttf', 15)
        except IOError:
            fnt = ImageFont.load_default()

        char_width = 8
        char_height = 18

        # Vars for frame/pixel looping
        ascii_chars = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
        self.frame_count = 0
        x_coor = 0
        y_coor = 0

        # Loop through each frame
        while True:
            frame_path = f"bin/frames/frame{self.frame_count}.jpg"
            
            # Check if frame exists
            if not os.path.exists(frame_path):
                print(f"Processed {self.frame_count} frames")
                break

            frame = Image.open("bin/frames/frame%d.jpg" % self.frame_count)
            output_frame = Image.new('RGB', (char_width * width, char_height * height), color = (0, 0, 0)) # create a black background
            d = ImageDraw.Draw(output_frame)

            # Loop through each pixel in the image
            for y_coor in range(height):
                for x_coor in range(width):
                    # Get RGB values
                    r, g, b = frame.getpixel((x_coor, y_coor))

                    # Get brightness value
                    h = int(r/3 + g/3 + b/3)

                    # Match brightness value to ascii char density
                    index = int((h / 255) * (len(ascii_chars) - 1))

                    # Write char to output image
                    d.text((x_coor*char_width, y_coor*char_height), ascii_chars[index], font = fnt, fill = (r, g, b))

            output_frame.save("bin/frames/frame%d.jpg" % self.frame_count)

            progress_value = self.frame_count / self.total_frames
            self.progress.set(progress_value)

            self.app.update_idletasks() # Update GUI to remain responsive and prefent freezing

            self.frame_count+=1


    # Function to compile all generated ascii frames into video format
    def frames_to_video(self):

        frame_dir = "bin/frames"
        output_video = self.folder_path + "/output_ascii.mp4"
        fps=self.fps

        # Get list of frame files
        frame_files = sorted(os.listdir(frame_dir), key=lambda x: int(x.replace('frame', '').replace('.jpg', '')))
        
        if not frame_files:
            print("No frames found!")
            return
        
        # Read first frame to get dimensions
        first_frame = cv2.imread(os.path.join(frame_dir, frame_files[0]))
        height, width, _ = first_frame.shape
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        # Write each frame to video
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            out.write(frame)
            print(f"Added {frame_file} to video")
        
        out.release()
        print(f"Video saved to {output_video}")


    # Main convert function that orchestrates everything
    def convert(self):
        
        # if source file or output dir not selected, or video is too longreturn
        if not self.file_path or not self.folder_path or self.cap is None:
            print("Error: Source file or output directory not selected")
            return
        
        self.output_video = os.path.join(self.folder_path, "output_ascii.mp4")
        self.convert_video.configure(state="disabled")
        
        vidcap = cv2.VideoCapture(self.file_path)
        self.fps = vidcap.get(cv2.CAP_PROP_FPS)
        vidcap.release()

        if self.video_to_frames() is False:
            self.convert_video.configure(state="normal")
            return
        self.frames_to_ascii()
        self.frames_to_video()

        self.convert_video.configure(state="normal")
        self.progress.set(1)

        # Load video for preview
        if self.output_video and os.path.exists(self.output_video):
            self.load_video(self.output_video)
            self.preview_label.configure(text="ASCII Output Preview")

    def run(self):
        self.app.mainloop()

# Run the app
if __name__ == '__main__':
    app = VideoToASCIIApp()
    app.run()
