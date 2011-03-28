import math

def ByteToHex(byteStr):
	return "".join(["%02X " % ord(x) for x in byteStr]).strip()

# Given a X,Y,Z tuple, what region file will this point be found in?
def which_region(coord):
	region_x = math.floor(coord[0]/16/32)
	region_z = math.floor(coord[2]/16/32)
	return region_x,region_z

# Given a X,Y,Z tuple, what chunk will this point be found in?
def which_chunk(coord):
	chunk_x = math.floor(coords[0]/16)
	chunk_z = math.floor(coords[2]/16)
	return chunk_x,chunk_z

# Create a blank region file
# Effectively an 8kiB file of zeros
def blank_region(filename):
	f = open(filename, 'w')
	f.seek(8191)
	f.write(chr(0))
	f.close()

# Draw a circle of a given radius and center, in the block dictionary, using the given block type (defaults to stone)
def draw_disk(center, diameter, blocks, block_id=1, fill_air=False):
	radius = diameter/2
	extents = radius
	if (diameter % 2 == 0):
		# diameter is even; center of disk is a point between blocks, the lower-southwest corner of the "center" coordinate given
		center = (center[0]+0.5, center[1], center[2]+0.5)
		extents += 0.5
	#print "Center: "+str(center[0])+","+str(center[1])+","+str(center[2])+"; Extents: "+str(extents)
	#print "Range: "+str(center[0]-extents)+","+str(center[0]+extents)
	for x in range(int(center[0]-extents), int(center[0]+extents)+1):
		for z in range(int(center[2]-extents), int(center[2]+extents)+1):
			if (math.sqrt(math.pow(x-center[0],2)+math.pow(z-center[2],2)) <= radius):
				# This point is inside the disk
				blocks[(x,center[1],z)] = block_id
			else:
				# This point is outside the disk
				if fill_air:
					blocks[(x,center[1],z)] = 0
	return blocks

# Draw a filled sphere of a given radius at center, the block dictionary, using the given block type (defaults to stone)
def draw_sphere(center, diameter, blocks, block_id=1, fill_air=False):
	radius = diameter/2
	extents = radius
	if (diameter % 2 == 0):
		# diameter is even; center of sphere is a point between blocks, the lower-southwest corner of the "center" coordinate given
		center = (center[0]+0.5, center[1]-0.5, center[2]+0.5)
		extents += 0.5
	for x in range(int(center[0]-extents), int(center[0]+extents)):
		for y in range(int(center[1]-extents), int(center[1]+extents)):
			for z in range(int(center[2]-extents), int(center[2]+extents)):
				if (math.sqrt(math.pow(x-center[0],2)+math.pow(y-center[1],2)+math.pow(z-center[2],2)) <= radius):
					# This point is inside the disk
					blocks[(x,y,z)] = block_id
				else:
					# This point is outside the disk
					if fill_air:
						blocks[(x,y,z)] = 0
	return blocks

def fill_blocks(start, end, blocks, block_id=1):
	for x in range(start[0], end[0]+1):
		for y in range(start[1], end[1]+1):
			for z in range(start[2], end[2]+1):
				blocks[(x,y,z)] = block_id
	return blocks