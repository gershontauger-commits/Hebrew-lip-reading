#!/usr/bin/env python3
"""
Hebrew Lip Reading Application

A Python-based application for recording, managing, and labeling video segments
for Hebrew lip reading research and machine learning.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from gui.main_window import MainWindow


def main():
    """Main entry point for the Hebrew Lip Reading application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Hebrew Lip Reading")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hebrew Lip Reading Research")

    # Set RTL layout direction for Hebrew support
    app.setLayoutDirection(Qt.RightToLeft)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
