#
# For more info of the region file format look:
# http://www.minecraftwiki.net/wiki/Beta_Level_Format
# 

from nbt import NBTFile
from chunk import Chunk
from struct import pack, unpack
from gzip import GzipFile
import zlib
from StringIO import StringIO
import math, time

try:
	import Image
	PIL_enabled = True
except ImportError:
	PIL_enabled = False

class RegionFile(object):
	"""
	A convenience class for extracting NBT files from the Minecraft Beta Region Format
	"""
	
	def __init__(self, filename=None, fileobj=None):
		if filename:
			self.filename = filename
			self.file = open(filename, 'r+b')
		if fileobj:
			self.file = fileobj
		self.chunks = []
		self.extents = None
		if self.file:
			self.parse_header()

	def __del__(self):
		if self.file:
			self.file.close()

	def parse_header(self):
		pass
	
	def get_chunks(self):
		index = 0
		self.file.seek(index)
		chunks = []
		while (index < 4096):
			offset, length = unpack(">IB", "\0"+self.file.read(4))
			if offset:
				x = (index/4) % 32
				z = int(index/4)/32
				chunks.append(Chunk(x,z,length))
			index += 4
		return chunks
	
	def get_map(self):
		if (not PIL_enabled): return false
		map = Image.new('RGBA', (512,512), (128,128,128,0))
		for x in range(32):
			for z in range(32):
				chunk_nbt = self.get_chunk(x,z)
				if (chunk_nbt == None): continue # Skip this chunk if it doesn't exist
				chunk = Chunk(chunk_nbt)
				im = chunk.get_map()
				map.paste(im, ((31-z)*16, x*16))
		return map

	def get_heightmap_image(self, gmin=50, gmax=128, contour=False):
		if (not PIL_enabled): return false
		map = Image.new('RGBA', (512,512), (128,128,128,0))
		for x in range(32):
			for z in range(32):
				chunk_nbt = self.get_chunk(x,z)
				if (chunk_nbt == None): continue # Skip this chunk if it doesn't exist
				chunk = Chunk(chunk_nbt)
				im = chunk.get_heightmap_image(False, gmin, gmax, contour)
				map.paste(im, ((31-z)*16, x*16))
		return map
		
	
	def get_timestamp(self, x, z):
		self.file.seek(4096+4*(x+z*32))
		timestamp = unpack(">I",self.file.read(4))

	def get_chunk(self, x, z):
		#read metadata block
		block = 4*(x+z*32)
		self.file.seek(block)
		offset, length = unpack(">IB", "\0"+self.file.read(4))
		offset = offset * 1024*4 # offset is in 4KiB sectors
		if offset:
			self.file.seek(offset)
			length = unpack(">I", self.file.read(4))[0]
			compression = unpack(">B", self.file.read(1))[0]
			chunk = self.file.read(length-1)
			if (compression == 2):
				chunk = zlib.decompress(chunk)
				chunk = StringIO(chunk)
				return NBTFile(buffer=chunk) #pass uncompressed
			else:
				chunk = StringIO(chunk)
				return NBTFile(fileobj=chunk) #pass compressed; will be filtered through Gzip
		else:
			return None
	
	def write_chunk(self, x, z, nbt_file):
		""" A smart chunk writer that uses extents to trade off between fragmentation and cpu time"""
		data = StringIO()
		nbt_file.write_file(buffer = data) #render to buffer; uncompressed
		
		compressed = zlib.compress(data.getvalue()) #use zlib compression, rather than Gzip
		data = StringIO(compressed)
		
		nsectors = int(math.ceil((data.len+0.001)/4096))
		
		#if it will fit back in it's original slot:
		self.file.seek(4*(x+z*32))
		offset, length = unpack(">IB", "\0"+self.file.read(4))
		pad_end = False
		if (offset == 0 and length == 0):
			# This chunk hasn't been generated yet
			# This chunk should just be appended to the end of the file
			self.file.seek(0,2) # go to the end of the file
			file_length = self.file.tell()-1 # current offset is file length
			total_sectors = file_length/4096
			sector = total_sectors+1
			pad_end = True
		else:
			if nsectors <= length:
				sector = offset
			else:
				#traverse extents to find first-fit
				sector= 2 #start at sector 2, first sector after header
				while 1:
					#check if extent is used, else move foward in extent list by extent length
					self.file.seek(0)
					found = True
					for intersect_offset, intersect_len in ( (extent_offset, extent_len)
						for extent_offset, extent_len in (unpack(">IB", "\0"+self.file.read(4)) for block in xrange(1024))
							if extent_offset != 0 and ( sector >= extent_offset < (sector+nsectors))):
								#move foward to end of intersect
								sector = intersect_offset + intersect_len
								found = False
								break
					if found:
						break

		#write out chunk to region
		self.file.seek(sector*4096)
		self.file.write(pack(">I", data.len+1)) #length field
		self.file.write(pack(">B", 2)) #compression field
		self.file.write(data.getvalue()) #compressed data
		if pad_end:
			# Write zeros up to the end of the chunk
			self.file.seek((sector+nsectors)*4096-1)
			self.file.write(chr(0))
		
		#seek to header record and write offset and length records
		self.file.seek(4*(x+z*32))
		self.file.write(pack(">IB", sector, nsectors)[1:])
		
		#write timestamp
		self.file.seek(4096+4*(x+z*32))
		timestamp = int(time.time())
		self.file.write(pack(">I", timestamp))


	def unlink_chunk(self, x, z):
		""" Removes a chunk from the header of the region file (write zeros in the offset of the chunk).
		Using only this method leaves the chunk data intact, fragmenting the region file (unconfirmed).
		This is an start to a better function remove_chunk"""
		
		self.file.seek(4*(x+z*32))
		self.file.write(pack(">IB", 0, 0)[1:])
