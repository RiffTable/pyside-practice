from typing import cast
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
	QPoint, QPointF, QLineF, QRectF,
)
from PySide6.QtGui import (
	QPalette, QColor, QPainter, QPen, QBrush,
	QMouseEvent, QKeyEvent, QWheelEvent, QNativeGestureEvent,
)
from UICore import (
	Color,
)
from UIGates import (
	CompItem, WireItem
)











class CircuitScene(QGraphicsScene):
	def __init__(self):
		super().__init__()

		self.SIZE = 20
		self.gates: list[CompItem] = []
		self.wires: list[WireItem] = []

	def addComp(self, x: float, y:float, comp_type: type[CompItem]):
		comp = comp_type(*self.snapToGrid(x, y))
		self.addItem(comp)
		self.gates.append(comp)

	def snapToGrid(self, x: float, y:float) -> tuple[int, int]:
		return (
			round(x/self.SIZE)*self.SIZE,
			round(y/self.SIZE)*self.SIZE
		)



class CircuitView(QGraphicsView):
	scene: CircuitScene
	def __init__(self):
		self.scene = CircuitScene()
		super().__init__(self.scene)

		self.setSceneRect(-5000, -5000, 10000, 10000)
		self.viewport().setMouseTracking(True)
		self.setRenderHints(
			QPainter.RenderHint.Antialiasing |
			QPainter.RenderHint.TextAntialiasing
		)
		
		# Hide scrollbars
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		# Disable scrollbars
		self.horizontalScrollBar().disconnect(self)
		self.verticalScrollBar().disconnect(self)
		# self.setTransformationAnchor(QGraphicsView.NoAnchor)    # .translate() moves scrollbars

		self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
		self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)
		self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

		self.lastMousePos = QPointF(0, 0)

		# Zooming
		self.viewScale = 1
		self.zoomlvl = 1
	

	###======= MOUTH CONTROLS =======###
	def mousePressEvent(self, event: QMouseEvent):
		if event.buttons() & (Qt.MouseButton.RightButton | Qt.MouseButton.MiddleButton):
		# if event.button() == Qt.MouseButton.MiddleButton or event.button() == Qt.MouseButton.RightButton:
			self.lastMousePos = event.position()
		
		super().mousePressEvent(event)
	
	def mouseMoveEvent(self, event: QMouseEvent):
		mousepos = event.position()
		if event.buttons() & (Qt.MouseButton.RightButton | Qt.MouseButton.MiddleButton):
			delta = mousepos - self.lastMousePos
			
			self.translate(
				delta.x()/self.viewScale,
				delta.y()/self.viewScale
			)
			# print(f"{self.transform().dx()}, {self.transform().dy()}")
		else:
			super().mouseMoveEvent(event)
		
		self.lastMousePos = mousepos
	
	def wheelEvent(self, event: QWheelEvent):
		self.applyZoom(
			event.position().toPoint(),
			1.25 if event.angleDelta().y() > 0 else 0.8
		)
	
	def viewportEvent(self, event: QEvent):
		if event.type() == QEvent.Type.NativeGesture:
			gestEvent = cast(QNativeGestureEvent, event)
			if gestEvent.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
				self.applyZoom(
					gestEvent.position().toPoint(),
					1.0 + gestEvent.value()
				)
				return True
		return super().viewportEvent(event)
	
	def applyZoom(self, mousePos: QPoint, factor: float):
		minZ = 0.5
		maxZ = 2.0


		# Tracking data
		curZ = self.transform().m11()
		pos1 = self.mapToScene(mousePos)

		# Calculating zoom factor
		newZ = curZ*factor
		newZ = max(minZ, min(newZ, maxZ))

		# Applying Zoom
		k = newZ/curZ
		self.scale(k, k)
		self.viewScale = newZ

		# Make sure cursor stays on the same position in scene
		pos2 = self.mapToScene(mousePos)
		delta = pos2 - pos1
		self.translate(delta.x(), delta.y())
