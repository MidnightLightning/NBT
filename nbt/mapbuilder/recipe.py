from nbt.region import RegionFile
from nbt.chunk import BlockArray
import math, os

class block_recipe:
	def __init__(self):
		self.blocks = {} # empty dictionary
		self.max_x = None
		self.max_y = None
		self.max_z = None
		self.min_x = None
		self.min_y = None
		self.min_z = None
	
	def add_block(self, coord, block_id):
		if (len(coord) != 3):
			raise Exception('Not a valid coordinate')
		
		self.blocks[coord] = block_id # Save the block assignment
		
		# Update extents
		if (self.min_x == None or coord[0] < self.min_x):
			self.min_x = coord[0]
		if (self.max_x == None or coord[0] > self.max_x):
			self.max_x = coord[0]
		if (self.min_y == None or coord[1] < self.min_y):
			self.min_y = coord[1]
		if (self.max_y == None or coord[1] > self.max_y):
			self.max_y = coord[1]
		if (self.min_z == None or coord[2] < self.min_z):
			self.min_z = coord[2]
		if (self.max_z == None or coord[2] > self.max_z):
			self.max_z = coord[2]
	
	def get_extents(self):
		min = self.min_x, self.min_y, self.min_z
		max = self.max_x, self.max_y, self.max_z
		return min,max
	
	def get_volume(self):
		min,max = self.get_extents()
		delta_x = abs(max[0]-min[0])+1
		delta_y = abs(max[1]-min[1])+1
		delta_z = abs(max[2]-min[2])+1
		#print str(delta_x)+","+str(delta_y)+","+str(delta_z)
		return delta_x*delta_y*delta_z
		
	def get_size(self):
		min,max = self.get_extents()
		return (abs(max[0]-min[0])+1, abs(max[1]-min[1])+1, abs(max[2]-min[2])+1)
		
	def apply(self, point, blocks=None, world_folder=None, fill_air=False):
		if blocks:
			return self._apply_dict(blocks, point, fill_air)
		elif world_folder:
			return self._apply_world(world_folder, point, fill_air)
		else:
			return False
	
	def _apply_dict(self, blocks, point, fill_air=False):
		# Copy the recipe into the "blocks" block dictionary, discarding those that don't fit in a single chunk of blocks
		size = self.get_size()
		for x in range(self.min_x, self.min_x+size[0]):
			for y in range(self.min_y, self.min_y+size[1]):
				for z in range(self.min_z, self.min_z+size[2]):
					world_x = point[0]+x
					world_y = point[1]+y
					world_z = point[2]+z
					if (world_x >= 0 and world_x < 16 and world_y >= 0 and world_y < 128 and world_z >= 0 and world_z < 16):
						if (self.blocks[(x,y,z)] > 0 or fill_air):
							blocks[(world_x, world_y, world_z)] = self.blocks[(x,y,z)]
		return blocks
	
	def _apply_world(self, world_folder, point, fill_air=False):
		# Copy the recipe into the regions in the given world folder
		if (not os.path.exists(world_folder)):
			return False
		if (not os.path.exists(world_folder+"/region")):
			return False
			
		# Recipe extents in world coordinates
		recipe_min_world = (point[0]+self.min_x, point[1]+self.min_y, point[2]+self.min_z)
		recipe_max_world = (point[0]+self.max_x, point[1]+self.max_y, point[2]+self.max_z)
		
		# Find north-east-most chunk affected by this recipe
		chunk_min_x = int(math.floor(recipe_min_world[0]/16))
		chunk_min_z = int(math.floor(recipe_min_world[2]/16))
		
		# Find south-west-most chunk affected by this recipe
		chunk_max_x = int(math.floor(recipe_max_world[0]/16))
		chunk_max_z = int(math.floor(recipe_max_world[2]/16))
		
		for chunk_x in range(chunk_min_x, chunk_max_x+1):
			for chunk_z in range(chunk_min_z, chunk_max_z+1):
				# Ensure chunk exists in region file and fetch it
				region_x = int(math.floor(chunk_x/32))
				region_z = int(math.floor(chunk_z/32))
				region_filename = world_folder+"/region/r."+str(region_x)+"."+str(region_z)+".mcr"
				if (not os.path.exists(region_filename)):
					continue # Skip this chunk
				f = RegionFile(filename=region_filename)
				chunk_data = f.get_chunk(chunk_x, chunk_z)
				if (chunk_data == None):
					continue # This chunk is not generated
				chunk_blocks = BlockArray(chunk_data['Level']['Blocks'].value, chunk_data['Level']['Data'].value)
				
				# Find region where recipe and this chunk overlap
				int_min_x = recipe_min_world[0] if (chunk_x*16 < recipe_min_world[0]) else chunk_x*16
				int_min_z = recipe_min_world[2] if (chunk_z*16 < recipe_min_world[2]) else chunk_z*16
				int_min = (int_min_x, recipe_min_world[1], int_min_z)
				
				int_max_x = recipe_max_world[0] if (chunk_x*16+15 > recipe_max_world[0]) else chunk_x*16+15
				int_max_z = recipe_max_world[2] if (chunk_z*16+15 > recipe_max_world[2]) else chunk_z*16+15
				int_max = (int_max_x, recipe_max_world[1], int_max_z)
				
				# Loop through intersecting region and apply recipe
				for x in range(int_min[0], int_max[0]+1):
					for y in range(int_min[1], int_max[1]+1):
						for z in range(int_min[2], int_max[2]+1):
							recipe_coord = (x-point[0], y-point[1], z-point[2]) # Where in the local recipe block array are we
							chunk_coord = (x % 16, y, z % 16) # Where in this chunk are we
							if (recipe_coord in self.blocks):
								if (self.blocks[recipe_coord] != 0 or fill_air):
									chunk_blocks.set_block(chunk_coord[0], chunk_coord[1], chunk_coord[2], self.blocks[recipe_coord])

				# Save the chunk to the region file
				chunk_data['Level']['Blocks'].value = chunk_blocks.get_blocks_byte_array()
				chunk_data['Level']['Data'].value = chunk_blocks.get_data_byte_array()
				chunk_data['Level']['HeightMap'].value = chunk_blocks.get_heightmap()
				f.write_chunk(chunk_x, chunk_z, chunk_data)
		return True
