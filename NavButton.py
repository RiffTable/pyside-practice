from PySide6.QtWidgets import QPushButton, QGridLayout

# 🢀 🢁 🢂 🢃 🢄 🢅 🢆 🢇
class NavButton:
	instance: QPushButton
	dir: tuple[int, int]

	def __init__(self, grid: QGridLayout, symbol: str, dir: tuple[int, int]):
		self.dir = dir
		x, y = dir
		self.instance = QPushButton(symbol)
		self.instance.setFixedSize(200 if x == 0 else 50, 200 if y == 0 else 50)
		grid.addWidget(self.instance, y+1, x+1)
	
	def callIfPressed(self, pan_tracker):
		if self.instance.isDown():
			pan_tracker(*self.dir)
