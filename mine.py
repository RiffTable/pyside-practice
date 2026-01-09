import sys
from functools import partial
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
import Color
from test import (PortItem, GateItem, WireItem)






##########################################
##########################################
##########################################

class CircuitScene(QGraphicsScene):
	def __init__(self):
		super().__init__()

class CircuitView(QGraphicsView):
	def __init__(self, scene: CircuitScene):
		super().__init__(scene)
		
		self.setRenderHints(
			QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
		)
		self.viewport().setMouseTracking(True)

		# At the End

class LogicSimApp(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("LogiSim")

		central = QWidget()
		self.setCentralWidget(central)
		layout = QVBoxLayout(central)
		self.scene = CircuitScene()
		self.view = CircuitView(self.scene)
		
		layout.addWidget(self.view)

		self.ghost_line = self.scene.addLine(0,0,0,0, QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.DashLine))
		self.ghost_line.setZValue(100)
		self.ghost_line.hide()

		self.gates = []
		self.wires = []
		self.wire_start_gate = None

		###======= SIDEBAR DRAG-N-DROP MENU =======###
		dragmenu = QWidget(self)
		dragmenu.setGeometry(10, 10, 120, 250)
		vbox = QVBoxLayout(dragmenu)
		for text in ["AND", "OR", "NOT", "IN", "BULB"]:
			btn = QPushButton(text)
			btn.clicked.connect(partial(self.add_gate, text))
			vbox.addWidget(btn)
		
		self.scene.viewport().installEventFilter(self)


	def eventFilter(self, source: QObject, event: QEvent):
		if event.type() == QEvent.Type.MouseMove and self.wire_start_gate:
			self.update_ghost_wire(event.position().toPoint())
		return super().eventFilter(source, event)

	def add_gate(self, gate_type: str):
		gate = GateItem(150, 150, gate_type, self)
		self.scene.addItem(gate)
		self.gates.append(gate)

	def start_wiring(self, gate: GateItem):
		self.wire_start_gate = gate
		p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
		self.ghost_line.setLine(QLineF(p1, p1))
		self.ghost_line.show()

	def update_ghost_wire(self, qt_mouse_pos: QPointF):
		if self.wire_start_gate:
			p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
			p2 = self.view.mapToScene(qt_mouse_pos)
			self.ghost_line.setLine(QLineF(p1, p2))

	def mouseReleaseEvent(self, event: QMouseEvent):
		if self.wire_start_gate:
			self.ghost_line.hide()
			pos = self.view.mapToScene(event.position().toPoint())
			items = self.scene.items(QRectF(pos.x()-15, pos.y()-15, 30, 30))
			for item in items:
				target = item.parentItem() if isinstance(item, (PortItem, QGraphicsTextItem)) else item
				if isinstance(target, GateItem) and target != self.wire_start_gate:
					wire = WireItem(self.wire_start_gate, target, self)
					self.scene.addItem(wire); self.wires.append(wire)
					target.inputs.append(self.wire_start_gate)
					self.run_logic(); break
			self.wire_start_gate = None
		super().mouseReleaseEvent(event)

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
			for item in self.scene.selectedItems():
				if isinstance(item, WireItem): self.remove_wire(item)
				elif isinstance(item, GateItem):
					connected = [w for w in self.wires if w.start_gate == item or w.end_gate == item]
					for w in connected: self.remove_wire(w)
					if item in self.gates: self.gates.remove(item)
					self.scene.removeItem(item)
			self.run_logic()
		super().keyPressEvent(event)

	def remove_wire(self, wire: WireItem):
		if wire in self.wires:
			wire.end_gate.inputs.remove(wire.start_gate)
			self.wires.remove(wire); self.scene.removeItem(wire)
			self.run_logic()

	def update_wires(self):
		for w in self.wires: w.update_path()

	def run_logic(self):
		for _ in range(5):
			for g in self.gates:
				if g.gate_type == "IN": continue
				v = [inp.state for inp in g.inputs]
				if g.gate_type == "AND": g.state = 1 if v and all(v) else 0
				elif g.gate_type == "OR": g.state = 1 if any(v) else 0
				elif g.gate_type == "NOT": g.state = 1 if v and v[0] == 0 else 0
				elif g.gate_type == "BULB": g.state = 1 if any(v) else 0
				g.update_appearance()
		self.update_wires()

##########################################
##########################################
##########################################

class AppWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Not LogiSim")
		central = QWidget()
		self.setCentralWidget(central)
		layout = QVBoxLayout(central)
		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene)
		self.view.setRenderHints(
			QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
		)

		# Enable tracking
		self.view.viewport().setMouseTracking(True)
		layout.addWidget(self.view)

		self.ghost_line = self.scene.addLine(0,0,0,0, QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.DashLine))
		self.ghost_line.setZValue(100)
		self.ghost_line.hide()

		self.gates = []
		self.wires = []
		self.wire_start_gate = None

		###======= SIDEBAR DRAG-N-DROP MENU =======###
		btns = QWidget(self)
		btns.setGeometry(10, 10, 120, 250)
		vbox = QVBoxLayout(btns)
		for t in ["Input", "Output", "AND", "OR", "NOT"]:
			b = QPushButton(t); b.clicked.connect(lambda chk=False, g=t: self.add_gate(g))
			vbox.addWidget(b)

		self.view.viewport().installEventFilter(self)

if __name__ == "__main__":
	app = QApplication(sys.argv)

	# Color palette for the app in fusion theme
	app.setStyle("Fusion")
	dark_palette = QPalette()
	Role = QPalette.ColorRole

	palette_colors = {
		Role.Window         : Color.alt_bg,
		Role.WindowText     : Color.text,
		Role.Base           : Color.bg,
		Role.AlternateBase  : Color.alt_bg,
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

	# Create the main app window
	window = QMainWindow()
	window.resize(1000, 600)
	window.show()

	sys.exit(app.exec())