import math, random
import time

try:
	import Image
	PIL_enabled = True
except ImportError:
	PIL_enabled = False

#random.seed('FortyTwo') # Static seed such that it will be the same each time this script is run

class perlin_noise(object):
	def __init__(self, dimensions, scale=1, shift=0.0):
		while (len(dimensions) < 3):
			dimensions.append(1)
		self.points = []
		for x in range(dimensions[0]):
			for y in range(dimensions[1]):
				for z in range(dimensions[2]):
					self.points.append(random.random())
		self.dimensions = dimensions
		self.scale = scale
		self.shift = shift
	
	def _smooth(self, point1, point2, ratio):
		# Cosine interpolation between given point values
		ft = ratio * math.pi
		f = (1-math.cos(ft))*0.5
		return point1*(1-f) + point2*f
	
	def getPoint(self, x=0, y=0, z=0):
		coord = (x,y,z)
		index = x + y*self.dimensions[0] + z*self.dimensions[0]*self.dimensions[1]
		#print "Coord:",coord, "Index:",index
		return self.points[index]
	
	def getValue(self, coord, space):
		# Get value at "coord", assuming noise space is "space" dimensions
		while (len(coord) < 3):
			coord.append(0.0)
		while (len(space) < 3):
			space.append(1)
		# Translate into local space
		local_x = (coord[0]+0.0)/(space[0]-1)*(self.dimensions[0]-1) if (space[0] > 1) else 0.0
		local_y = (coord[1]+0.0)/(space[1]-1)*(self.dimensions[1]-1) if (space[1] > 1) else 0.0
		local_z = (coord[2]+0.0)/(space[2]-1)*(self.dimensions[2]-1) if (space[2] > 1) else 0.0
		
		# If any local coordinate is an integer value, no need to interpolate
		z1 = int(local_z)
		z2 = z1+1 if (math.floor(local_z) != local_z) else z1
		
		y1 = int(local_y)
		y2 = y1+1 if (math.floor(local_y) != local_y) else y1
		
		x1 = int(local_x)
		x2 = x1+1 if (math.floor(local_x) != local_x) else x1
		
		local_coord = (local_x,local_y,local_z)
		#print "Coord:",coord, "Space:",space, "Dimensions:",self.dimensions, "Local:",local_coord,"X:",x1,x2, "Y:",y1,y2, "Z:",z1,z2
		
		if (z1 == z2):
			# No need to interpolate Z layer
			if (y1 == y2):
				if (x1 == x2):
					# No interpolation needed!
					raw = self.getPoint(x1,y1,z1)
				else:
					# Only interpolate X
					raw = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x2, y1, z1), local_x-x1)
			else:
				if (x1 == x2):
					# Only interpolate Y
					raw = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x1, y2, z1), local_y-y1)
				else:
					# Interpolate X/Y
					y1_blend = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x2, y1, z1), local_x-x1)
					y2_blend = self._smooth(self.getPoint(x1, y2, z1), self.getPoint(x2, y2, z1), local_x-x1)
					raw = self._smooth(y1_blend, y2_blend, local_y-y1)
		else:
			if (y1 == y2):
				if (x1 == x2):
					# Only interpolate Z
					raw = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x1, y1, z2), local_z-z1)
				else:
					# Interpolate X/Z
					z1_blend = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x2, y1, z1), local_x-x1)
					z2_blend = self._smooth(self.getPoint(x1, y1, z2), self.getPoint(x2, y1, z2), local_x-x1)
					raw = self._smooth(z1_blend, z2_blend, local_z-z1)
			else:
				if (x1 == x2):
					# Interpolate Y/Z
					z1_blend = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x1, y2, z1), local_y-y1)
					z2_blend = self._smooth(self.getPoint(x1, y1, z2), self.getPoint(x1, y2, z2), local_y-y1)
					raw = self._smooth(z1_blend, z2_blend, local_z-z1)
				else:
					# Interpolate X/Y/Z
					# Interpolate X values for surrounding Y values
					y1_blend = self._smooth(self.getPoint(x1, y1, z1), self.getPoint(x2, y1, z1), local_x-x1)
					y2_blend = self._smooth(self.getPoint(x1, y2, z1), self.getPoint(x2, y2, z1), local_x-x1)
					z1_blend = self._smooth(y1_blend, y2_blend, local_y-y1)
					
					# Repeat for second Z layer
					y1_blend = self._smooth(self.getPoint(x1, y1, z2), self.getPoint(x2, y1, z2), local_x-x1)
					y2_blend = self._smooth(self.getPoint(x1, y2, z2), self.getPoint(x2, y2, z2), local_x-x1)
					z2_blend = self._smooth(y1_blend, y2_blend, local_y-y1)
					
					# Blend the two Z layers together
					raw = self._smooth(z1_blend, z2_blend, local_z-z1)
		return (raw*self.scale)+self.shift
		
	def showSlice(self, z, size=(50,50)):
		if (not PIL_enabled): return false
		pixels = ""
		for y in range(size[1]):
			for x in range(size[0]):
				value = self.getValue([x,y,z], [size[0], size[1], self.dimensions[2]])
				pixels += chr(int( (value-self.shift)/self.scale*255 ))
		im = Image.fromstring('L', size, pixels)
		im.show()

