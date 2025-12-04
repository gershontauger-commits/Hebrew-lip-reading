"""
Main Window for Hebrew Lip Reading Application

This module provides the main application window with Hebrew RTL support,
video management, and segment labeling capabilities.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QSplitter, QStatusBar, QMenuBar,
    QAction, QToolBar, QFrame, QSpinBox, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont

from core.video_manager import VideoManager
from core.segment_manager import SegmentManager, Segment


class MainWindow(QMainWindow):
    """Main application window with Hebrew RTL support."""

    def __init__(self):
        super().__init__()
        self.video_manager = VideoManager()
        self.segment_manager = SegmentManager()
        self.current_video_path = None

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("קורא שפתיים עברי - Hebrew Lip Reading")
        self.setMinimumSize(1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Video display and controls
        left_panel = self.create_video_panel()
        splitter.addWidget(left_panel)

        # Right panel - Segment management
        right_panel = self.create_segment_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([700, 500])

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("מוכן לעבודה - Ready to work")

        # Timer for video playback
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_video_frame)

    def create_menu_bar(self):
        """Create the menu bar with Hebrew labels."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("קובץ - File")

        open_action = QAction("פתח וידאו - Open Video", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_video)
        file_menu.addAction(open_action)

        save_action = QAction("שמור סגמנטים - Save Segments", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_segments)
        file_menu.addAction(save_action)

        load_action = QAction("טען סגמנטים - Load Segments", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.load_segments)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_action = QAction("ייצוא למערך נתונים - Export Dataset", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_dataset)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("יציאה - Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Recording menu
        record_menu = menubar.addMenu("הקלטה - Recording")

        start_record_action = QAction("התחל הקלטה - Start Recording", self)
        start_record_action.setShortcut("Ctrl+R")
        start_record_action.triggered.connect(self.start_recording)
        record_menu.addAction(start_record_action)

        stop_record_action = QAction("עצור הקלטה - Stop Recording", self)
        stop_record_action.setShortcut("Ctrl+T")
        stop_record_action.triggered.connect(self.stop_recording)
        record_menu.addAction(stop_record_action)

        # Help menu
        help_menu = menubar.addMenu("עזרה - Help")

        about_action = QAction("אודות - About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar with common actions."""
        toolbar = QToolBar("כלים ראשיים - Main Tools")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open video button
        self.open_btn = QPushButton("📂 פתח וידאו")
        self.open_btn.clicked.connect(self.open_video)
        toolbar.addWidget(self.open_btn)

        toolbar.addSeparator()

        # Recording buttons
        self.record_btn = QPushButton("🔴 הקלט")
        self.record_btn.clicked.connect(self.start_recording)
        toolbar.addWidget(self.record_btn)

        self.stop_record_btn = QPushButton("⬛ עצור")
        self.stop_record_btn.clicked.connect(self.stop_recording)
        self.stop_record_btn.setEnabled(False)
        toolbar.addWidget(self.stop_record_btn)

        toolbar.addSeparator()

        # Playback controls
        self.play_btn = QPushButton("▶️ נגן")
        self.play_btn.clicked.connect(self.toggle_playback)
        toolbar.addWidget(self.play_btn)

    def create_video_panel(self):
        """Create the video display panel."""
        panel = QGroupBox("תצוגת וידאו - Video Display")
        layout = QVBoxLayout(panel)

        # Video display label
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet(
            "background-color: #1a1a1a; border: 2px solid #333;"
        )
        self.video_label.setText("אין וידאו נטען\nNo video loaded")
        layout.addWidget(self.video_label)

        # Video controls
        controls_layout = QHBoxLayout()

        self.frame_label = QLabel("פריים: 0 / 0")
        controls_layout.addWidget(self.frame_label)

        self.time_label = QLabel("זמן: 00:00:00")
        controls_layout.addWidget(self.time_label)

        controls_layout.addStretch()

        self.prev_frame_btn = QPushButton("◀ פריים קודם")
        self.prev_frame_btn.clicked.connect(self.prev_frame)
        controls_layout.addWidget(self.prev_frame_btn)

        self.next_frame_btn = QPushButton("פריים הבא ▶")
        self.next_frame_btn.clicked.connect(self.next_frame)
        controls_layout.addWidget(self.next_frame_btn)

        layout.addLayout(controls_layout)

        # Segment marking controls
        mark_layout = QHBoxLayout()

        self.mark_start_btn = QPushButton("סמן התחלה [")
        self.mark_start_btn.clicked.connect(self.mark_segment_start)
        mark_layout.addWidget(self.mark_start_btn)

        self.mark_end_btn = QPushButton("סמן סיום ]")
        self.mark_end_btn.clicked.connect(self.mark_segment_end)
        mark_layout.addWidget(self.mark_end_btn)

        self.add_segment_btn = QPushButton("הוסף סגמנט ✓")
        self.add_segment_btn.clicked.connect(self.add_segment)
        mark_layout.addWidget(self.add_segment_btn)

        layout.addLayout(mark_layout)

        # Current segment info
        segment_info_layout = QFormLayout()

        self.start_frame_spin = QSpinBox()
        self.start_frame_spin.setMinimum(0)
        self.start_frame_spin.setMaximum(999999)
        segment_info_layout.addRow("פריים התחלה:", self.start_frame_spin)

        self.end_frame_spin = QSpinBox()
        self.end_frame_spin.setMinimum(0)
        self.end_frame_spin.setMaximum(999999)
        segment_info_layout.addRow("פריים סיום:", self.end_frame_spin)

        layout.addLayout(segment_info_layout)

        return panel

    def create_segment_panel(self):
        """Create the segment management panel."""
        panel = QGroupBox("ניהול סגמנטים - Segment Management")
        layout = QVBoxLayout(panel)

        # Segment list
        list_label = QLabel("רשימת סגמנטים - Segment List:")
        layout.addWidget(list_label)

        self.segment_list = QListWidget()
        self.segment_list.setLayoutDirection(Qt.RightToLeft)
        self.segment_list.itemClicked.connect(self.on_segment_selected)
        layout.addWidget(self.segment_list)

        # Segment details
        details_group = QGroupBox("פרטי סגמנט - Segment Details")
        details_layout = QFormLayout(details_group)

        self.segment_id_label = QLabel("")
        details_layout.addRow("מזהה סגמנט:", self.segment_id_label)

        self.hebrew_label_edit = QLineEdit()
        self.hebrew_label_edit.setLayoutDirection(Qt.RightToLeft)
        self.hebrew_label_edit.setPlaceholderText("הקלד תווית בעברית...")
        self.hebrew_label_edit.setFont(QFont("Arial", 14))
        details_layout.addRow("תווית עברית:", self.hebrew_label_edit)

        self.english_label_edit = QLineEdit()
        self.english_label_edit.setLayoutDirection(Qt.LeftToRight)
        self.english_label_edit.setPlaceholderText("Enter English label...")
        details_layout.addRow("English Label:", self.english_label_edit)

        self.phonetic_edit = QLineEdit()
        self.phonetic_edit.setPlaceholderText("תעתיק פונטי...")
        details_layout.addRow("תעתיק פונטי:", self.phonetic_edit)

        self.speaker_combo = QComboBox()
        self.speaker_combo.setEditable(True)
        self.speaker_combo.addItems(["דובר 1", "דובר 2", "דובר 3"])
        details_layout.addRow("דובר:", self.speaker_combo)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("הערות נוספות...")
        details_layout.addRow("הערות:", self.notes_edit)

        layout.addWidget(details_group)

        # Segment actions
        actions_layout = QHBoxLayout()

        self.update_segment_btn = QPushButton("עדכן סגמנט")
        self.update_segment_btn.clicked.connect(self.update_segment)
        actions_layout.addWidget(self.update_segment_btn)

        self.delete_segment_btn = QPushButton("מחק סגמנט")
        self.delete_segment_btn.clicked.connect(self.delete_segment)
        actions_layout.addWidget(self.delete_segment_btn)

        self.play_segment_btn = QPushButton("נגן סגמנט")
        self.play_segment_btn.clicked.connect(self.play_segment)
        actions_layout.addWidget(self.play_segment_btn)

        layout.addLayout(actions_layout)

        # Statistics
        stats_group = QGroupBox("סטטיסטיקות - Statistics")
        stats_layout = QFormLayout(stats_group)

        self.total_segments_label = QLabel("0")
        stats_layout.addRow("סה״כ סגמנטים:", self.total_segments_label)

        self.total_duration_label = QLabel("00:00:00")
        stats_layout.addRow("משך כולל:", self.total_duration_label)

        self.labeled_segments_label = QLabel("0")
        stats_layout.addRow("סגמנטים מתוייגים:", self.labeled_segments_label)

        layout.addWidget(stats_group)

        return panel

    def setup_connections(self):
        """Setup signal connections."""
        self.segment_manager.segment_added.connect(self.refresh_segment_list)
        self.segment_manager.segment_removed.connect(self.refresh_segment_list)
        self.segment_manager.segment_updated.connect(self.refresh_segment_list)

    # Video operations
    def open_video(self):
        """Open a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "פתח קובץ וידאו - Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)"
        )
        if file_path:
            if self.video_manager.load_video(file_path):
                self.current_video_path = file_path
                self.update_video_display()
                self.status_bar.showMessage(f"נטען: {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "שגיאה - Error",
                    "לא ניתן לפתוח את קובץ הוידאו\nCannot open video file"
                )

    def update_video_display(self):
        """Update the video display with current frame."""
        frame = self.video_manager.get_current_frame()
        if frame is not None:
            # Convert frame to QPixmap
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()
            pixmap = QPixmap.fromImage(q_img)

            # Scale to fit label
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)

            # Update frame info
            current_frame = self.video_manager.current_frame_index
            total_frames = self.video_manager.total_frames
            self.frame_label.setText(f"פריים: {current_frame} / {total_frames}")

            # Update time info
            current_time = self.video_manager.get_current_time()
            self.time_label.setText(f"זמן: {current_time}")

    def update_video_frame(self):
        """Update video frame during playback."""
        if self.video_manager.is_playing:
            self.video_manager.next_frame()
            self.update_video_display()
        else:
            self.playback_timer.stop()

    def toggle_playback(self):
        """Toggle video playback."""
        if self.video_manager.is_playing:
            self.video_manager.is_playing = False
            self.play_btn.setText("▶️ נגן")
            self.playback_timer.stop()
        else:
            self.video_manager.is_playing = True
            self.play_btn.setText("⏸️ עצור")
            fps = self.video_manager.fps or 30
            self.playback_timer.start(int(1000 / fps))

    def prev_frame(self):
        """Go to previous frame."""
        self.video_manager.prev_frame()
        self.update_video_display()

    def next_frame(self):
        """Go to next frame."""
        self.video_manager.next_frame()
        self.update_video_display()

    # Recording operations
    def start_recording(self):
        """Start video recording from camera."""
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "שמור הקלטה - Save Recording",
            "",
            "Video Files (*.mp4);;All Files (*.*)"
        )
        if save_path:
            if not save_path.endswith('.mp4'):
                save_path += '.mp4'
            if self.video_manager.start_recording(save_path):
                self.record_btn.setEnabled(False)
                self.stop_record_btn.setEnabled(True)
                self.status_bar.showMessage("מקליט... - Recording...")
                # Start timer to update preview
                self.playback_timer.start(33)  # ~30 fps
            else:
                QMessageBox.warning(
                    self,
                    "שגיאה - Error",
                    "לא ניתן להתחיל הקלטה\nCannot start recording"
                )

    def stop_recording(self):
        """Stop video recording."""
        self.video_manager.stop_recording()
        self.record_btn.setEnabled(True)
        self.stop_record_btn.setEnabled(False)
        self.playback_timer.stop()
        self.status_bar.showMessage("הקלטה הסתיימה - Recording stopped")

    # Segment operations
    def mark_segment_start(self):
        """Mark the start of a segment."""
        self.start_frame_spin.setValue(self.video_manager.current_frame_index)
        self.status_bar.showMessage("סומנה התחלת סגמנט - Segment start marked")

    def mark_segment_end(self):
        """Mark the end of a segment."""
        self.end_frame_spin.setValue(self.video_manager.current_frame_index)
        self.status_bar.showMessage("סומן סוף סגמנט - Segment end marked")

    def add_segment(self):
        """Add a new segment."""
        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()

        if end_frame <= start_frame:
            QMessageBox.warning(
                self,
                "שגיאה - Error",
                "פריים הסיום חייב להיות גדול מפריים ההתחלה\n"
                "End frame must be greater than start frame"
            )
            return

        segment = Segment(
            start_frame=start_frame,
            end_frame=end_frame,
            video_path=self.current_video_path or "",
            fps=self.video_manager.fps or 30
        )
        self.segment_manager.add_segment(segment)
        self.status_bar.showMessage("סגמנט נוסף - Segment added")

    def refresh_segment_list(self):
        """Refresh the segment list display."""
        self.segment_list.clear()
        for segment in self.segment_manager.segments:
            item_text = (
                f"[{segment.id[:8]}] "
                f"פריימים: {segment.start_frame}-{segment.end_frame} | "
                f"תווית: {segment.hebrew_label or 'ללא'}"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, segment.id)
            self.segment_list.addItem(item)

        # Update statistics
        self.total_segments_label.setText(str(len(self.segment_manager.segments)))
        labeled_count = sum(
            1 for s in self.segment_manager.segments if s.hebrew_label
        )
        self.labeled_segments_label.setText(str(labeled_count))

    def on_segment_selected(self, item):
        """Handle segment selection."""
        segment_id = item.data(Qt.UserRole)
        segment = self.segment_manager.get_segment(segment_id)
        if segment:
            self.segment_id_label.setText(segment.id)
            self.hebrew_label_edit.setText(segment.hebrew_label)
            self.english_label_edit.setText(segment.english_label)
            self.phonetic_edit.setText(segment.phonetic_transcription)
            self.notes_edit.setText(segment.notes)

            # Jump to segment start in video
            self.video_manager.seek_frame(segment.start_frame)
            self.update_video_display()

    def update_segment(self):
        """Update the selected segment."""
        segment_id = self.segment_id_label.text()
        if not segment_id:
            return

        segment = self.segment_manager.get_segment(segment_id)
        if segment:
            segment.hebrew_label = self.hebrew_label_edit.text()
            segment.english_label = self.english_label_edit.text()
            segment.phonetic_transcription = self.phonetic_edit.text()
            segment.speaker_id = self.speaker_combo.currentText()
            segment.notes = self.notes_edit.toPlainText()
            self.segment_manager.update_segment(segment)
            self.status_bar.showMessage("סגמנט עודכן - Segment updated")

    def delete_segment(self):
        """Delete the selected segment."""
        segment_id = self.segment_id_label.text()
        if not segment_id:
            return

        reply = QMessageBox.question(
            self,
            "אישור מחיקה - Confirm Delete",
            "האם אתה בטוח שברצונך למחוק סגמנט זה?\n"
            "Are you sure you want to delete this segment?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.segment_manager.remove_segment(segment_id)
            self.clear_segment_details()
            self.status_bar.showMessage("סגמנט נמחק - Segment deleted")

    def play_segment(self):
        """Play the selected segment."""
        segment_id = self.segment_id_label.text()
        if not segment_id:
            return

        segment = self.segment_manager.get_segment(segment_id)
        if segment:
            self.video_manager.seek_frame(segment.start_frame)
            # TODO: Implement segment-limited playback
            self.toggle_playback()

    def clear_segment_details(self):
        """Clear the segment details form."""
        self.segment_id_label.setText("")
        self.hebrew_label_edit.clear()
        self.english_label_edit.clear()
        self.phonetic_edit.clear()
        self.notes_edit.clear()

    # File operations
    def save_segments(self):
        """Save segments to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "שמור סגמנטים - Save Segments",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            if self.segment_manager.save_to_file(file_path):
                self.status_bar.showMessage(f"סגמנטים נשמרו: {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "שגיאה - Error",
                    "לא ניתן לשמור סגמנטים\nCannot save segments"
                )

    def load_segments(self):
        """Load segments from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "טען סגמנטים - Load Segments",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            if self.segment_manager.load_from_file(file_path):
                self.refresh_segment_list()
                self.status_bar.showMessage(f"סגמנטים נטענו: {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "שגיאה - Error",
                    "לא ניתן לטעון סגמנטים\nCannot load segments"
                )

    def export_dataset(self):
        """Export segments as ML dataset."""
        dialog = ExportDatasetDialog(self)
        if dialog.exec_():
            export_path = dialog.get_export_path()
            export_format = dialog.get_export_format()

            if export_path:
                if self.segment_manager.export_dataset(
                    export_path, export_format, self.video_manager
                ):
                    self.status_bar.showMessage(
                        f"מערך נתונים יוצא: {export_path}"
                    )
                    QMessageBox.information(
                        self,
                        "הצלחה - Success",
                        f"מערך הנתונים יוצא בהצלחה\n"
                        f"Dataset exported successfully\n\n{export_path}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "שגיאה - Error",
                        "לא ניתן לייצא מערך נתונים\nCannot export dataset"
                    )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "אודות - About",
            "<h2>קורא שפתיים עברי</h2>"
            "<h3>Hebrew Lip Reading Application</h3>"
            "<p>גרסה 1.0.0</p>"
            "<p>אפליקציה להקלטה, ניהול ותיוג קטעי וידאו "
            "למחקר קריאת שפתיים בעברית ולמידת מכונה.</p>"
            "<p>Application for recording, managing, and labeling "
            "video segments for Hebrew lip reading research "
            "and machine learning.</p>"
            "<hr>"
            "<p>מתאים למחקר עם אוכלוסיות דוברים מגוונות.</p>"
            "<p>Adaptable for research with diverse speaker populations.</p>"
        )


class ExportDatasetDialog(QDialog):
    """Dialog for exporting dataset."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ייצוא מערך נתונים - Export Dataset")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        # Export path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("בחר תיקיית יעד...")
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("עיון...")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # Export format
        format_layout = QFormLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "CSV + Video Clips",
            "JSON + Video Clips",
            "TFRecord (TensorFlow)",
            "WebDataset (PyTorch)"
        ])
        format_layout.addRow("פורמט ייצוא:", self.format_combo)
        layout.addLayout(format_layout)

        # Options
        options_group = QGroupBox("אפשרויות - Options")
        options_layout = QFormLayout(options_group)

        self.include_video_check = QPushButton("כלול קטעי וידאו")
        self.include_video_check.setCheckable(True)
        self.include_video_check.setChecked(True)
        options_layout.addRow("", self.include_video_check)

        layout.addWidget(options_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def browse_path(self):
        """Browse for export directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "בחר תיקיית יעד - Select Destination Folder"
        )
        if path:
            self.path_edit.setText(path)

    def get_export_path(self):
        """Get the export path."""
        return self.path_edit.text()

    def get_export_format(self):
        """Get the export format."""
        return self.format_combo.currentText()
