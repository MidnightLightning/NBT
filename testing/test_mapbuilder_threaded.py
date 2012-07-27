from nbt.mapbuilder import noise
import array, Image, multiprocessing, time

def do_work(offset):
	# offset = x + y*size[0]
	x = offset % size[0]
	y = (offset-x)/size[0]
	
	v = forest_loc.getValue([x,y,0], [size[0], size[1], 1]) # Raw biome data
	v = soil_depth.getValue(v) # Get soil depth at that point

	return int(v*255)
	


if __name__ == '__main__': # Only if we're the parent thread
	def time_split(t1, label=None):
		t2 = time.time()
		if (label != None):
			print "Elapsed time ("+label+")", round(t2-t1,3), 'seconds'
		else:
			print "Elapsed time:", round(t2-t1, 3), 'seconds'
		return t2
	
	t1 = time.time() # Start time
	
	forest_loc = noise.octave_stack([16,16,1], 4, 0.4)
	soil_depth = noise.es_clip(0.775, 0.02)

	size = 2048,2048
	num_pixels = size[0]*size[1]
	
	time_split(t1, 'Setup done')

	p = multiprocessing.Pool() # Number of processes equal to number of cores on computer
	print "Pool created with",multiprocessing.cpu_count(),"processes"
	rs = p.map_async(do_work, xrange(num_pixels), size[1])
	p.close() # Done adding tasks
	#print rs.__dict__
	while (True):
		if (rs.ready()): break # Done with iteration
		num_done = num_pixels-rs._number_left
		percent = (num_done+0.0)/num_pixels
		label = "{0:0.4%} complete".format(percent)
		time_split(t1, label)
		time.sleep(1)
	p.join() # Ensure completion before continuing
	
	pixels = array.array('B', rs.get()).tostring() # rs is a multiprocessing.pool.IMapUnorderedIterator object, but apparently acts enough like a list for array.array()'s purposes
	time_split(t1, 'Pixels complete')
	
	im = Image.fromstring('L', size, pixels)
	im.show()
	
	t2 = time.time()
	print "Final time:", round(t2-t1, 3)