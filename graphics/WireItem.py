from __future__ import annotations
from typing import cast
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
# from CircuitView import CircuitScene, CircuitView
from CompItem import CompItem

class WireItem(QGraphicsPathItem):
	def __init__(self, beg: CompItem, end: CompItem):
		super().__init__()