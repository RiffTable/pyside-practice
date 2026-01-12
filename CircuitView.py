from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget,
	QPushButton, 
	QGraphicsScene, QGraphicsView,
	QVBoxLayout, QHBoxLayout,
	QGraphicsTextItem, 
)
from PySide6.QtCore import (
	Qt, QObject,
	QEvent, 
	QPointF, QLineF, QRectF
)
from PySide6.QtGui import (
	QPalette, QColor, QPainter, QPen, QBrush,
	QMouseEvent, QKeyEvent
)
from UICore import Color











class CircuitScene(QGraphicsScene):
	def __init__(self):
		super().__init__()

		self.gates = []
		self.wires = []



class CircuitView(QGraphicsView):
	def __init__(self):
		self.scene = CircuitScene()
		super().__init__(self.scene)

		self.viewport().setMouseTracking(True)
		self.setRenderHints(
			QPainter.RenderHint.Antialiasing |
			QPainter.RenderHint.TextAntialiasing
		)