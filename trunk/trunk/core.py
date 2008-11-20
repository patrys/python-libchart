import cairo
from math import floor, ceil, log10
from StringIO import StringIO

class Chart(object):
	width = 0
	height = 0
	text = None
	title = 'Untitled chart'
	points = []
	palette = (
		(231.0/255.0, 0, 0),
		(0, 156.0/255.0, 231.0/255.0),
		(156.0/255.0, 231.0/255.0, 0),
		(255.0/255.0, 225.0/255.0, 35.0/255.0),
		(219.0/255.0, 251.0/255.0, 0),
		(255.0/255.0, 164.0/255.0, 54.0/255.0),
		(70.0/255.0, 70.0/255.0, 70.0/255.0),
		(121.0/255.0, 75.0/255.0, 255.0/255.0),
		(231.0/255.0, 94.0/255.0, 50.0/255.0),
		(142.0/255.0, 165.0/255.0, 250.0/255.0),
		(162.0/255.0, 254.0/255.0, 239.0/255.0),
		(137.0/255.0, 240.0/255.0, 166.0/255.0),
		(104.0/255.0, 221.0/255.0, 71.0/255.0),
		(98.0/255.0, 174.0/255.0, 35.0/255.0),
		(93.0/255.0, 129.0/255.0, 1.0/255.0)
	)
	textColor = (0, 0, 0)
	backgroundColor = (1, 1, 1)
	chartRatio = 0.6

	def __init__(self, palette = None, background = (1, 1, 1, 1), foreground = (0, 0, 0)):
		if palette:
			self.palette = palette
		self.textColor = foreground
		self.backgroundColor = background
		self.graphDepth = 10
		self.reset()

	def computeLabels(self):
		labels = []
		for (label, value) in self.points:
			labels.append(label)
		self.labels = labels

	def setChartRatio(self, ratio):
		self.chartRatio = ratio

	def reset(self):
		self.text = Text()
		self.points = []
		self.setTitle('Untitled chart')

	def selectFont(self, name, size):
		self.text.selectFont(name, size)

	def addPoint(self, point):
		self.points.append(point)

	def setTitle(self, title):
		self.title = title

	def outlinedBox(self, point1, point2, color):
		w = int(point2[0] - point1[0] + 1)
		h = int(point2[1] - point1[1] + 1)
		self.ctx.set_source_rgb(*color)
		self.ctx.rectangle(int(point1[0]) - 0.5, int(point1[1]) - 0.5, w + 1, h + 1)
		self.ctx.fill()
		self.ctx.rectangle(int(point1[0]), int(point1[1]), w, h)
		self.ctx.fill()

	def printLabel(self):
		self.computeLabels()
		i = 0
		boxX1 = self.labelTLX + self.margin
		boxX2 = boxX1 + self.text.fontSize * 1.5
		for legend in self.labels:
			color = self.palette[i % len(self.palette)]
			boxY1 = self.labelTLY + self.margin + i * (self.text.fontSize * 2 + self.margin)
			boxY2 = boxY1 + self.text.fontSize * 1.5
			self.outlinedBox((boxX1, boxY1), (boxX2, boxY2), color)
			self.text.printText(self.ctx, (boxX2 + self.margin, boxY1 + self.text.fontSize * 0.75), self.textColor, legend, self.text.VERTICAL_CENTER_ALIGN);
			i += 1

	def printTitle(self):
		self.text.printText(self.ctx, (self.width * 0.5, self.margin * 0.5 + 2 * self.text.fontSize), self.textColor, self.title, align = self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_CENTER_ALIGN, weight = cairo.FONT_WEIGHT_BOLD, size = self.text.fontSize * 1.5)

	def createImage(self):
		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		self.ctx = cairo.Context(self.surface)
		self.ctx.rectangle(0, 0, self.width, self.height)
		self.ctx.set_source_rgba(*self.backgroundColor)
		self.ctx.fill()
		self.shadowPalette = []
		shadowFactor = 0.82
		for colorRGB in self.palette:
			(red, green, blue) = colorRGB
			shadowColor = (red * shadowFactor, green * shadowFactor, blue * shadowFactor)
			self.shadowPalette.append(shadowColor)

	def render(self, width, height, fileName = None, **kwargs):
		self.height = height
		self.width = width
		self.margin = self.text.fontSize * 0.5
		self.draw(**kwargs)
		self.ctx.show_page()
		if fileName:
			self.surface.write_to_png(fileName)
			self.surface.finish()
		else:
			buf = StringIO()
			self.surface.write_to_png(buf)
			self.surface.finish()
			return buf.getvalue()

