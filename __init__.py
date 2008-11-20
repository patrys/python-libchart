import operator
from math import cos, pi, sin
from core import Chart, BarChart, Axis
import os

class PieChart(Chart):
	total = 0
	percent = 0

	def computePercent(self):
		self.total = 0
		self.percent = []
		for point in self.points:
			self.total += point[1]
		for point in self.points:
			if self.total == 0:
				percent = 0
			else:
				percent = 100 * (point[1] / float(self.total))
			self.percent.append((percent, point))
		self.percent = sorted(self.percent, key = operator.itemgetter(0), reverse = True)

	def computeLabels(self):
		labels = []
		for (percent, data) in self.percent:
			labels.append(data[0])
		self.labels = labels

	def setLabelMarginCenter(self, labelMarginCenter):
		self.labelMarginCenter = labelMarginCenter

	def computeLabelMargin(self):
		graphWidth = self.width - self.margin * 2
		self.pieTLX = self.margin
		self.pieTLY = self.margin + 4 * self.text.fontSize
		self.pieBRX = self.pieTLX + graphWidth * self.chartRatio
		self.pieBRY = self.height - self.margin
		self.pieCenterX = self.pieTLX + (self.pieBRX - self.pieTLX) / 2
		self.pieCenterY = self.pieTLY + (self.pieBRY - self.pieTLY) / 2
		self.pieWidth = self.pieBRX - self.pieTLX
		self.pieWidth -= self.text.fontSize * 6
		self.pieHeight = self.pieBRY - self.pieTLY
		self.pieHeight -= self.text.fontSize * 4
		self.labelTLX = self.pieBRX
		self.labelTLY = self.pieTLY

	def drawPieslice(self, centerX, centerY, radius, point1, point2, color):
		self.ctx.move_to(centerX, centerY)
		self.ctx.arc(centerX, centerY, radius, point1, point2)
		self.ctx.line_to(centerX, centerY)
		self.ctx.set_source_rgb(*color)
		self.ctx.fill()

	def drawDisc(self, cy, colorArray, alpha = 0):
		i = 0
		angle1 = 0
		percentTotal = 0
		mtx = self.ctx.get_matrix()
		self.ctx.translate(self.pieCenterX, self.pieCenterY - cy)
		self.ctx.scale(1.0, float(self.pieHeight) / float(self.pieWidth))
		for a in self.percent:
			(percent, point) = a
			color = colorArray[i % len(colorArray)]
			if alpha:
				rDiff = self.backgroundColor[0] - color[0]
				gDiff = self.backgroundColor[1] - color[1]
				bDiff = self.backgroundColor[2] - color[2]
				color = (color[0] + rDiff * alpha, color[1] + gDiff * alpha, color[2] + bDiff * alpha)
			i += 1
			percentTotal += percent
			if i == len(self.percent) or self.percent[i] == 0:
				percentTotal = 100
			angle2 = percentTotal / 50.0 * pi
			if percent > 0:
				self.drawPieslice(0, 0, self.pieWidth / 2, angle1, angle2, color)
			angle1 = angle2
		self.ctx.set_matrix(mtx)

	def drawPercent(self):
		angle1 = 0
		percentTotal = 0
		for a in self.percent:
			(percent, point) = a
			if percent <= 0:
				continue
			percentTotal += percent
			angle2 = percentTotal * 2 * pi / 100
			angle = angle1 + (angle2 - angle1) / 2
			text = '%.1d%%' % percent
			x = cos(angle) * (self.pieWidth + 3 * self.text.fontSize) / 2 + self.pieCenterX
			y = sin(angle) * (self.pieHeight + 3 * self.text.fontSize) / 2 + self.pieCenterY - self.graphDepth * 0.5
			self.text.printText(self.ctx, (int(x), int(y)), self.textColor, text, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			angle1 = angle2

	def printPie(self):
		if self.points and self.percent[0][0]:
			for cy in range(self.graphDepth - 1):
				self.drawDisc(- self.graphDepth + cy, self.shadowPalette, alpha = 1.00 - (0.5 * cy / float(self.graphDepth)))
			for cy in range(self.graphDepth):
				self.drawDisc(cy, self.shadowPalette)
			self.drawDisc(self.graphDepth, self.palette)
			self.drawPercent()
		else:
			self.text.printText(self.ctx, (self.pieCenterX, self.pieCenterY), self.textColor, 'No data', self.text.VERTICAL_CENTER_ALIGN | self.text.HORIZONTAL_CENTER_ALIGN);

	def draw(self):
		self.computeLabelMargin()
		self.computePercent()
		self.createImage()
		self.printTitle()
		self.printPie()
		self.printLabel()

class VerticalChart(BarChart):
	def printAxis(self):
		if not self.sampleCount:
			return
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		value = minValue
		while value <= maxValue:
			y = int(self.graphBRY - (value - minValue) * self.graphHeight / self.axis.displayDelta)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(self.graphTLX - 3, y, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(self.graphTLX - 1, y, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (self.graphTLX - 5, y), self.textColor, '%u' % value, self.text.HORIZONTAL_RIGHT_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			value += stepValue
		columnWidth = self.graphWidth / self.sampleCount
		i = 0
		for point in self.points:
			x = int(self.graphTLX + i * columnWidth)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(x, self.graphBRY + 3, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(x, self.graphBRY + 1, 1, 1)
			self.ctx.fill()
			i += 1

	def computeLabelMargin(self):
		self.axis = Axis(self.yMinValue, self.yMaxValue)
		self.axis.computeBoundaries()
		self.graphTLX = int(self.margin + 3 * self.text.fontSize)
		self.graphTLY = int(self.margin + 5 * self.text.fontSize)
		self.graphBRX = int(self.graphTLX  + (self.width - 2 * self.margin) * self.chartRatio)
		self.graphBRY = int(self.height - self.margin - self.text.fontSize)
		self.graphWidth = self.graphBRX - self.graphTLX + 1
		self.graphHeight = self.graphBRY - self.graphTLY + 1
		self.labelTLX = self.graphBRX
		self.labelTLY = self.graphTLY

	def printBar(self):
		if not self.sampleCount:
			self.text.printText(self.ctx, ((self.graphTLX + self.graphBRX) / 2, (self.graphTLY + self.graphBRY) / 2), self.textColor, 'No data', self.text.VERTICAL_CENTER_ALIGN | self.text.HORIZONTAL_CENTER_ALIGN);
			return
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		columnWidth = int(self.graphWidth / self.sampleCount)
		i = 0
		for point in self.points:
			x = self.graphTLX + i * columnWidth
			value = point[1]
			ymin = int((value - minValue) * self.graphHeight / self.axis.displayDelta)
			self.text.printText(self.ctx, (x + columnWidth * 0.5, self.graphBRY - ymin - self.text.fontSize * 0.5), self.textColor, '%u' % value, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_BOTTOM_ALIGN)
			x1 = x + self.text.fontSize * 0.5
			x2 = columnWidth - self.text.fontSize
			color = self.palette[i % len(self.palette)]
			self.ctx.set_source_rgb(*color)
			self.ctx.rectangle(x1, self.graphBRY - ymin, x2, ymin)
			self.ctx.fill()
			if x2 > 2 * self.graphDepth:
				shadow = self.shadowPalette[i % len(self.palette)]
				self.ctx.set_source_rgb(*shadow)
				self.ctx.rectangle(x1 + x2 - self.graphDepth, self.graphBRY - ymin, self.graphDepth, ymin)
				self.ctx.fill()
			for line in range(1, min(self.graphDepth, ymin)):
				alpha = 0.5 - float(line) / float(2 * self.graphDepth)
				if x2 > 2 * self.graphDepth:
					self.ctx.set_source_rgba(color[0], color[1], color[2], alpha)
					self.ctx.rectangle(x1, self.graphBRY + line, x2 - self.graphDepth, 1)
					self.ctx.fill()
					self.ctx.set_source_rgba(shadow[0], shadow[1], shadow[2], alpha)
					self.ctx.rectangle(x1 + x2 - self.graphDepth, self.graphBRY + line, self.graphDepth, 1)
					self.ctx.fill()
				else:
					self.ctx.set_source_rgba(color[0], color[1], color[2], alpha)
					self.ctx.rectangle(x1, self.graphBRY + line, x2, 1)
					self.ctx.fill()
			i += 1

	def draw(self, margin = 0.0):
		self.computeBound(margin = margin)
		self.computeLabelMargin()
		self.createImage()
		self.printTitle()
		self.printBar()
		self.printAxis()
		self.printLabel()

class VerticalComparativeBarChart(VerticalChart):
	groups = []
	groupSize = 2
	def printAxis(self):
		if not self.sampleCount:
			return
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		value = minValue
		while value <= maxValue:
			y = int(self.graphBRY - (value - minValue) * self.graphHeight / self.axis.displayDelta)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(self.graphTLX - 3, y, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(self.graphTLX - 1, y, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (self.graphTLX - 5, y), self.textColor, '%u' % value, self.text.HORIZONTAL_RIGHT_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			value += stepValue
		columnWidth = self.graphWidth / len(self.groups)
		i = 0
		for group in self.groups:
			x = int(self.graphTLX + i * columnWidth)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(x, self.graphBRY + 3, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(x, self.graphBRY + 1, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (x + columnWidth * 0.5, self.graphBRY + 2), self.textColor, group, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_TOP_ALIGN)
			i += 1

	def addGroup(self, name):
		self.groups.append(name)

	def setGroupSize(self, groupSize):
		self.groupSize = groupSize

	def computeLabels(self):
		labels = []
		for (label, value) in self.points:
			labels.append(label)
		self.labels = labels[:self.groupSize]

	def printBar(self):
		if not self.sampleCount:
			self.text.printText(self.ctx, ((self.graphTLX + self.graphBRX) / 2, (self.graphTLY + self.graphBRY) / 2), self.textColor, 'No data', self.text.VERTICAL_CENTER_ALIGN | self.text.HORIZONTAL_CENTER_ALIGN);
			return;
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		columnWidth = int(self.graphWidth / self.groupSize / len(self.groups))
		i = 0
		for point in self.points:
			x = self.graphTLX + i * columnWidth
			value = point[1]
			ymin = int((value - minValue) * self.graphHeight / self.axis.displayDelta)
			self.text.printText(self.ctx, (x + columnWidth * 0.5, self.graphBRY - ymin - self.text.fontSize * 0.5), self.textColor, '%u' % value, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_BOTTOM_ALIGN)
			x1 = x + self.text.fontSize * 0.5
			x2 = columnWidth - self.text.fontSize
			color = self.palette[i % self.groupSize % len(self.palette)]
			self.ctx.set_source_rgb(*color)
			self.ctx.rectangle(x1, self.graphBRY - ymin, x2, ymin)
			self.ctx.fill()
			if x2 > 2 * self.graphDepth:
				shadow = self.shadowPalette[i % self.groupSize % len(self.palette)]
				self.ctx.set_source_rgb(*shadow)
				self.ctx.rectangle(x1 + x2 - self.graphDepth, self.graphBRY - ymin, self.graphDepth, ymin)
				self.ctx.fill()
			for line in range(1, min(self.graphDepth, ymin)):
				alpha = 0.5 - float(line) / float(2 * self.graphDepth)
				if x2 > 2 * self.graphDepth:
					self.ctx.set_source_rgba(color[0], color[1], color[2], alpha)
					self.ctx.rectangle(x1, self.graphBRY + line, x2 - self.graphDepth, 1)
					self.ctx.fill()
					self.ctx.set_source_rgba(shadow[0], shadow[1], shadow[2], alpha)
					self.ctx.rectangle(x1 + x2 - self.graphDepth, self.graphBRY + line, self.graphDepth, 1)
					self.ctx.fill()
				else:
					self.ctx.set_source_rgba(color[0], color[1], color[2], alpha)
					self.ctx.rectangle(x1, self.graphBRY + line, x2, 1)
					self.ctx.fill()
			i += 1

	def draw(self, margin = 0.0):
		self.computeBound(margin = margin)
		self.computeLabelMargin()
		self.createImage()
		self.printTitle()
		self.printBar()
		self.printAxis()
		self.printLabel()

class VerticalComparativeKnotChart(VerticalComparativeBarChart):
	groups = []
	groupSize = 2
	def printAxis(self):
		if not self.sampleCount:
			return
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		value = minValue
		while value <= maxValue:
			y = int(self.graphBRY - (value - minValue) * self.graphHeight / self.axis.displayDelta)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(self.graphTLX - 3, y, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(self.graphTLX - 1, y, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (self.graphTLX - 5, y), self.textColor, '%u' % value, self.text.HORIZONTAL_RIGHT_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			value += stepValue
		columnWidth = self.graphWidth / len(self.groups)
		i = 0
		for group in self.groups:
			x = int(self.graphTLX + (i + 0.5) * columnWidth)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(x, self.graphBRY + 3, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(x, self.graphBRY + 1, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (x, self.graphBRY + 2), self.textColor, group, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_TOP_ALIGN)
			i += 1

	def printKnots(self):
		if not self.sampleCount:
			self.text.printText(self.ctx, ((self.graphTLX + self.graphBRX) / 2, (self.graphTLY + self.graphBRY) / 2), self.textColor, 'No data', self.text.VERTICAL_CENTER_ALIGN | self.text.HORIZONTAL_CENTER_ALIGN);
			return;
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		columnWidth = int(self.graphWidth / len(self.groups))
		i = 0
		for point in self.points:
			x = self.graphTLX + (int(i / self.groupSize) + 0.5) * columnWidth
			value = point[1]
			ymin = int((value - minValue) * self.graphHeight / self.axis.displayDelta)
			color = self.palette[i % self.groupSize % len(self.palette)]
			if i >= self.groupSize:
				lastPoint = self.points[i - self.groupSize]
				self.ctx.set_source_rgb(*color)
				self.ctx.move_to(x, self.graphBRY - ymin)
				lastymin = int((lastPoint[1] - minValue) * self.graphHeight / self.axis.displayDelta)
				self.ctx.line_to(x - columnWidth, self.graphBRY - lastymin)
				self.ctx.set_line_width(self.text.fontSize * 0.5)
				self.ctx.stroke()
			i += 1
		i = 0
		for point in self.points:
			x = self.graphTLX + (int(i / self.groupSize) + 0.5) * columnWidth
			value = point[1]
			ymin = int((value - minValue) * self.graphHeight / self.axis.displayDelta)
			color = self.palette[i % self.groupSize % len(self.palette)]
			self.ctx.set_source_rgb(*color)
			self.ctx.arc(x, self.graphBRY - ymin, self.text.fontSize, 0, 2 * pi)
			self.ctx.fill()
			self.text.printText(self.ctx, (x, self.graphBRY - ymin), self.textColor, '%u' % value, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			i += 1

	def draw(self, margin = 0.0):
		self.computeBound(margin = margin)
		self.computeLabelMargin()
		self.createImage()
		self.printTitle()
		self.printKnots()
		self.printAxis()
		self.printLabel()

class HorizontalChart(VerticalChart):
	def printAxis(self):
		if not self.sampleCount:
			return;
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		value = minValue
		while value <= maxValue:
			x = int(self.graphTLX + (value - minValue) * self.graphWidth / self.axis.displayDelta)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(x, self.graphBRY + 3, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(x, self.graphBRY + 1, 1, 1)
			self.ctx.fill()
			self.text.printText(self.ctx, (x, self.graphBRY + 5), self.textColor, '%u' % value, self.text.HORIZONTAL_CENTER_ALIGN | self.text.VERTICAL_TOP_ALIGN)
			value += stepValue
		columnHeight = self.graphHeight / self.sampleCount
		i = 0
		for point in self.points:
			y = int(self.graphTLY + i * columnHeight)
			self.ctx.set_source_rgb(*self.textColor)
			self.ctx.rectangle(self.graphTLX - 3, y, 1, 1)
			self.ctx.fill()
			self.ctx.rectangle(self.graphTLX - 1, y, 1, 1)
			self.ctx.fill()
			i += 1

	def computeLabelMargin(self):
		self.axis = Axis(self.yMinValue, self.yMaxValue)
		self.axis.computeBoundaries()
		self.graphTLX = int(self.margin + self.text.fontSize)
		self.graphTLY = int(self.margin + 4 * self.text.fontSize)
		self.graphBRX = int(self.graphTLX  + (self.width - 2 * self.margin) * self.chartRatio - 4 * self.text.fontSize)
		self.graphBRY = int(self.height - self.margin - self.text.fontSize)
		self.graphWidth = self.graphBRX - self.graphTLX + 1
		self.graphHeight = self.graphBRY - self.graphTLY + 1
		self.labelTLX = self.graphBRX + 4 * self.text.fontSize
		self.labelTLY = self.graphTLY

	def printBar(self):
		if not self.sampleCount:
			return;
		minValue = self.axis.displayMin
		maxValue = self.axis.displayMax
		stepValue = self.axis.tics
		columnHeight = int(self.graphHeight / self.sampleCount)
		i = 0
		for point in self.points:
			y = self.graphTLY + i * columnHeight
			value = point[1]
			xmin = int((value - minValue) * self.graphWidth / self.axis.displayDelta)
			self.text.printText(self.ctx, (self.graphTLX + xmin + self.text.fontSize * 0.5, y + columnHeight * 0.5), self.textColor, '%u' % value, self.text.HORIZONTAL_LEFT_ALIGN | self.text.VERTICAL_CENTER_ALIGN)
			y1 = y + self.text.fontSize * 0.5
			y2 = columnHeight - self.text.fontSize
			color = self.palette[i % len(self.palette)]
			self.ctx.set_source_rgb(*color)
			self.ctx.rectangle(self.graphTLX + 1, y1, xmin, y2)
			self.ctx.fill()
			if y2 > 2 * self.graphDepth:
				shadow = self.shadowPalette[i % len(self.palette)]
				self.ctx.set_source_rgb(*shadow)
				self.ctx.rectangle(self.graphTLX + 1, y1 + y2 - self.graphDepth, xmin, self.graphDepth)
				self.ctx.fill()
			for line in range(self.graphDepth):
				alpha = 0.5 - float(line) / float(2 * self.graphDepth)
				self.ctx.set_source_rgba(color[0], color[1], color[2], alpha)
				self.ctx.rectangle(self.graphTLX + 1, y1 + y2 + line, xmin, 1)
				self.ctx.fill()
			i += 1

if __name__ == '__main__':
	foo = VerticalComparativeBarChart(background = (0, 0, 0, 1), foreground = (1, 1, 1))
	foo.selectFont('Georgia', 10)
	foo.setTitle('Testowy wykres')
	foo.setGroupSize(3)
	foo.addGroup('mama')
	foo.addGroup('tata')
	foo.addGroup('wujek')
	foo.addPoint(('1111', 20))
	foo.addPoint(('2222', 30))
	foo.addPoint(('333', 40))
	foo.addPoint(('333', 50))
	foo.addPoint(('333', 40))
	foo.addPoint(('333', 30))
	foo.addPoint(('333', 60))
	foo.addPoint(('4444', 63))
	foo.addPoint(('55555', 70))
	foo.render(1000, 500, 'chart.png', margin = 1.0)
