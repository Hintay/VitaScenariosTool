# Voices Name Correspondence List Extractor
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 提取语音名称与角色对应的列表

import os
import re
import sys
import codecs
import argparse

class VoiceFile:
	def __init__(self):
		self.voice_filename = {}

	def loop_file(self, filename):
		fs = open(filename, 'rb')
		text = fs.read()
		lines = text.split(b';')
		for line in lines:
			if line[:5] == b'_VPLY':
				voices = line[6:].decode().split(',')
				self.voice_filename[voices[1]] = voices[0]
		fs.close()

	def output_file(self):
		fs = codecs.open('voices.py', 'w', 'utf-8') # 文本方式打开
		sorted_filename = sorted(self.voice_filename.items(), key=lambda d:d[0], reverse = False )
		new_filename = '{'
		for item in sorted_filename:
			new_filename += "'" + item[0] + "': '" + item[1] + "', "
		new_filename += '}'
		fs.write(new_filename)
		#fs.write(repr(self.voice_filename))
		fs.close()

def parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('input', metavar='input', help='input .ini file or folder')
	return parser, parser.parse_args()

def extract_verb(args):
	if not os.path.exists(args.input):
		parser.print_usage()
		print('Error: the following file or folder does not exist: ' + args.input)
		sys.exit(20)

	voices = VoiceFile()
	os.chdir(args.input)
	for file in os.listdir('.'):
		if file.endswith('ini'):
			scenario_file = voices.loop_file(file)
	voices.output_file()

if __name__ == '__main__':
	parser, args = parse_args()
	if (args.input != None): extract_verb(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)