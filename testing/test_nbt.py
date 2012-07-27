import nbt
from nbt.mapbuilder import utilities
from gzip import GzipFile
import os, sys

if (len(sys.argv) == 1):
	print "No NBT file specified!"
	sys.exit()

filename = sys.argv[1]
if (not os.path.exists(filename)):
	print "No such file as "+filename
	sys.exit()

gz = GzipFile(filename)
gz = gz.read()
print utilities.ByteToHex(gz)
file = nbt.NBTFile(filename=filename)
print file.pretty_tree()

