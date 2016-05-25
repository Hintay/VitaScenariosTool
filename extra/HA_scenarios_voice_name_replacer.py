# Voice File Names Replacer for HA Scenarios
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 批量修改 HA 剧本中的语音文件名

from voices_character import *
import os
import re
import sys
import codecs
import argparse

replace_regex = re.compile(r'(say.*storage=)(?:[A-Z]{3}[A-Z0-9]{2}[0-9]{2}_)?[A-z0-9]{3}_([A-Fa-f0-9]{5})')

class ScenarioHandle:
	def __init__(self, file_path):
		self.file_path = file_path
		self.file_name = os.path.basename(file_path)
		self.base_name = os.path.splitext(self.file_name)[0]
		name_split = self.base_name.split('-')
		if(len(name_split) < 2): return
		#route_name = name_split[0]
		self.new_lines = []

		print(self.file_name, file=sys.stderr)
		self.handle_scenario()
		self.output_file()

	def handle_scenario(self):
		fs = codecs.open(self.file_path, 'r', 'u16')
		for line in fs:
			if line[:1] == '@' and line[:4] != '@say':
				self.new_lines.append(line)
				continue
			new_line = replace_regex.sub(self.replace_voice_name, line)
			self.new_lines.append(new_line)
		fs.close()

	def output_file(self):
		fs = codecs.open(self.file_path, 'w', 'u16')
		for line in self.new_lines:
			fs.write(line)
		fs.close()

	# For re.sub
	@classmethod
	def replace_voice_name(cls, m):
		# m.group(2) = voice_number
		voice_desc = voices_list.get(m.group(2), '')
		if voice_desc:
			line = '%s%s%s_%s_%s' % (m.group(1), voice_desc[0], voice_desc[1], voice_desc[2], m.group(2))
			return line
		else:
			return m.group(0)

def parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('input', metavar='input', help='input .ks file or folder')
	return parser, parser.parse_args()

def replace_verb(args):
	if not os.path.exists(args.input):
		parser.print_usage()
		print('Error: the following file or folder does not exist: ' + args.input)
		sys.exit(20)

	if os.path.isfile(args.input):
		ScenarioHandle(args.input)
	else: # 文件夹
		for root, dirs, files in os.walk(args.input):
			for file in files:
				if file.endswith('ks'):
					file_path = os.path.join(root, file)
					ScenarioHandle(file_path)

if __name__ == '__main__':
	parser, args = parse_args()
	if (args.input != None): replace_verb(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)
