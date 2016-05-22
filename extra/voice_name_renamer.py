# Voice File Names Renamer
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 批量修改语音文件名

from voices_character import *
import os
import sys

class ChangeVoiceName:
	def __init__(self, folder):
		self.folder = folder
		self.hex_mod = os.path.exists(os.path.join('voice1', '03e5a.opus'))
		self.loop_file_list()

	def loop_file_list(self):
		for root, dirs, files in os.walk(self.folder):
			for f in files:
				if f.endswith('opus'):
					voice_number = self.match_number(f.split('.')[0])
					try:
						if self.hex_mod:
							voice_number = int(voice_number, 16)
						else:
							voice_number = int(voice_number)
							if self.folder == 'voice2': voice_number += 20000
						hex_number = hex(voice_number)
						hex_number = '{:0>5}'.format(hex_number[2:])
						file_path = os.path.join(self.folder, f)

						self.change_name(file_path, hex_number)
					except ValueError: # 字母等
						continue

	def change_name(self, file_path, hex_number):
		voice_name = voices_list.get(hex_number, '')
		if voice_name:
			if len(voice_name) == 4:
				new_name = '%s%s_%s_%s.opus' % (voice_name[0], voice_name[1], voice_name[2], voice_name[3])
			else:
				new_name = '%s%s_%s_%s.opus' % (voice_name[0], voice_name[1], voice_name[2], hex_number)
				#new_name = '%s_%s.opus' % (voice_name[2], hex_number)
		else:
			#new_name = hex_number[1:] + '.opus'
			new_name = hex_number + '.opus'
		print(new_name, file=sys.stderr)
		try:
			os.rename(file_path, os.path.join(self.folder, new_name))
		except WindowsError:
			pass

	def match_number(self, file_name):
		if self.hex_mod:
			name_split = file_name.split('_')
		else:
			name_split = file_name.split('-')

		if len(name_split) > 1:
			voice_number = name_split[1]
		elif file_name in special_name[self.folder].keys():
			voice_number = special_name[self.folder][file_name]
		else:
			voice_number = file_name
		return voice_number

def change_filenames():
	for folder in ['voice1', 'voice2']:
		ChangeVoiceName(folder)

if __name__ == '__main__':
	if os.path.exists('voice1') and os.path.exists('voice2'):
		change_filenames()
	else:
		print('Error: please put this script in the outer layer of the voice1 and voice2 folder.')
		sys.exit(20)