# A wrapper for several noise objects stacked together, to make finer-grained, yet continuous noise
class noise_stack(object):
	def __init__(self, noises=None):
		self.noises = []
		if (noises != None):
			# Add these noises to the stack
			# 'noises' is a list of dictionaries
			self.noises = noises

	def add(self, noise, weight):
		self.noises.append({
			'noise': noise,
			'weight': weight
		})
	
	def getValue(self, point, size):
		tot_weight = 0
		tot_value = 0.0
		for n in self.noises:
			tot_value += n['noise'].getValue(point,size)*n['weight']
			tot_weight += n['weight']
		return tot_value/tot_weight
	
	def showSlice(self, z, size=(50,50)):
		if (not PIL_enabled): return false
		pixels = ""
		for y in range(size[1]):
			for x in range(size[0]):
				value = self.getValue([x,y,z], [size[0], size[1], self.noises[0]['noise'].dimensions[2]])
				pixels += chr(int(value*255))
		im = Image.fromstring('L', size, pixels)
		im.show()
		

# Auto-generate a stack of perlin noise functions, where the granularity of the noise function doubles each octave, and the weight of that octave is persistence ** octave
class octave_stack(noise_stack):
	def __init__(self, dimensions, octaves, persistence):
		while (len(dimensions) < 3):
			dimensions.append(1)
		self.noises = []
		start_weight = 10
		for i in range(octaves):
			cur_dims = (dimensions[0] * 2**i, dimensions[1] * 2**i, dimensions[2] * 2**i)
			cur_weight = start_weight * persistence**i
			self.add(perlin_noise(cur_dims), cur_weight)

class gradient(object):
	def __init__(self, points={}):
		self.points = points # A dictionary of values
		if (not '0.0' in self.points.keys()): self.points['0.0'] = 0.0 # Add end points if not given
		if (not '1.0' in self.points.keys()): self.points['1.0'] = 1.0
	
	def getValue(self, point):
		if (str(point) in self.points.keys()):
			# This is a literal point in the defined gradient
			return self.points[str(point)]
		else:
			# Interpolate this point from the given points
			lower_point = 0.0
			upper_point = 1.0
			for coord in self.points.keys():
				coord = float(coord)
				if (coord < point and coord > lower_point):
					lower_point = coord
				if (coord > point and coord < upper_point):
					upper_point = coord
			#print point,'not literally given; interpolating:',"Lower:", lower_point, 'Upper:', upper_point
			lower_value = self.points[str(lower_point)]
			upper_value = self.points[str(upper_point)]
			ratio = (point-lower_point)/(upper_point-lower_point)
			value_delta = upper_value - lower_value
			return value_delta*ratio+lower_value
	
	# Change all the points to their inverses
	def invert(self):
		new_points = {}
		for key,value in self.points.items():
			new_points[key] = 1-value
		self.points = new_points
	
	# Mirror image of the gradient
	def flip(self):
		new_points = {}
		for key,value in self.points.items():
			new_key = 1-float(key)
			new_points[str(new_key)] = value
		self.points = new_points
	
	def show(self, size=(300,10)):
		if (not PIL_enabled): return false
		pixels = ""
		for y in range(size[1]):
			for x in range(size[0]):
				local_x = (x+0.0)/size[0]
				value = self.getValue(local_x)
				pixels += chr(int(value*255))
		im = Image.fromstring('L', size, pixels)
		im.show()

# Create a gradient that is zero up to a certain point, then filters to one beyond that
class low_clip(gradient):
	def __init__(self, threshold):
		if (threshold <= 0 or threshold >= 1): return False
		self.points = {
			'0.0': 0,
			str(threshold): 0,
			'1.0': 1
		}

# Create a gradient that filters up to one at a certain point and is one beyond that
class high_clip(gradient):
	def __init__(self, threshold):
		if (threshold <= 0 or threshold >= 1): return False
		self.points = {
			'0.0': 0,
			str(threshold): 1,
			'1.0': 1
		}

# Create a gradient that is one around a certain point, and falls off after a given threshold
class local_clip(gradient):
	def __init__(self, point, range):
		low_clip = point-range
		high_clip = point+range
		low_value = 0
		high_value = 0
		if (low_clip < 0):
			low_value = (low_clip*-1)/range
		if (high_clip > 1):
			high_value = (high_clip-1)/range
		self.points = {
			'0.0':low_value,
			str(point): 1,
			'1.0':high_value
		}
		if (high_clip < 1.0): self.points[str(high_clip)] = 0
		if (low_clip > 0.0): self.points[str(low_clip)] = 0

# Create a gradient of all zeroes up to a certain point, and then all ones from that point and beyond
# point <  threshold => 0
# point >= threshold => 1
class hard_clip(gradient):
	def __init__(self, threshold):
		if (threshold <= 0 or threshold >= 1): return False
		self.points = {
			'0.0': 0,
			str(threshold-0.0000000000000001): 0,
			str(threshold): 1,
			'1.0': 1
		}

# Create a gradient of all zeroes up to a certain point, and all ones after, with a gradiated bit in the middle
# point = threashold => 0.5
class es_clip(gradient):
	def __init__(self, point, range):
		low_clip = point-range
		high_clip = point+range
		low_value = 0
		high_value = 1
		if (low_clip < 0):
			low_value = (low_clip*-1)/range
		if (high_clip > 1):
			high_value = (1-high_clip)/range
		self.points = {
			'0.0':low_value,
			str(point): 0.5,
			'1.0':high_value
		}
		if (high_clip < 1.0): self.points[str(high_clip)] = 1
		if (low_clip > 0.0): self.points[str(low_clip)] = 0
