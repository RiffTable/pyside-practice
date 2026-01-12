# Drag Text to Move | Drag Body to Wire

from __future__ import annotations
import sys
from functools import partial
from PySide6.QtWidgets import (
	QApplication, QGraphicsSceneMouseEvent, QMainWindow, QGraphicsView, QGraphicsScene, 
	QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem, 
	QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QGraphicsItem, QGraphicsTextItem
)
from PySide6.QtCore import (
	Qt, QPointF, QLineF, QRectF, QEvent, QObject
)
from PySide6.QtGui import (
	QPen, QPainterPath, QColor, QBrush, QFont, QPainter, QPalette, QKeyEvent, QMouseEvent, QTransform
)
from UICore import Color

class PortItem(QGraphicsEllipseItem):
	def __init__(self, parent: GateItem, is_output=True):
		super().__init__(-5, -5, 10, 10, parent)
		self.is_output = is_output
		self.setBrush(QBrush(QColor("#34495e") if not is_output else "#3498db"))
		self.setPen(QPen(Qt.GlobalColor.white, 1))
		self.setPos(80 if is_output else 0, 25)

class WireItem(QGraphicsPathItem):
	def __init__(self, start_gate: GateItem, end_gate: GateItem, manager: QGraphicsScene):
		super().__init__()
		self.start_gate = start_gate
		self.end_gate = end_gate
		self.manager = manager
		self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
		self.setZValue(-1)
		self.update_path()

	def update_path(self):
		p1 = self.start_gate.scenePos() + QPointF(80, 25)
		p2 = self.end_gate.scenePos() + QPointF(0, 25)
		path = QPainterPath()
		path.moveTo(p1)
		path.cubicTo(p1.x() + 50, p1.y(), p2.x() - 50, p2.y(), p2.x(), p2.y())
		self.setPath(path)
		color = QColor("#2ecc71") if self.start_gate.state == 1 else QColor("#7f8c8d")
		if self.isSelected(): color = QColor("#f39c12")
		self.setPen(QPen(color, 3 if not self.isSelected() else 5))

	def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
		if event.button() == Qt.MouseButton.RightButton:
			self.manager.remove_wire(self)
		super().mousePressEvent(event)

class GateItem(QGraphicsRectItem):
	def __init__(self, x: float, y: float, gate_type: str, manager: QGraphicsScene):
		super().__init__(0, 0, 80, 50)
		self.setPos(x, y)
		self.gate_type = gate_type
		self.manager = manager
		self.state = 0
		self.inputs = []

		self.setBrush(QBrush(Color.gate_on))
		self.setPen(QPen(Qt.GlobalColor.black, 2))
		self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

		self.out_port = PortItem(self, True)
		self.in_port = PortItem(self, False)

		self.label = QGraphicsTextItem(self.gate_type, self)
		self.label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
		self.label.setDefaultTextColor(Qt.GlobalColor.white)
		self.label.setPos(15, 12)
		self.label.setCursor(Qt.CursorShape.SizeAllCursor)

	def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			self.manager.update_wires()
		return super().itemChange(change, value)

	def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
		# item_at_click = self.scene().itemAt(event.scenePos(), self.manager.views[0].transform())
		item_at_click = self.scene().itemAt(event.scenePos(), QTransform())
		
		if item_at_click == self.label:
			self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		else:
			self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
			if event.button() == Qt.MouseButton.LeftButton:
				self.manager.start_wire(self)
			elif event.button() == Qt.MouseButton.RightButton and self.gate_type == "IN":
				self.state = 1 if self.state == 0 else 0
				self.update_appearance()
				self.manager.run_logic()
		
		super().mousePressEvent(event)

	def update_appearance(self):
		if self.gate_type == "BULB":
			color = QColor("#f1c40f") if self.state == 1 else QColor("#e74c3c")
		else:
			color = Color.gate_on if self.state == 1 else Color.gate_off
		self.setBrush(QBrush(color))





