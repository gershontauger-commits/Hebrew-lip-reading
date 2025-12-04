# Hebrew Lip Reading Application

קריאת שפתיים בעברית

A Python-based application for recording, managing, and labeling video segments for Hebrew lip reading research and machine learning.

## Features

- **Video Recording & Management**: Record and import video files for lip reading analysis
- **Segment Management**: Create, edit, and organize video segments with Hebrew labels
- **RTL Hebrew Support**: Full right-to-left text support for Hebrew labels and interface
- **ML Dataset Export**: Export labeled segments in JSON format for machine learning training
- **User-Friendly GUI**: Intuitive graphical interface built with Tkinter

## Installation

### Prerequisites

- Python 3.9 or higher
- Tkinter (usually included with Python)
- Webcam (optional, for recording)

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

## Usage

### Running the Application

```bash
python main.py
```

With a custom data directory:
```bash
python main.py --data-dir /path/to/data
```

### Application Features

#### Segment Management
- Create new segments from video files
- Label segments with Hebrew text and transliteration
- Assign speaker IDs for multi-speaker datasets
- Add notes and metadata to segments

#### Video Operations
- Import existing video files (.mp4, .avi, .mov, .mkv)
- Record new videos directly from webcam
- Extract and save video segments

#### ML Export
- Export all labeled segments to JSON format
- Output includes video paths, frame ranges, labels, and speaker information

## Project Structure

```
Hebrew-lip-reading/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── src/
│   └── hebrew_lip_reading/
│       ├── __init__.py              # Package initialization
│       ├── gui.py                   # GUI components with RTL support
│       ├── segment.py               # Segment data management
│       └── video_handler.py         # Video recording and processing
├── tests/
│   ├── __init__.py
│   ├── test_segment.py              # Segment module tests
│   └── test_video_handler.py        # Video handler tests
└── data/
    ├── segments/                    # Segment metadata storage
    └── videos/                      # Recorded video files
```

## Development

### Running Tests

```bash
pip install pytest
pytest tests/
```

With coverage:
```bash
pytest tests/ --cov=src/hebrew_lip_reading
```

### Code Style

The project follows PEP 8 style guidelines.

## Research Applications

This application is designed to facilitate:
- Creation of Hebrew lip reading datasets
- Training visual speech recognition models
- Research with diverse speaker populations
- Aphasia patient communication assistance

## Future Extensions

- ML model integration for real-time lip reading
- Audio transcription comparison
- Multi-language support
- Cloud storage integration

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
