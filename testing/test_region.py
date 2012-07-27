import nbt.region
from nbt.chunk import Chunk
from nbt.mapbuilder import utilities
import Image, os, sys

if (len(sys.argv) == 1):
	print "No region file specified!"
	sys.exit()

filename = sys.argv[1]
if (not os.path.exists(filename)):
	print "No such file as "+filename
	sys.exit()

file = nbt.region.RegionFile(filename=filename)
#for c in file.get_chunks():
#	print c
	
chunk_nbt = file.get_chunk(0,0)
chunk = Chunk(chunk_nbt)
#print chunk.blocks.get_blocks_struct()
#print chunk.blocks.get_all_data()
print "The block at (0,60,0) is: "+str(chunk.blocks.get_block(0,60,0))
print chunk_nbt.pretty_tree()

im = chunk.get_heightmap_image()
im.show()