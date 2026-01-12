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
from UICore import Color
from CircuitView import (CircuitScene, CircuitView)







class AppWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Not LogiSim")

		central = QWidget()
		self.setCentralWidget(central)
		layout_main = QHBoxLayout(central)
		
		
		###======= CIRCUIT VIEW =======###
		self.view = CircuitView()


		###======= SIDEBAR DRAG-N-DROP MENU =======###
		self.dragbar = QVBoxLayout()
		self.dragbar.setSpacing(10)
		for text in ["AND", "OR", "NOT", "IN", "BULB"]:
			btn = QPushButton(text)
			btn.setMinimumHeight(50)
			# btn.clicked.connect(partial(self.scene.add_gate, text))
			self.dragbar.addWidget(btn)
		self.dragbar.addStretch()
		
		layout_main.addLayout(self.dragbar)
		layout_main.addWidget(self.view)



if __name__ == "__main__":
	app = QApplication(sys.argv)

	###======= APP COLOR PALETTE =======###
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


	###======= APP WINDOW =======###
	window = AppWindow()
	window.resize(1000, 600)
	window.show()

	sys.exit(app.exec())