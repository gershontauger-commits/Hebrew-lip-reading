"""Command-line interface for the Hebrew Lip Reading application."""

import argparse
import os
import sys


def main():
    """Run the Hebrew Lip Reading application."""
    parser = argparse.ArgumentParser(
        description="Hebrew Lip Reading Application - קריאת שפתיים בעברית",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hebrew-lip-reading                    # Run with default data directory
  hebrew-lip-reading --data-dir mydata  # Run with custom data directory
        """,
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory for storing data files (default: data)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )

    args = parser.parse_args()

    if args.version:
        from hebrew_lip_reading import __version__

        print(f"Hebrew Lip Reading Application v{__version__}")
        return

    # Create data directory if it doesn't exist
    os.makedirs(args.data_dir, exist_ok=True)

    # Import GUI module (requires tkinter)
    try:
        from hebrew_lip_reading.gui import MainWindow
    except ImportError as e:
        print(f"Error: Could not import GUI module: {e}")
        print("Make sure tkinter is installed (usually included with Python)")
        sys.exit(1)

    # Run the application
    app = MainWindow(data_dir=args.data_dir)
    app.run()


if __name__ == "__main__":
    main()
