import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from mipi2raw import convertMipi2Raw, bayer_order_maps

class Mipi2RawConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MIPI to RAW Converter")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        main_layout = QVBoxLayout()

        # Load MIPI RAW file button
        self.load_button = QPushButton("Load MIPI RAW File")
        self.load_button.clicked.connect(self.load_mipi_raw_file)
        main_layout.addWidget(self.load_button)

        # Width input
        main_layout.addWidget(QLabel("Width:"))
        self.width_input = QLineEdit()
        main_layout.addWidget(self.width_input)

        # Height input
        main_layout.addWidget(QLabel("Height:"))
        self.height_input = QLineEdit()
        main_layout.addWidget(self.height_input)

        # Bit depth selection
        main_layout.addWidget(QLabel("Bit Depth:"))
        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(["8", "10", "12", "14", "16"])
        main_layout.addWidget(self.bit_depth_combo)

        # Bayer pattern selection
        main_layout.addWidget(QLabel("Bayer Pattern:"))
        self.bayer_combo = QComboBox()
        self.bayer_combo.addItems(["RGGB", "BGGR", "GRBG", "GBRG"])
        main_layout.addWidget(self.bayer_combo)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_image)
        main_layout.addWidget(self.convert_button)

        # Set main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Placeholder for file path
        self.mipi_file_path = None

    def load_mipi_raw_file(self):
        # Open file dialog to select MIPI RAW file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open MIPI RAW File", "", "MIPI RAW Files (*.raw);;All Files (*)")
        if file_name:
            self.mipi_file_path = file_name

    def convert_image(self):
        if not self.mipi_file_path:
            print("Please load a MIPI RAW file first.")
            return

        # Get input values
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            print("Please enter valid numbers for width and height.")
            return

        bit_depth = int(self.bit_depth_combo.currentText())
        bayer_pattern = self.bayer_combo.currentText()
        bayer_order = bayer_order_maps[bayer_pattern]

        # Convert MIPI RAW to image
        convertMipi2Raw(self.mipi_file_path, width, height, bit_depth, bayer_order)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Mipi2RawConverterApp()
    window.show()
    sys.exit(app.exec_())