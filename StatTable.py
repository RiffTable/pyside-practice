from PySide6.QtWidgets import QLabel, QLineEdit, QGridLayout
from typing import Callable

class StatTable(QGridLayout):
	rows: int
	fieldlist: list[QLineEdit]
	funclist: list[Callable[[], str]]
	def __init__(self):
		super().__init__()
		self.rows = 0
		self.fieldlist = []
		self.funclist = []
	
	def addEntry(self, labeltext: str, func: Callable[[], str]):
		lbl = QLabel(labeltext)
		self.addWidget(lbl, self.rows, 0)

		field = QLineEdit()
		field.setReadOnly(True)
		self.fieldlist.append(field)
		self.funclist.append(func)
		self.addWidget(field, self.rows, 1)

		self.rows += 1

	def on_tick(self):
		for i in range(self.rows):
			self.fieldlist[i].setText(self.funclist[i]())