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
	QMouseEvent, QKeyEvent, QWheelEvent
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

	def addComp(self, x: float, y:float, comp_type):
		comp: CompItem = comp_type(*self.snapToGrid(x, y))
		self.addItem(comp)
		self.gates.append(comp)

	def snapToGrid(self, x: float, y:float) -> tuple[int, int]:
		return (
			round(x/self.SIZE)*self.SIZE,
			round(y/self.SIZE)*self.SIZE
		)



class CircuitView(QGraphicsView):
	def __init__(self):
		self.scene = CircuitScene()
		super().__init__(self.scene)

		self.ZOOMRATE = 1.25
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

		self.lastMousePos = QPointF(0, 0)

		# Zooming
		self.viewScale = 1
		self.zoomlvl = 1
	

	###======= MOUTH CONTROLS =======###
	def mousePressEvent(self, event: QMouseEvent):
		if event.button() == Qt.RightButton:
			self.lastMousePos = event.position()
		
		super().mousePressEvent(event)
	
	def mouseMoveEvent(self, event: QMouseEvent):
		mousepos = event.position()
		if event.buttons() & Qt.RightButton:
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
		minZ = -3
		maxZ = +3
		# 1. Capture the scene position under the mouse before zooming
		mouse_pos = event.position()
		scene_pos = self.mapToScene(mouse_pos.toPoint())
		event.scenePosition()

		# Zoom factor
		self.zoomlvl += +1 if event.angleDelta().y() > 0 else -1
		self.zoomlvl = max(minZ, min(self.zoomlvl, maxZ))

		# k = self.ZOOMRATE**(newZoom-self.currZoom)
		newscale = self.ZOOMRATE**self.zoomlvl
		k = newscale/self.viewScale
		self.scale(k, k)
		self.viewScale = newscale
		# self.viewScale = self.transform().m11()


		# Make sure cursor stays on the same position in scene
		new_scene_pos = self.mapToScene(mouse_pos.toPoint())
		delta = new_scene_pos - scene_pos
		self.translate(delta.x(), delta.y())