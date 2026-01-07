# Drag Text to Move | Drag Body to Wire

import sys
from PySide6.QtWidgets import (
  QApplication, QGraphicsSceneMouseEvent, QMainWindow, QGraphicsView, QGraphicsScene, 
  QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem, 
  QVBoxLayout, QWidget, QPushButton, QGraphicsItem, QGraphicsTextItem
)
from PySide6.QtCore import (
  QCoreApplication, Qt, QPointF, QLineF, QRectF, QEvent
)
from PySide6.QtGui import (
  QPen, QPainterPath, QColor, QBrush, QFont, QPainter, QPalette
)

class PortItem(QGraphicsEllipseItem):
  def __init__(self, parent, is_output=True):
    super().__init__(-5, -5, 10, 10, parent)
    self.is_output = is_output
    self.setBrush(QBrush(QColor("#34495e") if not is_output else "#3498db"))
    self.setPen(QPen(Qt.GlobalColor.white, 1))
    self.setPos(80 if is_output else 0, 25)

class WireItem(QGraphicsPathItem):
  def __init__(self, start_gate, end_gate, manager):
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
  def __init__(self, x, y, gate_type: str, manager):
    super().__init__(0, 0, 80, 50)
    self.setPos(x, y)
    self.gate_type = gate_type
    self.manager = manager
    self.state = 0
    self.inputs = []

    self.setBrush(QBrush(QColor("#3498db")))
    self.setPen(QPen(Qt.GlobalColor.black, 2))
    self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    self.out_port = PortItem(self, True)
    self.in_port = PortItem(self, False)

    self.label = QGraphicsTextItem(self.gate_type, self)
    self.label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    self.label.setDefaultTextColor(Qt.GlobalColor.white)
    self.label.setPos(15, 12)
    self.label.setCursor(Qt.CursorShape.SizeAllCursor)

  def itemChange(self, change, value):
    if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
      self.manager.update_wires()
    return super().itemChange(change, value)

  def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
    item_at_click = self.scene().itemAt(event.scenePos(), self.manager.view.transform())
    
    if item_at_click == self.label:
      self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
    else:
      self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
      if event.button() == Qt.MouseButton.LeftButton:
        self.manager.start_wiring(self)
      elif event.button() == Qt.MouseButton.RightButton and self.gate_type == "IN":
        self.state = 1 if self.state == 0 else 0
        self.update_appearance()
        self.manager.run_logic()
    
    super().mousePressEvent(event)

  def update_appearance(self):
    color = "#2ecc71" if self.state == 1 else "#3498db"
    if self.gate_type == "BULB": color = "#f1c40f" if self.state == 1 else "#e74c3c"
    self.setBrush(QBrush(QColor(color)))


class LogicSimApp(QMainWindow):
  def __init__(self):
    super().__init__()

    self.setWindowTitle("LogiSim")

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

    self.setupSidebar()
    self.view.viewport().installEventFilter(self)

  def eventFilter(self, source, event):
    # FIXED: Use QEvent.MouseMove instead of event.MouseMove
    if event.type() == QEvent.Type.MouseMove and self.wire_start_gate:
      self.update_ghost_wire(event.position().toPoint())
    return super().eventFilter(source, event)

  def setupSidebar(self):
    btns = QWidget(self)
    btns.setGeometry(10, 10, 120, 250)
    vbox = QVBoxLayout(btns)
    for t in ["AND", "OR", "NOT", "IN", "BULB"]:
      b = QPushButton(t); b.clicked.connect(lambda chk=False, g=t: self.add_gate(g))
      vbox.addWidget(b)

  def add_gate(self, g_type: str):
    gate = GateItem(150, 150, g_type, self)
    self.scene.addItem(gate)
    self.gates.append(gate)

  def start_wiring(self, gate):
    self.wire_start_gate = gate
    p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
    self.ghost_line.setLine(QLineF(p1, p1))
    self.ghost_line.show()

  def update_ghost_wire(self, qt_mouse_pos):
    if self.wire_start_gate:
      p1 = self.wire_start_gate.scenePos() + QPointF(80, 25)
      p2 = self.view.mapToScene(qt_mouse_pos)
      self.ghost_line.setLine(QLineF(p1, p2))

  def mouseReleaseEvent(self, event):
    if self.wire_start_gate:
      self.ghost_line.hide()
      pos = self.view.mapToScene(event.pos())
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

  def keyPressEvent(self, event):
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

  def remove_wire(self, wire):
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

if __name__ == "__main__":
  app = QApplication(sys.argv)
  app.setStyle("Fusion")

  dark_palette = QPalette()
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Window, QColor("#2b2b2b"))
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Base, QColor("#1e1e1e"))
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.AlternateBase, QColor("#2b2b2b"))
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.ToolTipText, Qt.GlobalColor.red)
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Text, Qt.GlobalColor.white)
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Button, QColor("#3c3f41"))
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Highlight, QColor("#2f65ca"))
  dark_palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

  app.setPalette(dark_palette)

  window = LogicSimApp()
  window.resize(1000, 600)
  window.show()
  sys.exit(app.exec())
