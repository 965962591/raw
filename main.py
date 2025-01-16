import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt
from raw import read_raw10

def convert_cv_to_qt(cv_img):
    """Convert from an opencv image to QImage."""
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return q_img.rgbSwapped()

class ImageViewer(QGraphicsView):
    def __init__(self, image_path, width, height, bayer_pattern):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 隐藏水平和垂直滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 读取并转换图像
        rgb_image = read_raw10(image_path, width, height, bayer_pattern)

        # 将OpenCV图像转换为QImage
        qt_image = convert_cv_to_qt(rgb_image)

        # 将QImage转换为QPixmap并添加到场景中
        self.pixmap_item = self.scene.addPixmap(QPixmap.fromImage(qt_image))

        # 启用鼠标滚轮缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

    # def resizeEvent(self, event):
    #     """自适应窗口大小"""
    #     self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """使用鼠标滚轮放大缩小图片"""
        factor = 1.15
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        """处理鼠标按下事件以开始拖动"""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件以停止拖动"""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            super().mouseReleaseEvent(event)

def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer(r"C:\Users\chenyang3\Desktop\raw\test\dcim\IMG_20250115_231916.raw", 4096, 3072, 'GRBG')
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()