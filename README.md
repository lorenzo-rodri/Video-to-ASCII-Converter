# Video to ASCII Converter

A Python based app that converts videos into ASCII art. Built with CustomTkinter, OpenCV, and Pillow.  

---

## Features
- Select a video file (MP4) as source
- Convert video frames into ASCII art
- Preview the video before and after conversion
- Save the converted ASCII video to a chosen folder
- Simple and intuitive GUI

---

## Installation

1. Clone this repository.
2. Install Python if you don’t have it.
3. Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Run the app:

```bash
python main.py
```

2. Use the GUI to:
   - Select a source video
   - Select an output folder
   - Click Convert to ASCII
3. Preview the original video in the right panel.  
4. The converted ASCII video will be saved in the selected output folder as `output_ascii.mp4`.
5. Preview the converted ASCII video in the right panel.

---

## Notes
- Max supported video length: 1000 frames
- ASCII conversion may take a few minutes depending on video length

---

## Potential Updates
- Retain sound after conversion
- Allow other video formats
- Create more efficient algorithm to allow for faster conversion time
- Allow the user to set the size of the ASCII characters in the converted video