class CircuitScene(QGraphicsScene):
	def __init__(self):
		super().__init__()
		
		self.wire_start_gate = None
		self.gates: list[GateItem] = []
		self.wires: list[WireItem] = []

		self.ghost_line = self.addLine(
			0, 0,
			0, 0,
			QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine)
			)
		self.ghost_line.setZValue(100)
		self.ghost_line.hide()

	def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
		if self.wire_start_gate:
			p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
			p2 = event.scenePos()
			self.ghost_line.setLine(QLineF(p1, p2))
		super().mouseMoveEvent(event)
	
	def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
		if self.wire_start_gate:
			self.ghost_line.hide()
			pos = event.scenePos()
			items = self.items(QRectF(
				pos.x()-15, pos.y()-15,
				30, 30)
			)
			for item in items:
				if isinstance(item, (PortItem, QGraphicsTextItem)):
					target = item.parentItem()
				else:
					target = item
				
				if isinstance(target, GateItem) and target != self.wire_start_gate:
					wire = WireItem(self.wire_start_gate, target, self)
					self.addItem(wire)
					self.wires.append(wire)
					target.inputs.append(self.wire_start_gate)
					self.run_logic()
					break
			self.wire_start_gate = None
		super().mouseReleaseEvent(event)
	
	def update_wires(self):
		for w in self.wires: w.update_path()

	def add_gate(self, gate_type: str):
		gate = GateItem(150, 150, gate_type, self)
		self.addItem(gate)
		self.gates.append(gate)

	def remove_wire(self, wire: WireItem):
		if wire in self.wires:
			wire.end_gate.inputs.remove(wire.start_gate)
			self.wires.remove(wire)
			self.removeItem(wire)
			# self.run_logic()
	
	def remove_gate(self, gate: GateItem):
		for w in self.wires:
			if w.start_gate == gate or w.end_gate == gate:
				self.remove_wire(w)
		if gate in self.gates:
			self.gates.remove(gate)
			self.removeItem(gate)
	
	def start_wire(self, gate: GateItem):
		self.wire_start_gate = gate
		p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
		self.ghost_line.setLine(QLineF(p1, p1))
		self.ghost_line.show()

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
			for item in self.selectedItems():
				if   isinstance(item, WireItem): self.remove_wire(item)
				elif isinstance(item, GateItem): self.remove_gate(item)
			
			self.run_logic()
		super().keyPressEvent(event)
	
	def run_logic(self):
		for _ in range(5):
			for g in self.gates:
				if g.gate_type == "IN": continue
				v = [i.state for i in g.inputs]
				if g.gate_type == "AND": g.state = 1 if v and all(v) else 0
				elif g.gate_type == "OR": g.state = 1 if any(v) else 0
				elif g.gate_type == "NOT": g.state = 1 if v and v[0] == 0 else 0
				elif g.gate_type == "BULB": g.state = 1 if any(v) else 0
				g.update_appearance()
		self.update_wires()



class CircuitView(QGraphicsView):
	def __init__(self, scene: CircuitScene):
		super().__init__(scene)
		
		self.viewport().setMouseTracking(True)
		self.setRenderHints(
			QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
		)

class LogicSimApp(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("LogiSim")

		central = QWidget()
		self.setCentralWidget(central)
		layout = QHBoxLayout(central)

		###======= CIRCUIT VIEW =======###
		self.scene = CircuitScene()
		self.view = CircuitView(self.scene)

		###======= SIDEBAR DRAG-N-DROP MENU =======###
		vbox = QVBoxLayout()
		vbox.setSpacing(10)
		for text in ["AND", "OR", "NOT", "IN", "BULB"]:
			btn = QPushButton(text)
			btn.setMinimumHeight(50)
			btn.clicked.connect(partial(self.scene.add_gate, text))
			vbox.addWidget(btn)
		vbox.addStretch()
		layout.addLayout(vbox)
		layout.addWidget(self.view)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle("Fusion")

	dark_palette = QPalette()
	Role = QPalette.ColorRole

	palette_colors = {
		Role.Window         : Color.secondary_bg,
		Role.WindowText     : Color.text,
		Role.Base           : Color.primary_bg,
		Role.AlternateBase  : Color.secondary_bg,
		Role.ToolTipBase    : Color.tooltip_bg,
		Role.ToolTipText    : Color.tooltip_text,
		Role.Text           : Color.text,
		Role.Button         : Color.button,
		Role.ButtonText     : Color.text,
		Role.Highlight      : Color.hl_text_bg,
		Role.HighlightedText: Color.text,
	}
	for role, color in palette_colors.items():
		dark_palette.setColor(QPalette.ColorGroup.All, role, color)
	app.setPalette(dark_palette)

	window = LogicSimApp()
	window.resize(1000, 600)
	window.show()
	sys.exit(app.exec())
