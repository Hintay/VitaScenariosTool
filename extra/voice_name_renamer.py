# Voice File Names Renamer
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 批量修改语音文件名

from voices_character import *
import os
import sys

hex_files = {'voice1':'03e5a.opus', 'voice2':'04e21.opus'}

class ChangeVoiceName:
	def __init__(self, folder):
		self.folder = folder
		self.hex_mod = os.path.exists(os.path.join(self.folder, hex_files[self.folder]))
		self.loop_file_list()

	def loop_file_list(self):
		for root, dirs, files in os.walk(self.folder):
			for f in files:
				if f.endswith('opus'):
					if self.shrine_fix(root, f): continue
					voice_number = self.match_number(os.path.splitext(f)[0])
					try:
						if self.hex_mod:
							if(len(voice_number) == 4): continue # 四位数则跳过（0000、0010这种）
							voice_number = int(voice_number, 16)
						else:
							voice_number = int(voice_number)
							if self.folder == 'voice2': voice_number += 20000
						hex_number = '%05x' % voice_number
						self.change_name(root, f, hex_number)
					except ValueError: # 字母等
						continue

	def change_name(self, root_path, file_name, hex_number):
		voice_name = voices_list.get(hex_number, '')
		if voice_name:
			if len(voice_name) == 4:
				if(voice_name[0] == ''):
					new_name = '%s_%s.opus' % (voice_name[2], voice_name[3])
				elif(voice_name[0] == 'EMA_' or voice_name[0] == 'KUJI'):
					new_name = '%s_%s_%s_%s.opus' % (voice_name[0], voice_name[1], voice_name[2], voice_name[3])
				else:
					new_name = '%s%s_%s_%s.opus' % (voice_name[0], voice_name[1], voice_name[2], voice_name[3])
			else:
				new_name = '%s%s_%s_%s.opus' % (voice_name[0], voice_name[1], voice_name[2], hex_number)
				#new_name = '%s_%s.opus' % (voice_name[2], hex_number)
		else:
			new_name = hex_number + '.opus'

		if(file_name == new_name): return
		try:
			print('>> Rename %s to %s' % (file_name, new_name), file=sys.stderr)
			os.rename(os.path.join(root_path, file_name), os.path.join(root_path, new_name))
		except WindowsError:
			print('   Rename FAILED!', file=sys.stderr)

	def shrine_fix(self, root_path, file_name):
		if (file_name.startswith('EMA_') and file_name[4] != '_') or (file_name.startswith('KUJI') and (file_name[4] != '_' and file_name[4] != 'F')):
			new_name = file_name[:4] + '_' + file_name[4:]
			try:
				print('>> Rename %s to %s' % (file_name, new_name), file=sys.stderr)
				os.rename(os.path.join(root_path, file_name), os.path.join(root_path, new_name))
			except WindowsError:
				print('   Rename FAILED!', file=sys.stderr)
			return True
		else:
			return False

	def match_number(self, file_name):
		if self.hex_mod:
			name_split = file_name.split('_')
		else:
			name_split = file_name.split('-')

		if len(name_split) > 1:
			voice_number = name_split[-1]
		else:
			voice_number = special_name[self.folder].get(file_name, file_name)
		return voice_number

def change_filenames():
	for folder in ['voice1', 'voice2']:
		ChangeVoiceName(folder)
	print("DONE!")

if __name__ == '__main__':
	if os.path.exists('voice1') and os.path.exists('voice2'):
		change_filenames()
	else:
		print('Error: please put this script in the outer layer of the voice1 and voice2 folder.')
		sys.exit(20)