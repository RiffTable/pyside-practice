import sys
import time
from functools import partial
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
	QApplication, QWidget, QProgressBar, 
	QGridLayout, QHBoxLayout, QVBoxLayout
)
from TrackerWidget import TrackerWidget
from NavButton import NavButton
from StatTable import StatTable



class MainWindow(QWidget):
	deltaTime = 0.016

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Tomfoolery")

		main_layout = QHBoxLayout(self)
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)

		### Grid Layout
		grid = QGridLayout()
		grid.setSpacing(2)
		grid.setContentsMargins(5, 5, 5, 5)
		main_layout.addLayout(grid)

		# Central Tracker
		self.tracker = TrackerWidget(200)
		grid.addWidget(self.tracker, 1, 1)

		# Buttons
		self.buttons = [
			NavButton(grid, "🢄", (-1, -1)),
			NavButton(grid, "🢁", (0 , -1)),
			NavButton(grid, "🢅", (1 , -1)),
			NavButton(grid, "🢂", (1 ,  0)),
			NavButton(grid, "🢆", (1 ,  1)),
			NavButton(grid, "🢃", (0 ,  1)),
			NavButton(grid, "🢇", (-1,  1)),
			NavButton(grid, "🢀", (-1,  0))
		]

		### Right Panel
		right_panel = QVBoxLayout()
		right_panel.setSpacing(2)
		right_panel.setContentsMargins(5, 5, 5, 5)
		main_layout.addLayout(right_panel)

		# Stats Layout
		self.stats = StatTable()
		self.stats.setSpacing(10)
		self.stats.setContentsMargins(5, 5, 5, 5)
		right_panel.addLayout(self.stats)

		# self.stats.addEntry("x", lambda: str(self.tracker.x))
		# self.stats.addEntry("y", lambda: str(self.tracker.y))
		# self.stats.addEntry("ox", lambda: str(self.tracker.offset_x))
		# self.stats.addEntry("oy", lambda: str(self.tracker.offset_y))
		# self.stats.addEntry("dx", lambda: str(self.tracker.x - self.tracker.offset_x))
		# self.stats.addEntry("dy", lambda: str(self.tracker.y - self.tracker.offset_y))
		self.stats.addEntry("dist", lambda: str(int(self.tracker.getDist()*100)))

		# Progress Bar
		self.progbar = QProgressBar()
		self.progbar.setOrientation(Qt.Orientation.Vertical)
		self.progbar.setMinimum(0)
		self.progbar.setMaximum(100)
		right_panel.addWidget(self.progbar)

		right_panel.addStretch()
		



		# Setting the timer
		self.lastframe = time.perf_counter()
		timer = QTimer(self)
		timer.timeout.connect(self.on_tick)
		timer.start(16)

	def on_tick(self):
		self.tracker.on_tick(self.deltaTime)
		for btn in self.buttons:
			btn.callIfPressed(self.pan_tracker)
		self.stats.on_tick()
		self.progbar.setValue(int(self.tracker.progress))

		# Counting deltaTime
		nowframe = time.perf_counter()
		self.deltaTime = nowframe - self.lastframe
		self.lastframe = nowframe
	
	def pan_tracker(self, dx: float, dy: float):
		l = 0.707 if dx != 0 and dy != 0 else 1
		self.tracker.pan(dx*l*self.deltaTime, dy*l*self.deltaTime)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())