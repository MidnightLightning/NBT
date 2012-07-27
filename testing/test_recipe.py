from nbt.mapbuilder.recipe import block_recipe

coord = 1,2,10 # A tuple of x,y,z coordinates

recipe = block_recipe()
recipe.add_block(coord, 7)
recipe.add_block((1,3,10), 7)
recipe.add_block((1,2,11), 3)
recipe.add_block((5,5,64), 3)
print recipe.get_extents()
print recipe.get_volume()
print recipe.blocks