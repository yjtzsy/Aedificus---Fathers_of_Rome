import my, pygame, random, math
from pygame.locals import *
pygame.init()


def loadTerrainImgs(buildingNames):
	"""Load terrain .png's from assets/buildings/ when given a ist of names"""
	imgs = {}
	for name in buildingNames:
		imgs[name] = (pygame.image.load('assets/buildings/' + name + '.png').convert_alpha())
	return imgs


class Map:
	TERRAIN = ['tree', 'grass']
	IMGS = loadTerrainImgs(TERRAIN)
	def __init__(self):
		self.genBlankStructure()
		self.surf = self.genSurf()


	def genBlankStructure(self):
		self.map = []
		for x in range(my.MAPXCELLS):
			row = []
			for y in range(my.MAPYCELLS):
				tile = 'grass'
				if random.randint(0, my.TREEFREQUENCY) == 0:
					tile = 'tree'
				row.append(tile)
			self.map.append(row)


	def genSurf(self):
		surf = pygame.Surface((my.MAPWIDTH, my.MAPHEIGHT))
		for x in range(my.MAPXCELLS):
			for y in range(my.MAPYCELLS):
				tile = self.map[x][y]
				if tile not in Map.TERRAIN:
					tile = 'grass'
				surf.blit(Map.IMGS[tile], (x * my.CELLSIZE, y * my.CELLSIZE))
		my.updateSurf = True
		return surf


	def screenToGamePix(self, pixels):
		"""Given a tuple of screen pixel coords, returns corresponding game surf coords"""
		x, y = pixels
		rectx, recty = my.camera.viewArea.topleft
		return (x + rectx, y + recty)


	def pixelsToCell(self, pixels):
		"""Given a tuple of game surf coords, returns the occupied cell's (x, y)"""
		x, y = pixels
		return int(math.floor(x / my.CELLSIZE)), int(math.floor(y / my.CELLSIZE))


	def cellsToPixels(self, coords):
		"""Given a tuple of my.map.map coords, returns the pixel coords of the cell's topleft"""
		x, y = coords
		return (x * my.CELLSIZE, y * my.CELLSIZE)


	def screenToCellCoords(self, pixels):
		"""Given a tuple of screen surf coords, returns the occupied cell's (x, y)"""
		gamex, gamey = self.screenToGamePix(pixels)
		return self.pixelsToCell((gamex, gamey))


	def screenToCellType(self, pixels):
		"""Given a tuple of screen surf coords, returns the occupied cell's type"""
		coords = self.screenToCellCoords(pixels)
		return self.cellType(coords)


	def cellType(self, coords):
		"""Given a tuple of map coords, returns the cell's type"""
		x, y = coords
		return self.map[x][y]


	def distanceTo(self, start, end):
		"""Distance from cell A to cell B. Look at me, using PYTHAGORUS like a real man."""
		startx, starty = start
		endx, endy =  end
		return math.sqrt(math.pow(math.fabs(endx - startx), 2)
						 + math.pow(math.fabs(endy - starty), 2))


	def findNearestBuildings(self, coords, buildingGroup):
		"""Returns a list of buildings specified, in ascending order of distance"""
		if len(buildingGroup.sprites()) == 0:
			return None
		buildings = []
		distances = []
		for building in buildingGroup.sprites():
			distance = self.distanceTo(coords, building.coords)
			for i in range(len(buildings)):
				if distances[i] < distance:
					if i == len(buildings):
						buildings.append(building)
						distances.append(distance)
				elif distances[i] >= distance:
					buildings.insert(i, building)
					distances.insert(i, distance)
			if len(buildings) == 0:
				buildings.append(building)
				distances.append(distance)
		return buildings



class Camera:
	"""Allows for a scrolling game view, and camera shake."""
	def __init__(self):
		self.viewArea = pygame.Rect((0, 0), (my.WINDOWWIDTH, my.WINDOWHEIGHT))
		self.width = my.WINDOWWIDTH
		self.shake = 0
		self.focus = (0, 0)
		self.xVel, self.yVel = 0, 0


	def update(self):
		"""Updates camera pos and shake, and blits the to my.screen"""
		x, y = self.focus
		# ACELLERATE X
		if K_RIGHT in my.input.pressedKeys or K_d in my.input.pressedKeys:
			if self.xVel < 0: self.xVel = 0
			self.xVel += my.SCROLLACCEL
			if self.xVel > my.MAXSCROLLSPEED: xVel = my.MAXSCROLLSPEED
		elif K_LEFT in my.input.pressedKeys or K_a in my.input.pressedKeys:
			if self.xVel > 0: self.xVel = 0
			self.xVel -= my.SCROLLACCEL
			if self.xVel < -my.MAXSCROLLSPEED: xVel = -my.MAXSCROLLSPEED
		# DECELLERATE X
		elif self.xVel > -my.SCROLLDRAG and self.xVel < my.SCROLLDRAG:
			self.xVel = 0
		elif self.xVel > 0:
			self.xVel -= my.SCROLLDRAG
		elif self.xVel < 0:
			self.xVel += my.SCROLLDRAG
		x += self.xVel
		# ACELLERATE Y
		if K_DOWN in my.input.pressedKeys or K_s in my.input.pressedKeys:
			if self.yVel < 0: self.yVel = 0
			self.yVel += my.SCROLLACCEL
			if self.yVel > my.MAXSCROLLSPEED: yVel = my.MAXSCROLLSPEED
		elif K_UP in my.input.pressedKeys or K_w in my.input.pressedKeys:
			if self.yVel > 0: self.yVel = 0
			self.yVel -= my.SCROLLACCEL
			if self.yVel < -my.MAXSCROLLSPEED: yVel = -my.MAXSCROLLSPEED
		# DECELLERATE Y
		elif self.yVel > -my.SCROLLDRAG and self.yVel < my.SCROLLDRAG:
			self.yVel = 0
		elif self.yVel > 0:
			self.yVel -= my.SCROLLDRAG
		elif self.yVel < 0:
			self.yVel += my.SCROLLDRAG
		y += self.yVel
		# UPDATE SELF.VIEWAREA AND BLIT
		self.focus = (x, y)
		self.viewArea.center = self.focus
		if self.viewArea.top < 0:
			self.viewArea.top = 0
			self.yVel = my.MAPEDGEBOUNCE
		elif self.viewArea.bottom > my.map.surf.get_height():
			self.viewArea.bottom = my.map.surf.get_height()
			self.yVel = -my.MAPEDGEBOUNCE
		if self.viewArea.left < 0:
			self.viewArea.left = 0
			self.xVel = my.MAPEDGEBOUNCE
		elif self.viewArea.right > my.map.surf.get_width():
			self.viewArea.right = my.map.surf.get_width()
			self.xVel = -my.MAPEDGEBOUNCE
		my.screen.blit(my.surf, (0,0), self.viewArea)


	def shake(self, intensity):
		pass

