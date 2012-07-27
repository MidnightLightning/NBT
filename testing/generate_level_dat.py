# Create a file that can be used as a basic level.dat file with all required fields
# http://www.minecraftwiki.net/wiki/Alpha_Level_Format#level.dat_Format

from nbt import *
import time
import random

level = NBTFile() # Blank NBT
data = TAG_Compound()
data.name = "Data"
data.tags.extend([
	TAG_Long(name="Time", value=1),
	TAG_Long(name="LastPlayed", value=int(time.time()*1000)),
	TAG_Int(name="SpawnX", value=0),
	TAG_Int(name="SpawnY", value=2),
	TAG_Int(name="SpawnZ", value=0),
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
	TAG_Double(value=0.5),
	TAG_Double(value=2.8),
	TAG_Double(value=0.5)
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

print level.pretty_tree()
#level.write_file("level.dat")