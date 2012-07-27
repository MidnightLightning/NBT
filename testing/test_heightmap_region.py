import nbt.region
import nbt.chunk
from nbt.mapbuilder import utilities
from struct import pack
import array, Image, os, sys

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


# Build a map of this region
map = file.get_heightmap_image()
map.show()
map.save('tmp.png')