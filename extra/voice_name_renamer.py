# Voice File Names Renamer
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 批量修改语音文件名

from voices_character import *
import os

class ChangeVoiceName:
	def __init__(self, folder):
		self.folder = folder
		self.loop_file_list()

	def loop_file_list(self):
		for root, dirs, files in os.walk(self.folder):
			for f in files:
				if f.endswith('opus'):
					voice_number = self.match_number(f.split('.')[0])
					try:
						voice_number = int(voice_number)
						if self.folder == 'voice2': voice_number += 20000
						hex_number = hex(voice_number)
						hex_number = '{:0>5}'.format(hex_number[2:])
						file_path = os.path.join(self.folder, f)

						self.change_name(file_path, hex_number)
					except ValueError: # 字母等
						continue

	def change_name(self, file_path, hex_number):
		new_name = ''
		if hex_number in voices_list.keys():
			new_name += voices_list[hex_number] + '_'
		#new_name += '{:0>6}'.format(int(hex_number, 16))  + '.opus' # decimal
		new_name += hex_number + '.opus'

		print(new_name)
		try:
			os.rename(file_path, os.path.join(self.folder, new_name))
		except WindowsError:
			pass

	def match_number(self, file_name):
		name_split = file_name.split('-')
		if len(name_split) > 1:
			voice_number = name_split[1]
		elif name_split[0] in special_name[self.folder].keys():
			voice_number = special_name[self.folder][name_split[0]]
		else:
			voice_number = name_split[0]
		return voice_number

voice_folders = ['voice1', 'voice2']
def change_filenames():
	for folder in voice_folders:
		ChangeVoiceName(folder)

if __name__ == '__main__':
	if os.path.exists('voice1') and os.path.exists('voice2'):
		change_filenames()
	else:
		print('Error: please put this script in the outer layer of the voice1 and voice2 folder.')
		sys.exit(20)