import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog, QGraphicsView, QSplitter
from PyQt5.QtCore import Qt, QSettings
import cv2
import numpy as np
from mipi2raw import convertMipi2Raw, bayer_order_maps
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent, QPainter
from PyQt5.QtWidgets import QGraphicsScene
import json  # 添加 json 模块

class ImageGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)

    def wheelEvent(self, event: QWheelEvent):
        # Zoom in or out
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

class Mipi2RawConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MIPI to RAW Converter")
        self.setGeometry(100, 100, 800, 300)

        # Main layout using QSplitter
        splitter = QSplitter(Qt.Horizontal)

        # Left layout for image display
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        self.graphics_view = ImageGraphicsView()
        left_layout.addWidget(self.graphics_view)
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right layout for controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()


        # Width and Height in the same row
        size_layout = QHBoxLayout()
        
        size_layout.addWidget(QLabel("Width:"))
        self.width_input = QLineEdit()
        size_layout.addWidget(self.width_input)

        size_layout.addWidget(QLabel("Height:"))
        self.height_input = QLineEdit()
        size_layout.addWidget(self.height_input)

        right_layout.addLayout(size_layout)

        # Bit Depth and Bayer Pattern in the same row
        format_layout = QHBoxLayout()

        format_layout.addWidget(QLabel("Bit Depth:"))
        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(["8", "10", "12", "14", "16"])
        format_layout.addWidget(self.bit_depth_combo)

        format_layout.addWidget(QLabel("Bayer Pattern:"))
        self.bayer_combo = QComboBox()
        self.bayer_combo.addItems(["RGGB", "BGGR", "GRBG", "GBRG"])
        format_layout.addWidget(self.bayer_combo)

        right_layout.addLayout(format_layout)
        # Load and Convert buttons in the same row
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load MIPI RAW File")
        self.load_button.clicked.connect(self.load_mipi_raw_file)
        button_layout.addWidget(self.load_button)

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_image)
        button_layout.addWidget(self.convert_button)
        right_layout.addLayout(button_layout)
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set initial sizes for the splitter
        splitter.setSizes([600, 100])  # Adjust the sizes as needed

        # Set main widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(splitter)
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        # Placeholder for file path
        self.mipi_file_path = None

        # Initialize QSettings
        self.settings = QSettings("YourCompany", "Mipi2RawConverter")

        # Load previous settings from JSON
        self.load_settings()

    def load_settings(self):
        try:
            with open("raw_settings.json", "r") as file:
                settings = json.load(file)
                self.width_input.setText(settings.get("width", ""))
                self.height_input.setText(settings.get("height", ""))
                self.bit_depth_combo.setCurrentText(settings.get("bit_depth", "8"))
                self.bayer_combo.setCurrentText(settings.get("bayer_pattern", "RGGB"))
                self.mipi_file_path = settings.get("mipi_file_path", None)
        except FileNotFoundError:
            # 如果文件不存在，使用默认值
            self.width_input.setText("")
            self.height_input.setText("")
            self.bit_depth_combo.setCurrentText("8")
            self.bayer_combo.setCurrentText("RGGB")
            self.mipi_file_path = None

    def closeEvent(self, event):
        # Save current values to JSON
        settings = {
            "width": self.width_input.text(),
            "height": self.height_input.text(),
            "bit_depth": self.bit_depth_combo.currentText(),
            "bayer_pattern": self.bayer_combo.currentText(),
            "mipi_file_path": self.mipi_file_path
        }
        with open("raw_settings.json", "w") as file:
            json.dump(settings, file, indent=4)
        super().closeEvent(event)

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

        # Load the converted image
        jpg_file_path = self.mipi_file_path[:-4] + '_unpack.jpg'
        self.display_image(jpg_file_path)

    def display_image(self, image_path):
        # Load image using QImage
        image = QImage(image_path)
        if image.isNull():
            print("Failed to load image:", image_path)
            return

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(image)

        # Create a scene and add the pixmap
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        # Set the scene to the graphics view
        self.graphics_view.setScene(scene)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Mipi2RawConverterApp()
    window.show()
    sys.exit(app.exec_())