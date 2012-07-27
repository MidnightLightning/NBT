import nbt.region
import Image, os, sys

if (len(sys.argv) == 1):
	print "No world folder specified!"
	sys.exit()

world_folder = sys.argv[1]
if (not os.path.exists(world_folder)):
	print "No such folder as "+filename
	sys.exit()

if (world_folder[-1] == '/'):
	world_folder = world_folder[:-1] # Trim trailing slash

regions = os.listdir(world_folder+'/region/')
min_x = 999999999
max_x = -999999999
min_z = 999999999
max_z = -999999999

for filename in regions:
	pieces = filename.split('.')
	rx = int(pieces[1])
	rz = int(pieces[2])
	if (rx < min_x):
		min_x = rx
	if (rx > max_x):
		max_x = rx
	if (rz < min_z):
		min_z = rz
	if (rz > max_z):
		max_z = rz

print min_x,max_x,min_z,max_z
delta_x = max_x - min_x +1
delta_z = max_z - min_z +1
if (delta_x < 1 or delta_z < 1):
	print "No chunks defined!"
	sys.exit()
print "World is",delta_x,'regions tall, and',delta_z,'regions wide'

map = Image.new('RGBA', (512*delta_z, 512*delta_x), (128,128,128,0))
for filename in regions:
	print "Parsing",filename,"..."
	pieces = filename.split('.')
	rx = int(pieces[1])
	rz = int(pieces[2])
	file = nbt.region.RegionFile(filename=world_folder+'/region/'+filename)
	sub = file.get_map()
	map.paste(sub, ((max_z-rz)*512, (rx-min_x)*512))
world_name = os.path.basename(world_folder)
map.save(world_name+'.png')
#map.show()