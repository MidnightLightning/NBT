from nbt.mapbuilder import noise
from nbt.mapbuilder import utilities
from nbt.region import RegionFile
from nbt.chunk import BlockArray
from nbt import *
from math import ceil
import array, Image, multiprocessing, os, sys, time

def get_soil_depth(world_x, world_z):
	z = world_z
	x = world_x
	
	v = forest_loc.getValue([x,0,z], [size[1], 1, size[0]]) # Raw biome data
	v = soil_depth.getValue(v) # Get soil depth at that point

	return int(v*255)
	
def get_block(task):
	x = task['x']
	y = task['y']
	z = task['z']
	
	air_clip = 0.5 # ground is half the height of the world
	dirt_clip = 0.45
	min_terrain_height = 50
	ground_turb_ratio = 0.02
	
	
	h = ground_height.getValue(y/128.0)
	if (y >= min_terrain_height):
		# Normal terrain depth doesn't go below level 50. From 50-128 turbulence applies
		t = ground_turb.getValue([x,y-min_terrain_height,z], [size[1], 128-min_terrain_height, size[0]])
		t = (t*2)-1 # Change from 0-1 to -1-1
		h = h + (t*ground_turb_ratio)
	if (h < dirt_clip):
		return 1 # Stone
	elif (h < air_clip):
		return 3 # Dirt
	else:
		return 0 # Air
	

if __name__ == '__main__': # Only if we're the parent thread
	def time_split(t1, label=None):
		t2 = time.time()
		if (label != None):
			print "Elapsed time ("+label+")", round(t2-t1,3), 'seconds'
		else:
			print "Elapsed time:", round(t2-t1, 3), 'seconds'
		return t2
	
	t1 = time.time() # Start time

	# Create world folder
	world_folder = "dynamic"
	if (os.path.exists(world_folder)):
		print "Folder already exists at "+world_folder
		sys.exit()
	os.mkdir(world_folder)
	os.mkdir(world_folder+"/region")

	chunk_width = 32
	chunk_height = 4
	size = chunk_width*16,chunk_height*16 # Dimensions of the world
	max_dim = size[0] if (size[0] >= size[1]) else size[1]
	
	# Create level.dat
	level_nbt = utilities.blank_level_nbt(world_folder, int(size[1]/2), 64, int(size[0]/2))
	level_nbt.write_file(world_folder+"/level.dat")
	
	forest_loc = noise.octave_stack([max_dim/128,1,max_dim/128], 4, 0.4)
	soil_depth = noise.es_clip(0.775, 0.02)
	
	ground_turb = noise.octave_stack([max_dim/128,4,max_dim/128], 4, 0.25)
	ground_height = noise.gradient() # Default gradient, from zero to one
	
	# Create the world with the origin in the NE corner and extend into positive space
	num_x_regions = int(ceil(size[1]/512.0))
	num_z_regions = int(ceil(size[0]/512.0))
	
	p = multiprocessing.Pool() # Number of processes equal to number of cores on computer
	print "Pool created with",multiprocessing.cpu_count(),"processes"
	time_split(t1, 'Setup done')

	for region_x in range(num_x_regions):
		for region_z in range(num_z_regions):
			time_split(t1, 'Starting region ('+str(region_x)+','+str(region_z)+')')
			region_filename = world_folder+'/region/r.'+str(region_x)+'.'+str(region_z)+'.mcr'
			utilities.blank_region(region_filename)
			region = RegionFile(region_filename)

			for chunk_x in range(32):
				for chunk_z in range(32):
					world_x = chunk_x*16 + region_x*512
					world_z = chunk_z*16 + region_z*512
					if (world_x >= size[1] or world_z >= size[0]): 
						break # Jump to next chunk if outside the range of the world

					time_split(t1, 'Starting chunk ('+str(chunk_x)+','+str(chunk_z)+')')
					chunk_nbt = utilities.blank_chunk_nbt(chunk_x, chunk_z)
					blocks = [] # List of final block IDs
					for local_x in range(16):
						for local_z in range(16):
							world_x = local_x + chunk_x*16 + region_x*512
							world_z = local_z + chunk_z*16 + region_z*512
							
							soil_depth = p.apply(get_soil_depth, (world_x, world_z))
							
							tasks = []					
							for local_y in range(128):
								tasks.append({'x':world_x, 'z':world_z, 'y':local_y})
							rs = p.map_async(get_block, tasks)
							rs.wait(10) # Wait for the column to calculate
							blocks.extend(rs.get()) # Add blocks to listing

					if (len(blocks) > 0): # Write chunk, if it has any blocks in it
						#print blocks
						block_array = BlockArray()
						block_array.set_blocks(list=blocks)
						block_buffer = block_array.get_blocks_byte_array(buffer = True)
						chunk_nbt['Level']['Blocks'] = TAG_Byte_Array(name="Blocks", buffer=block_buffer)
						data_buffer = block_array.get_data_byte_array(buffer=True)
						chunk_nbt['Level']['Data'] = TAG_Byte_Array(name="Data", buffer=data_buffer)
						heightmap_buffer = block_array.generate_heightmap(buffer=True)
						chunk_nbt['Level']['HeightMap'] = TAG_Byte_Array(name="HeightMap", buffer=heightmap_buffer)
						region.write_chunk(chunk_x,chunk_z, chunk_nbt)
	
	t2 = time.time()
	print "Final time:", round(t2-t1, 3)