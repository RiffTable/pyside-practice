from __future__ import annotations
from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget,
	QPushButton, 
	QGraphicsScene, QGraphicsView,
	QVBoxLayout, QHBoxLayout,
	QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsRectItem, QGraphicsSceneMouseEvent,
)
from PySide6.QtCore import (
	Qt, QObject,
	QEvent, 
	QPointF, QLineF, QRectF
)
from PySide6.QtGui import (
	QPalette, QColor, QFont, QPainter, QPen, QBrush, QPainterPath,
	QMouseEvent, QKeyEvent,
)
from UICore import Color






class CompItem(QGraphicsRectItem):
	def __init__(self, x: float, y: float, scene: QGraphicsScene):
		super().__init__(x, y, 80, 50)

		self.setFlags(
			QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
			QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
		)

class WireItem(QGraphicsPathItem):
	def __init__(self, beg: CompItem, end: CompItem, scene: QGraphicsScene):
		super().__init__()
	pass
