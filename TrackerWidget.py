from enum import Enum
from math import sqrt
from random import random
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class st(Enum):
	UNSET		= 0
	DRIFTING	= 1
	FLYING		= 2

outRadius = 0.1
inRadius = 0.4

class TrackerWidget(QWidget):
	state = st.UNSET
	timer = 0
	progress: float

	x  = y  = 0
	vx = vy = 0
	ax = ay = 0
	offset_x = offset_y = -0.5

	def __init__(self, width: int):
		super().__init__()
		self.w = width
		self.setFixedSize(width, width)
		self.progress = 0

		self.changestate(st.DRIFTING)
	
	def changestate(self, newstate: int) -> None:
		print(f"New State: {"DRIFTING" if newstate == st.DRIFTING else "FLYING"}")
		if self.state == newstate:
			return
		
		if newstate == st.FLYING:
			self.timer = random()*(9-5) + 5
		elif newstate == st.DRIFTING:
			self.timer = random()*(6-5) + 5
		
		self.state = newstate

	def on_tick(self, dt):
		# Constants
		drag = 0.1
		accdrag = 0.1
		flyMax = 0.050
		driftMax = 0.007

		# Timer Countdown
		self.timer -= dt
		if self.timer < 0:
			self.changestate(st.DRIFTING if (self.state == st.FLYING) else st.FLYING)

		
		### Physics
		# Random Jerk
		jerk = driftMax if (self.state == st.DRIFTING) else flyMax
		randomx = 2*random()-1
		r = sqrt(1 - randomx**2)
		randomy = 2*r*random() - r

		# Change acceleration and simulation acc drag
		self.ax += randomx*(jerk*dt)
		self.ay += randomy*(jerk*dt)
		self.ax *= 1-accdrag
		self.ay *= 1-accdrag

		# Change velocity and simulation drag
		self.vx += self.ax
		self.vy += self.ay
		self.vx *= 1-drag
		self.vy *= 1-drag

		self.x += self.vx
		self.y += self.vy

		
		### Updating Progress
		pograte = 5 if (self.state == st.FLYING) else 1
		dist = self.getDist()

		if dist < inRadius: 
			self.progress += 1.5*pograte*dt
		elif dist < outRadius: 
			self.progress += 1.0*pograte*dt
		else:
			self.progress -= 3.0*pograte*dt
		
		if self.progress < 0:
			self.progress = 0
		elif self.progress > 100:
			self.progress = 100
		
		self.update()
	
	def paintEvent(self, event):
		# Draw
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
		
		# Background
		painter.fillRect(
			self.rect(),
			QColor(255, 255, 255)
		)

		# Dist Circles
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(QColor(0, 150, 0, 50))
		
		r = inRadius*self.w
		painter.drawEllipse(
			self.w/2 - r,
			self.w/2 - r,
			2*r,
			2*r
		)
		r = outRadius*self.w
		painter.drawEllipse(
			self.w/2 - r,
			self.w/2 - r,
			2*r,
			2*r
		)

		# Vermin
		painter.setPen(QColor(0, 0, 0))
		painter.setBrush(QColor(255, 200, 0))
		
		r = 10
		painter.drawEllipse(
			(self.x - self.offset_x)*self.w - r,
			(self.y - self.offset_y)*self.w - r,
			2*r,
			2*r
		)

	def getOffset(self) -> tuple[float, float]:
		return (
			self.x - self.offset_x - 0.5,
			self.y - self.offset_y - 0.5,
		)
	def getDist(self) -> float:
		dx, dy = self.getOffset()
		return sqrt(dx**2 + dy**2)
	
	def pan(self, x: float, y: float):
		panSpeed = 1.5
		self.offset_x += x*panSpeed
		self.offset_y += y*panSpeed
