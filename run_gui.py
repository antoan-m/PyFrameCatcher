#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the project root to sys.path explicitly
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