class Text(object):
	HORIZONTAL_LEFT_ALIGN = 1
	HORIZONTAL_CENTER_ALIGN = 2
	HORIZONTAL_RIGHT_ALIGN = 4
	VERTICAL_BOTTOM_ALIGN = 8
	VERTICAL_CENTER_ALIGN = 16
	VERTICAL_TOP_ALIGN = 32
	fontCondensed = None
	fontCondensedBold = None

	def selectFont(self, name, size):
		self.fontName = name
		self.fontSize = size

	def printText(self, canvas, point, color, text, align = 0, weight = cairo.FONT_WEIGHT_NORMAL, size = None):
		if not size:
			size = self.fontSize
		canvas.select_font_face(self.fontName, cairo.FONT_SLANT_NORMAL, weight)
		canvas.set_font_size(size)
		if not align & self.HORIZONTAL_CENTER_ALIGN and not align & self.HORIZONTAL_RIGHT_ALIGN:
			align |= self.HORIZONTAL_LEFT_ALIGN
		if not align & self.VERTICAL_CENTER_ALIGN and not align & self.VERTICAL_TOP_ALIGN:
			align |= self.VERTICAL_BOTTOM_ALIGN
		(bw, bh, tw, th) = canvas.text_extents(text)[:4]
		(pointX, pointY) = point
		if align & self.HORIZONTAL_CENTER_ALIGN:
			pointX = pointX - tw / 2
		elif align & self.HORIZONTAL_RIGHT_ALIGN:
			pointX = pointX - tw
		if align & self.VERTICAL_CENTER_ALIGN:
			pointY = pointY + size * 0.4
		elif align & self.VERTICAL_TOP_ALIGN:
			pointY = pointY + size * 0.9
		canvas.set_source_rgb(*color)
		canvas.move_to(pointX, pointY)
		canvas.show_text(text)

class BarChart(Chart):
	def computeBound(self, margin = 0.0):
		if not self.points:
			yMin = 0
			yMax = 1
		else:
			yMax = self.points[0][1]
			yMin = yMax

			for point in self.points:
				y = point[1]
				if y < yMin:
					yMin = y
				if y > yMax:
					yMax = y
		self.yMinValue = yMin * (1.0 - margin)
		self.yMaxValue = yMax
		self.sampleCount = len(self.points)

	def createImage(self, **kwargs):
		super(BarChart, self).createImage(**kwargs)
		self.ctx.set_source_rgb(*self.textColor)
		self.ctx.rectangle(self.graphTLX, self.graphTLY, 1, self.graphHeight)
		self.ctx.fill()
		self.ctx.rectangle(self.graphTLX, self.graphBRY, self.graphWidth, 1)
		self.ctx.fill()

class Axis(object):
	min = 0
	max = 1
	guide = 10.0
	tics = 1.0

	def __init__(self, min, max):
		self.min = min
		self.max = max

	def quantizeTics(self):
		norm = self.delta / self.magnitude
		posns = self.guide / norm
		if posns > 20:
			tics = 0.05
		elif posns > 10:
			tics = 0.2
		elif posns > 5:
			tics = 0.4
		elif posns > 3:
			tics = 0.5
		elif posns > 2:
			tics = 1.0
		elif posns > 0.25:
			tics = 2.0
		else:
			tics = math.ceil(norm)
		self.tics = tics * self.magnitude

	def computeBoundaries(self):
		self.delta = abs(self.max - self.min)
		if self.delta == 0:
			self.delta = 1
		self.magnitude = pow(10, floor(log10(self.delta)))
		self.quantizeTics()
		self.displayMin = floor(self.min / self.tics) * self.tics
		self.displayMax = ceil(self.max / self.tics) * self.tics
		self.displayDelta = self.displayMax - self.displayMin
		if self.displayDelta == 0:
			self.displayDelta = 1

	def setBoundaries(self, sampleCount, yMinValue, yMaxValue):
		self.sampleCount = sampleCount
		self.yMinValue = yMinValue
		self.yMaxValue = yMaxValue
