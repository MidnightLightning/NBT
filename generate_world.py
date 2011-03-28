from nbt import *
from nbt.mapbuilder import utilities
from nbt.region import RegionFile
from nbt.chunk import BlockArray
from struct import pack
from StringIO import StringIO
import argparse, array, os, random, sys, time

# Set up CLI parameters
parser = argparse.ArgumentParser(description="Generate a Minecraft World")
parser.add_argument('name', metavar='Name', nargs='?', help="Name of the world folder")
parser.add_argument('-d','--directory', default='./', help="Directory the world folder will be created in. Defaults to current directory")
parser.add_argument('-x','--width', type=int, default=2, help="Number of chunks east-west to create")
parser.add_argument('-z','--height', type=int, default=2, help="Number of chunks north-south to create")
args = parser.parse_args()

# Create world folder
if (args.name == None):
	print "No world name supplied!"
	parser.print_help()
	sys.exit()
	
world_folder = args.directory+args.name
if (os.path.exists(world_folder)):
	print "Folder already exists at "+world_folder
	sys.exit()
os.mkdir(world_folder)

# Create a region file
# http://www.minecraftwiki.net/wiki/Beta_Level_Format#Region_Files
os.mkdir(world_folder+"/region")
region_x = 0
region_z = 0
region_filename = world_folder+'/region/r.'+str(region_x)+'.'+str(region_z)+'.mcr'
utilities.blank_region(region_filename)
region = RegionFile(region_filename)

# Create chunk blocks
blocks = BlockArray() # Generate empty
chunk_blocks = {}
chunk_blocks = utilities.fill_blocks((0,0,0), (15,0,15), chunk_blocks, 7) # Make bedrock floor
chunk_blocks[(0,1,0)] = 1 # Stone grid marker
blocks.set_blocks(dict=chunk_blocks)

blocks_byte = blocks.get_blocks_byte_array(buffer=True)
data_byte = blocks.get_data_byte_array(buffer=True)
heightmap = blocks.get_heightmap(buffer=True)


# Create empty byte array buffers
blocklight_bytes = []
skylight_bytes = []
for i in range(2048):
	blocklight_bytes.extend([0,0,0,0,0,0,0,0])
	skylight_bytes.extend([255,255,255,255,255,255,255,255])

length = len(blocklight_bytes)
blocklight_bytes = pack(">i", length)+array.array('B', blocklight_bytes).tostring()
length = len(skylight_bytes)
skylight_bytes = pack(">i", length)+array.array('B', skylight_bytes).tostring()


for x in range(args.width):
	for z in range(args.height):
		chunk = NBTFile() # Blank NBT
		# Rewind reused buffers
		blocks_byte.seek(0)
		data_byte.seek(0)
		heightmap.seek(0)
		
		level = TAG_Compound()
		level.name = "Level"
		level.tags.extend([
			TAG_Byte(name="TerrainPopulated", value=1),
			TAG_Int(name="xPos", value=x),
			TAG_Int(name="zPos", value=z),
			TAG_Long(name="LastUpdate", value=0),
			TAG_Byte_Array(name="BlockLight", buffer=StringIO(blocklight_bytes)),
			TAG_Byte_Array(name="Blocks", buffer=blocks_byte),
			TAG_Byte_Array(name="Data", buffer=data_byte),
			TAG_Byte_Array(name="SkyLight", buffer=StringIO(skylight_bytes)),
			TAG_Byte_Array(name="HeightMap", buffer=heightmap),
			TAG_List(name="Entities", type=TAG_Compound),
			TAG_List(name="TileEntities", type=TAG_Compound)
		])
		chunk.tags.append(level)
		region.write_chunk(x,z, chunk)

# Create a level.dat
# http://www.minecraftwiki.net/wiki/Alpha_Level_Format#level.dat_Format
spawn_x = args.width*8
spawn_z = args.height*8

level = NBTFile() # Blank NBT
data = TAG_Compound()
data.name = "Data"
data.tags.extend([
	TAG_Long(name="Time", value=1),
	TAG_Long(name="LastPlayed", value=int(time.time()*1000)),
	TAG_Int(name="SpawnX", value=spawn_x),
	TAG_Int(name="SpawnY", value=2),
	TAG_Int(name="SpawnZ", value=spawn_z),
	TAG_Long(name="SizeOnDisk", value=0),
	TAG_Long(name="RandomSeed", value=random.randrange(1,9999999999)),
	TAG_Int(name="version", value=19132),
	TAG_String(name="LevelName", value="Testing")
])

player = TAG_Compound()
player.name = "Player"
player.tags.extend([
	TAG_Int(name="Score", value=0),
	TAG_Int(name="Dimension", value=0),
	TAG_Short(name="Air", value=300),
	TAG_Short(name="AttackTime", value=0),
	TAG_Short(name="DeathTime", value=0),
	TAG_Short(name="Fire", value=-20),
	TAG_Short(name="Health", value=20),
	TAG_Short(name="HurtTime", value=0),
	TAG_Float(name="FallDistance", value=0),
	TAG_Byte(name="OnGround", value=1),
	TAG_Byte(name="Sleeping", value=0),
	TAG_Short(name="SleepTimer", value=0)
])

inventory = TAG_List(name="Inventory", type=TAG_Compound)
player.tags.append(inventory)

motion = TAG_List(name="Motion", type=TAG_Double)
motion.tags.extend([
	TAG_Double(value=0.0),
	TAG_Double(value=0.0),
	TAG_Double(value=0.0)
])
player.tags.append(motion)

position = TAG_List(name="Pos", type=TAG_Double)
position.tags.extend([
	TAG_Double(value=spawn_x+0.5),
	TAG_Double(value=2.8),
	TAG_Double(value=spawn_z+0.5)
])
player.tags.append(position)

rotation = TAG_List(name="Rotation", type=TAG_Float)
rotation.tags.extend([
	TAG_Float(value=0.0),
	TAG_Float(value=0.0)
])
player.tags.append(rotation)

data.tags.append(player)
level.tags.append(data)

level.write_file(world_folder+"/level.dat")

print "World generated at "+world_folder
