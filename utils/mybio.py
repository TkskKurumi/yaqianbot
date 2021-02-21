import struct
class bread():
	def __init__(self,file):
		self.file=open(file,'rb')
	def read_int32(self):
		temp=self.file.read(4)
		return struct.unpack('i',temp)[0]
	def read_uint32(self):
		temp=self.file.read(4)
		return struct.unpack('I',temp)[0]
	def read_int64(self):
		temp=self.file.read(8)
		return struct.unpack('q',temp)[0]
	def read_uint64(self):
		temp=self.file.read(8)
		return struct.unpack('Q',temp)[0]
	def read_uint8(self):
		temp=self.file.read(1)
		return struct.unpack('B',temp)[0]
	def close(self):
		return self.file.close()
class bwrite():
	def __init__(self,file):
		self.file=open(file,'wb')
	def write_int32(self,n):
		self.file.write(struct.pack('i',n))
	def write_uint32(self,n):
		self.file.write(struct.pack('I',n))
	def write_int64(self,n):
		self.file.write(struct.pack('q',n))
	def write_uint64(self,n):
		self.file.write(struct.pack('Q',n))
	def write_uint8(self,n):
		try:
			self.file.write(struct.pack('B',n))
		except Exception as e:
			print(n)
			raise e
	def close(self):
		self.file.close()