from nbt.mapbuilder import noise
import array, Image, time

def time_split(t1, label=None):
	t2 = time.clock()
	if (label != None):
		print "Elapsed time ("+label+")", round(t2-t1,3)
	else:
		print "Elapsed time:", round(t2-t1, 3)
	return t2

t1 = time.clock() # Start time

forest_loc = noise.octave_stack([8,8,1], 4, 0.4)
soil_depth = noise.es_clip(0.775, 0.02)
time_split(t1, 'Setup done')


size = 500,500
pixels = [0]*size[0]*size[1]
for y in range(size[1]):
	if (y % 50 == 0): time_split(t1, 'Y='+str(y))
	for x in range(size[0]):
		offset = x + y*size[0]
		v = forest_loc.getValue([x,y,0], [size[0], size[1], 1]) # Raw biome data
		v = soil_depth.getValue(v) # Get soil depth at that point		
		pixels[offset] = int(v*255)
pixels = array.array('B', pixels).tostring()
time_split(t1, 'Pixels complete')

im = Image.fromstring('L', size, pixels)
im.show()

t2 = time.clock()
print "Final time:", round(t2-t1, 3)
