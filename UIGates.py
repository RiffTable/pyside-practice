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
# from CircuitView import CircuitScene, CircuitView
from UICore import *






class CompItem(QGraphicsRectItem):
	def __init__(self, x: float, y: float):
		super().__init__(x, y, 80, 50)
		
		self.state = False
		self.setFlags(
			QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
			QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
			QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
		)
		self.updateVisual()
		self.setPen(QPen(Color.outline, 2))
		self.label = QGraphicsTextItem("=1", self)
		self.label.setFont(Font.default)
		# self.label.setDefaultTextColor(Color.text)
		self.label.setPos(x+5, y+5)


	def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
			return QPointF(*self.scene().snapToGrid(
				value.x(),
				value.y()
			))

		return super().itemChange(change, value)
	
	def updateVisual(self):
		if self.state: self.setBrush(Color.gate_on)
		else         : self.setBrush(Color.gate_off)



class WireItem(QGraphicsPathItem):
	def __init__(self, beg: CompItem, end: CompItem):
		super().__init__()
