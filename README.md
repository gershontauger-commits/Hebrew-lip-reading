# Hebrew Lip Reading - קורא שפתיים עברי

A Python-based application for recording, managing, and labeling video segments for Hebrew lip reading research and machine learning.

## Overview

This application provides a user-friendly GUI for:
- Recording video segments for lip reading training data
- Managing and organizing video segments
- Labeling segments with Hebrew and English text
- Exporting datasets for machine learning model training

The application is designed with full right-to-left (RTL) Hebrew language support and can be adapted for research with diverse speaker populations.

## Features

### Video Management
- Load and play video files (MP4, AVI, MOV, MKV)
- Frame-by-frame navigation
- Record new videos from camera
- Extract video clips from segments

### Segment Management
- Mark start and end points for segments
- Add labels in Hebrew and English
- Phonetic transcription support
- Speaker identification
- Notes and annotations

### Dataset Export
- Export to CSV format with video clips
- Export to JSON format for ML pipelines
- TFRecord format support (for TensorFlow)
- WebDataset format support (for PyTorch)

### Hebrew Language Support
- Full right-to-left (RTL) interface
- Hebrew text input and display
- Bilingual labels (Hebrew + English)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/gershontauger-commits/Hebrew-lip-reading.git
cd Hebrew-lip-reading
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Opening a Video
1. Click "📂 פתח וידאו" (Open Video) or use Ctrl+O
2. Select a video file
3. Use the playback controls to navigate the video

### Creating Segments
1. Navigate to the start of a speech segment
2. Click "סמן התחלה" (Mark Start) to set the start frame
3. Navigate to the end of the segment
4. Click "סמן סיום" (Mark End) to set the end frame
5. Click "הוסף סגמנט" (Add Segment) to create the segment

### Labeling Segments
1. Select a segment from the list
2. Enter the Hebrew label in the "תווית עברית" field
3. Enter the English translation in the "English Label" field
4. Add phonetic transcription if needed
5. Click "עדכן סגמנט" (Update Segment) to save

### Recording New Videos
1. Click "🔴 הקלט" (Record) to start recording
2. Choose a save location for the video
3. Click "⬛ עצור" (Stop) when finished

### Exporting Datasets
1. Go to File > Export Dataset (Ctrl+E)
2. Choose the export format
3. Select the destination folder
4. The dataset will include video clips and metadata

## Project Structure

```
Hebrew-lip-reading/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── gui/
│   ├── __init__.py
│   └── main_window.py     # Main application window
├── core/
│   ├── __init__.py
│   ├── video_manager.py   # Video handling
│   └── segment_manager.py # Segment management
└── tests/
    ├── __init__.py
    ├── test_video_manager.py
    └── test_segment_manager.py
```

## Running Tests

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m pytest tests/test_segment_manager.py
python -m pytest tests/test_video_manager.py
```

## Extending for ML Integration

The application is designed to be extensible for machine learning integration:

1. **Dataset Export**: Use the export functionality to create training datasets
2. **Model Integration**: Add model inference to the `core/` module
3. **Real-time Prediction**: Integrate predictions into the video playback

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source. Please contact the maintainers for licensing details.

## Acknowledgments

This application was created to help with lip reading research, particularly for Hebrew speakers and potentially to assist aphasia patients in communication.
