#!/usr/bin/python

# SpineML log parser object Alex Cope - 2014 
# 
# This class parses the SpineML XML log description
# and uses this to set up simple access to the log
# file. 
# Once set up log data can be extracted by time, index
# or all data.

# eTree library for extracting the XML data
import xml.etree.ElementTree as ET
import struct

class sml_log:
	def __init__(self, dir_name, log_file):
		# try and load in the specified log file
		self.log_dir_name = dir_name
		self.xml_file = dir_name + "/" + log_file
		self.index_nums = []
		self.index_datatypes = []
		self.all_indices = False
		self.isanalog = True
		self.parsexml()


	def parsexml(self):
		# we have a file name, so load the file
		tree = ET.parse(self.xml_file)
		root = tree.getroot()
		self.data_file_name = root.getchildren()[0].find("LogFile").text
		self.data_length = float(root.getchildren()[0].find("LogEndTime").text)
		self.data_timestep = float(root.getchildren()[0].find("TimeStep").get("dt"))
		self.data_file_type = root.getchildren()[0].find("LogFileType").text
		if len(root.getchildren()[0].findall("LogAll")) == 1:
			# all indices are logged, note how many there are
			self.all_indices = True
			self.num_indices = int(root.getchildren()[0].find("LogAll").get("size"))
			self.all_datatype = root.getchildren()[0].find("LogAll").get("type")
			# for event:
			for ind in root.getchildren()[0].findall("LogCol"):
				index = ind.get("index")
				if index != None:
					self.index_nums.append(index)
				self.index_datatypes.append(ind.get("type"))
		else:
			# not all indices are logged, find which ones are
			for ind in root.getchildren()[0].findall("LogCol"):
				index = ind.get("index")
				if index != None:
					self.index_nums.append(index)
				self.index_datatypes.append(ind.get("type"))
				self.all_indices = False
			for ind in root.getchildren()[0].findall("LogIndex"):
				self.index_nums.append(ind.text)
				self.index_datatypes.append(ind.get("type"))
				self.all_indices = False
		if root[0].tag == "AnalogLog":
			# stuff
			self.isanalog = True
		if root[0].tag == "EventLog":
			# otherstuff
			self.isanalog = False			
		# open the data file for reading
		self.data_file = open(self.log_dir_name + "/" + self.data_file_name,"rb"); # binary flag technically not required for 'Nix

	def getdataforindex(self,i, start_t = 0, end_t = -1):
		vals = []
		if self.isanalog:
			### for now we only implement binary
			# get the data for the specified index
			indexdatatype = ""
			num_skip = 0
			offset = 0
			data_size = 4
			data_type_c = 'd'
			if end_t == -1:
				end_t = self.data_length
				print "correcting"
			# first check index is sane
			if self.all_indices == True:
				assert i < self.num_indices
				# index must be sane: continue
				indexdatatype = self.all_datatype
				num_skip = self.num_indices-1 # one less to skip as we read a value
				offset = i
			else:
				print '------'
				print self.index_nums
				test = self.index_nums.index(i)
				# index must be sane: continue
				indexdatatype = self.index_datatypes[self.index_nums.index(i)]
				num_skip = len(self.index_nums)-1 # one less to skip as we read a value
				offset =  self.index_nums.index(i)
			# setup the data reading
			if indexdatatype == "int":
				data_size = 4
				data_type_c = 'i'
			elif indexdatatype == "float":
				data_size = 4
				data_type_c = 'f'
			elif indexdatatype == "double":
				data_size = 8
				data_type_c = 'd'
			self.data_file.seek(0,0) # return to beginning of the file
			# offset into the file
			self.data_file.seek(int(data_size*offset+data_size*(start_t/self.data_timestep)),1)
			row = 0
			print (end_t-start_t)/self.data_timestep-0.5*self.data_timestep
			while row < (end_t-start_t)/self.data_timestep-0.5*self.data_timestep:
				row = row + 1
				s = self.data_file.read(data_size)
				val = struct.unpack(data_type_c, s)[0] # use first index as result is tuple even with one value
				vals.append(val)
				self.data_file.seek(data_size*num_skip,1)
			return vals
		elif not(self.isanalog):
			### for now we only implement CSV
			# find out which of the cols is the time and which is the index
			ind = self.index_datatypes.index("int")
			if ind == 0:
				indexdatatype = self.index_datatypes[1]
			else:
				indexdatatype = self.index_datatypes[0]
			self.data_file.seek(0,0) # return to beginning of the file
			# for events we must go through the entire file and extract all the relevant index entries
			for line in self.data_file:
				bits = line.split(",")
				index = int(bits[ind])
				time = float(bits[1-ind])
				if index == i:
					if time >= start_t and time < end_t:
						vals.append(time)
			return vals
						
	


