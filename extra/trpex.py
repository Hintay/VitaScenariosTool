# TROPHY.TRP Extractor
# comes with ABSOLUTELY NO WARRANTY.
#
# Copyright (C) 2016 Hintay <hintay@me.com>
# Portions Copyright (C) 2010 Red Squirrel
#
# trpex is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# trpex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with trpex. If not, see <http://www.gnu.org/licenses/>.
#
##################

import os
import sys
from struct import unpack, pack
import argparse

class TrophyFile:
	def __init__(self, input_file, output_folder):
		self.desc_index = []
		self.output_folder = output_folder
		self.check_output_folder()

		print("Opening input file...", end="")
		self.file_stream = open(input_file, 'rb')
		print("OK!")

		self.get_header()
		self.processing_file()

	def check_output_folder(self):
		print("Creating output folder...", end="")
		if os.path.isdir(self.output_folder):
			print("EXISTS!")
		else:
			os.mkdir(self.output_folder)
			print("OK!")

	def get_header(self):
		print("Getting header size...", end="")
		self.file_stream.seek(100)
		header_size, = unpack('>L', self.file_stream.read(4))
		self.number_of_entries = (header_size // 0x40) - 1
		print("OK!")

	def processing_file(self):
		for i in range(self.number_of_entries):
			file_name = self.get_file_name(i)
			entry_data = self.get_file_content(i)
			self.output_file(file_name, entry_data)

		self.file_stream.close()
		print("\nAll done! Bye bye :-)\n")

	def get_file_name(self, index):
		print("\nGetting filename...", end="")
		self.file_stream.seek(0x40 + index * 0x40)
		file_name = self.read_0_string(self.file_stream.read(16))
		print(file_name)
		return file_name

	def get_file_content(self, index):
		print(">>\tGetting file offset and size...", end="")
		self.file_stream.seek(16, 1)
		offset, size = unpack('>QQ', self.file_stream.read(16))
		print("OK!")
		#print("\t\t[offset: %d, size: %d]" % (offset, size))

		print(">>\tGetting file content...", end="")
		self.file_stream.seek(offset)
		entry_data = self.file_stream.read(size)
		print("OK!")

		return entry_data

	def output_file(self, file_name, entry_data):
		print(">>\tOpening output file...", end="")
		fs = open(os.path.join(self.output_folder, file_name), 'wb')
		print("OK!")
		print(">>\tWriting output file content...", end="")
		fs.write(entry_data)
		fs.close()
		print("DONE!")

	def read_0_string(self, bstr):
		try:
			return bstr[0:bstr.index(b'\x00')].decode()
		except ValueError:
			return bstr.decode()

def parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('input', metavar='input_file', help='path of your TROPHY.TRP.')
	parser.add_argument('output', metavar='output_folder', help='output folder.')
	return parser, parser.parse_args()

def convert_verb(args):
	if not os.path.exists(args.input):
		parser.print_usage()
		print('Error: the following file does not exist: ' + args.input)
		sys.exit(20)

	if os.path.isfile(args.input):
		TrophyFile(args.input, args.output)
	else: # 文件夹
		parser.print_usage()
		print('Error: the following input does not file: ' + args.input)
		sys.exit(20)

if __name__ == '__main__':
	print("TROPHY.TRP Extractor")
	print("Copyright (C) 2016 Hintay")
	print("Portions Copyright (C) 2010 Red Squirrel\n")

	parser, args = parse_args()
	if (args.input != None): convert_verb(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)