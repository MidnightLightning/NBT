from nbt import *
from nbt.mapbuilder import utilities
from nbt.mapbuilder import recipe
from nbt.region import RegionFile
from nbt.chunk import BlockArray
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
if (not os.path.exists(world_folder)):
	print "No such world fold as "+world_folder
	sys.exit()

# Create flying island
blocks = {}
diameter = args.width*16-4 if args.width < args.height else args.height*16-4
blocks = utilities.draw_disk((0,0,0), diameter, blocks, 2) # Draw a grass disk
blocks = utilities.draw_disk((0,0,0), int(diameter/8), blocks, 0) # punch a hole in it
blocks = utilities.draw_disk((0,5,0), 11, blocks, 3)
blocks = utilities.draw_disk((0,6,0), 9, blocks, 12)
blocks = utilities.draw_disk((0,7,0), 7, blocks, 4)

island = recipe.block_recipe()
island.set_blocks(blocks)
island.apply((args.width*8, 3, args.width*8), world_folder=world_folder)
