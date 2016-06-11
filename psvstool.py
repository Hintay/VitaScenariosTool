# Vita Scenarios Converter
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# The scenario files that extracted from PSV conversion utility

from macroslist import *
from extra.voices_character import * # in 'extra' directory
import os
import re
import sys
import codecs
import argparse

encoding = 'Shift_JIS'

# 处理行
class ScenarioLine:
	def __init__(self, line):
		self.line = line
		self.newline = ''
		self.macro = None
		self.macro_type = None
		self.macro_subtype = None
		self.macro_comment_out = False # 该行是否需要注释
		self.macro_converted = None
		self.parameters = ''
		self.newparameters = ''
		self.ismessage = False
		self.messageid = None
		self.match_line()

	# 正则匹配提取数据
	def match_line(self):
		if self.line == b'': return # 空行
		matchs = re.match(b'^_(.*?)\((.*)', self.line)
		if(matchs): # 匹配至(宏)(宏参数)
			self.macro = matchs.group(1).decode()
			if(self.macro in ignore_macros): return

			# 判断文本
			# MSA2 上行只可能有 WTKY；MSAD上方可能有其他代码，并等运行完才会显示。（应该适用于文本快进）
			elif(self.macro[:3] == 'MSA'):
				self.ismessage = True
				self.parameters = matchs.group(2)
				return
			elif(self.macro[:2] == 'ZM' or self.macro[:2] == 'ZZ'): # ZZ为剧本开头
				self.ismessage = True
				self.parameters = matchs.group(2)
				self.messageid = self.macro[2:] # ID
				return
			# /判断文本

			elif(self.macro == 'EVT0'):
				self.newline += '@call storage=staffroll.ks'
				return
			elif(self.macro == 'HFTF'):
				self.get_hftf(matchs.group(2))
				return

			elif(macros.get(self.macro)): # macro 列表中有匹配
				if matchs.group(2): # 若有参数
					self.parameters = matchs.group(2).split(bytes(',`', encoding)) # 分割后[0]为宏参数
			else: # 找不到相应macro时不处理
				self.newline += ';%s' % self.line.decode(encoding)
				return
		else: # 未匹配到任何数据，一般不会出现
			print(self.line, file=sys.stderr)

		self.get_macro()

	def get_hftf(self, parameters):
		par_dict = {}
		par_keys = {'026': 'eval', '235':'result'}
		for parameter in parameters.decode(encoding).split(',`'):
			if(parameter == '0'): continue
			parsplit = parameter.split(':')
			par_dict[par_keys[parsplit[0]]] = parsplit[1]
		self.newline += '@eval exp="tf[\'%s\']=%s"' % (par_dict['eval'], true_false[par_dict['result']])

	# 匹配宏类型
	def match_macro_type(self):
		if self.macro in bracket_end_macros and self.parameters[0][-1:] == b')':
			self.parameters[0] = self.parameters[0][:-1]
		if not self.parameters or self.ismessage or self.macro in macros_without_comma:
			return
		parameter = self.parameters[0]
		macro_types = parameter.decode(encoding).split(',')
		if len(macro_types) > 1: # 宏有子类型
			if self.macro == 'BTXO': # 特殊处理，无额外参数的
				self.parameters.append(b'003:'+macro_types[1].encode(encoding))
			else:
				self.macro_subtype = macro_types[1]
		try: # 有对应macro则删除参数
			if(macros[self.macro][macro_types[0]] != None):
				self.macro_type = macro_types[0]
				del self.parameters[0] # 使用后移除参数
		# 无对应macro，例：*page
		except TypeError:
			pass
		except KeyError:
			pass

	# 获取宏名字
	def get_macro_name(self):
		if(self.macro and macros.get(self.macro)):
			#print(self.macro)
			#print(self.macro_type)
			if self.macro_type != None:
				if self.macro_subtype != None:
					return(macros[self.macro][self.macro_type][self.macro_subtype])
				else:
					return(macros[self.macro][self.macro_type])
			else:
				return(macros[self.macro])
		else:
			return # 无对应的macro type

	# 获取参数文本
	def get_parameters(self):
		for par in self.parameters:
			parsplit = par.decode(encoding).split(':')
			# 若分割出的参数小于2则没有参数可分割
			if not len(parsplit) < 2:
				par_key = parsplit[0]
				par_value = parsplit[1]
				if(parameters.get(par_key)):
					par_key = parameters[par_key]

					if par_key in special_parameter.keys():
						par_value = special_parameter[par_key].get(par_value, par_value)

					if self.macro == 'MPLY' and par_key == 'storage':
						par_value = bgm.get(parsplit[1], parsplit[1])
					elif self.macro_converted == '@rep' and par_key == 'storage':
						par_key = 'bg'
					elif self.macro == 'KMVE' and par_key == 'mag':
						par_key = 'magnify'
					elif self.macro == 'IRIW' and par_key == 'target' and parsplit[1][:6] == '_PAGE(':
						par_value = '*page%s %s' % (parsplit[1][6], parsplit[1][7:])
				else:
					if par_key in ignore_parameters:
						continue
					par_key = '`' + par_key
			else:
				par_key = None
				par_value = parsplit[0]
				if self.macro == 'PAGE': # 页面标签
					self.macro_converted += parsplit[0]
					return
				elif self.macro == 'NEVL': # @eval
					eval_value = par_value.split('=')
					par_key = eval_value[0]
					par_value = '"%s"' % eval_value[1]
				elif self.macro == 'VPLY': # 语音标签
					voice_split = par_value.split(',')
					try: # 格式检查
						#par_value = '%s_%05x' % (voice_split[0], int(voice_split[1], 16))
						voice_number = '%05x' % int(voice_split[1], 16)
						voice_desc = voices_list.get(voice_number, '')
						par_key = 'storage'
						par_value = '%s%s_%s_%s' % (voice_desc[0], voice_desc[1], voice_split[0], voice_number)
					except ValueError: # '_____' 或其它
						self.macro_comment_out = True
						#par_key = 'storage'
						#par_value = '%s_%s' % (voice_split[0], voice_split[1])
				elif self.macro == 'WTVT': # 语音等待标签
					par_key = 'time'
				elif self.macro == 'KDLY':
					par_key = 'speed'
					if par_value == '0': par_value = 'user'
				elif self.macro == 'FCAL':
					par_key = 'storage'
					par_value = call.get(par_value, par_value)
				elif self.macro == 'MTLK':
					say_key = par_value.split(',')[1]
					say_value = say_name.get(say_key, say_key)
					if(say_value):
						self.newparameters += ' name=%s' % say_value
					return
				elif self.macro == 'KFCH' and par_value == 'extoff=0': # 修复错误
					par_key = 'textoff'
					par_value = '0'

			if(par_key):
				if(par_value == ''): par_value = '""'
				self.newparameters += ' %s=%s' % (par_key, par_value)
			elif(par_value):
				self.newparameters += ' ' + par_value

	def get_macro(self):
		if self.ismessage: # 文本内容直接退出
			return
		self.match_macro_type()
		self.macro_converted = self.get_macro_name()
		if(self.macro_converted): # 有对应的 macro 名
			self.get_parameters() # 格式化参数
			if(self.macro_comment_out): self.newline += ';'
			self.newline += self.macro_converted
			self.newline += self.newparameters
		else:
			self.newline += ';%s' % self.line.decode(encoding)

# 处理剧本Message
class ScenarioMessage:
	def __init__(self):
		self.need_next = False
		self.temp_need_next = 0 # @n 临时下一行 搜索有几个@n就重复几次
		self.fore_need_next = False # 遇到 WTVT 等标签时不按@n个数，连续包含行内宏
		self.already_reline = False
		self.is_HFUL = False
		self.need_handle_line = None
		self.inline_macros = '' # 转换好的macros
		self.newlines = ''

	# 重置所有参数
	def reset_variables(self):
		self.__init__()

	# 添加一行
	def add_line(self, lineinfo):
		if lineinfo.ismessage: # 若为 Message
			# 特殊情况重置
			if self.temp_need_next > 0 or self.fore_need_next == True:
				self.end_inline_macros('n')
			# 若需要添加下一行但本行又为文本的话则封闭 Macro 再处理本行
			if self.need_next:
				self.end_inline_macros('a')
			# /特殊情况重置

			if lineinfo.messageid: # 有 ID 则加上 ID 注释
				if self.newlines != '': self.newlines += '\n'
				self.newlines += ';%d, %s\n' % (int(lineinfo.messageid, 16), lineinfo.messageid)
				self.is_start_line = True
			else:
				self.is_start_line = False

			if lineinfo.parameters: # 内容处理
				self.processing_message_line(lineinfo.parameters)
		else:
			# 特殊情况重置 - 语音等
			if lineinfo.macro in close_inline_macro:
				if self.temp_need_next > 0:
					self.end_inline_macros('n')
				elif self.need_next:
					self.end_inline_macros('a')
				self.newlines += '\n'+lineinfo.newline
				return

			if(lineinfo.macro == 'WTKY'): # 用于换行判断
				self.already_reline = True

			# 将 Macro 的 @ 替换为 [
			if lineinfo.newline[:1] == '@':
				self.inline_macros += '[' + lineinfo.newline[1:] +']'
			elif not lineinfo.newline == '':
				self.inline_macros += '\n' + lineinfo.newline + '\n'

			# 行内 @n 要包含的 Macro 块也在这里处理
			if self.temp_need_next > 0 and self.fore_need_next == False:
				# 语音等待符号
				if lineinfo.macro == 'WTVT':
					self.fore_need_next = True
					return
				self.temp_need_next -= 1
				if self.temp_need_next == 0:
					self.end_inline_macros('n')

	# 处理Message
	def processing_message_line(self, content):
		# 先匹配特殊字符 注意：返回值为 Unicode 字符串
		newlines = self.processing_special_character(content)
		self.already_reline = False

		# [hfu] [hfl]
		if(self.is_HFUL):
			self.is_HFUL = False
			newlines = self.processing_hful(newlines)

		# 处理行内的 Marco： @n 或 @a(id)
		# ！注意！ @a 与 @n 会出现在同一行！@a 比 @n 先出现
		# ！注意！ @a 可能会多次出现！
		#
		# @a(ID) ID与 _SYNC( 中 ID 相同
		# 不用管有 @a 行中的 @n
		if(newlines.find('@a') >= 0):
			if newlines[-2:] == '@n': newlines = newlines[:-2]

			self.need_handle_line = newlines
			self.need_next = True
			return
		# @n 重复几次即为包含下面几行
		n_count = newlines.count(r'@n')
		if(n_count):
			self.need_handle_line = newlines
			self.temp_need_next = n_count
			return
		# 有需要处理的行代表暂时不能直接添加该行
		if self.need_handle_line:
			return
		# /处理行内的 Marco

		self.newlines += newlines

	@classmethod
	def processing_hful(cls, content):
		new_content = ''
		for index, value in enumerate(content):
			if value == '。': continue
			try:
				char = (value + content[index+1]) if content[index+1] == '。' else value
			except IndexError:
				char = value
			new_content += '[hfu]%s[hfl]%s' % (char, char)
		return new_content

	# 行内 Macros 结束
	def end_inline_macros(self, end_type):
		if end_type == 'a':
			# 重置 Flag
			self.need_next = False
			# 正则替换行内的@a(ID)
			self.newlines += re.sub('(@a\(\d+\))', self.inline_macros, self.need_handle_line)
		else:
			self.temp_need_next = 0
			self.fore_need_next = False
			# 正则替换行内的@n
			self.newlines += re.sub('(@n)+', self.inline_macros, self.need_handle_line)
		# 重置部分参数
		self.need_handle_line = None
		self.inline_macros = ''

	# 处理特殊字符 (以 \xec 开头)
	# \xec\x4a = Line Macro Start
	# \xec\x46 = Line Macro Padding Character
	# \xec\x48 = Line Macro End
	# \xec\x45 = [heart]
	# \xec\x59 = [ansz]
	# \xec\x5a = [argz]
	# \xec\x5b = [ingz]
	# \xec\x5c = [nusz]
	# \xec\x5d = Inline Macros End Tag for @a
	# \xec\x4b = Block Macro Start
	# \xec\x47 = Block Macro Padding Character
	# \xec\x49 = Block Macro End
	# \xec\x50 = Wacky Macro Length 3
	# \xec\x52 = Wacky Macro Length 6
	# \xec\x53 = Wacky Macro Length 9
	# \xec\x54 = Wacky Macro Length 12
	def processing_special_character(self, content):
		content = content.replace(b'\xec\x5d', b'') # 直接去掉结束标记
		content = content.replace(b'\xec\x5a', b'[argz]')
		content = content.replace(b'\xec\x5c', b'[nusz]')
		content = content.replace(b'\xec\x59', b'[ansz]')
		content = content.replace(b'\xec\x5b', b'[ingz]')
		content = content.replace(b'\xec\x45', b'[heart]')
		content = content.replace(b'\xec\x50', b'[wacky len=3]')
		content = content.replace(b'\xec\x52', b'[wacky len=6]')
		content = content.replace(b'\xec\x53', b'[wacky len=9]')
		content = content.replace(b'\xec\x54', b'[wacky len=12]')
		# 处理Line宏
		content = re.sub(b'((?:\xec\x4a)(?:\xec\x46)*(?:\xec\x48))',
			lambda m: b'[line len=' + str(int(len(m.group(1))/2)).encode(encoding) + b']', content)
		# 处理Block宏
		content = re.sub(b'((?:\xec\x4b)(?:\xec\x47)*(?:\xec\x49))',
			lambda m: b'[block len=' + str(int(len(m.group(1))/2)).encode(encoding) + b']', content)
		# 解码为unicode
		try:
			content = content.decode(encoding)
		except UnicodeDecodeError:
			print(content, file=sys.stderr)
			sys.exit(20)

		# @s(28) [large] @s(16) [small]
		if(content.find('@s(') >= 0):
			matchs = re.match(r'^(?:\^)*@s\((\d{2})\)(?:@n)?$', content)
			if(matchs):
				content = content.replace('@s(28)@n', '@large')
				content = content.replace('@s(16)@n', '@small')
			else:
				content = content.replace('@s(28)', '[large]')
				content = content.replace('@s(16)', '[small]')

		# 上标文字 Ruby
		content = re.sub('<(.*?),(.*?)>', self.get_ruby_macro, content)

		# 特殊换行标记
		if(self.is_start_line == False and content[:2] == '^　' and self.newlines != '' and self.already_reline == False):
			content = re.sub('^(\^+)', lambda m:'[br]' * (len(m.group(1))) + '\n', content)
		# 开头的换行标记 ^
		if self.is_start_line:
			content = re.sub('^(\^+)', lambda m:'@r\n' * (len(m.group(1))), content)
		else:
			content = re.sub('^(\^+)', self.get_beginning_r_macro, content)
		# 剩下的换行标记 ^
		content = re.sub('(\^+)(@n)?(.{0,2})', self.get_remained_r_macro, content)

		# 颜色标记 @c(r,g,b) = [font color=0x000000]
		content = re.sub('@c\((\d+),(\d+),(\d+)\)',
			lambda m: '[font color=0x{:0>2}{:0>2}{:0>2}]'.format(m.group(1), m.group(2), m.group(3)), content)
		return content

	# For re.sub
	@classmethod
	def get_ruby_macro(cls, m):
		ruby_macro = '[ruby text=' + m.group(2)
		if len(m.group(1)) > 1: ruby_macro += ' char=' + str(len(m.group(1)))
		ruby_macro += ']' + m.group(1)
		return ruby_macro

	# For re.sub
	@classmethod
	def get_beginning_r_macro(cls, m):
		br_count = len(m.group(1))
		return '@r\n' * (br_count - 1) if br_count > 1 else ''

	# For re.sub
	@classmethod
	def get_remained_r_macro(cls, m):
		br_count = len(m.group(1))
		if(not m.group(3) or m.group(3)[0] == '@'):
			text = '\n@r' * br_count + '\n'
		elif(m.group(3)[0] == '　'):
			text = '[br]' * br_count + '\n'
		else:
			text = '[br]'
		if(m.group(3) != '@n'): text += m.group(3)
		return text

# 处理剧本文件
class ScenarioFile:
	def __init__(self, file_path):
		self.lines = None
		self.newlines = []
		self.file_path = file_path
		self.filename = os.path.basename(file_path)
		self.basename = os.path.splitext(self.filename)[0]
		self.open_file()
		self.output_file()

	def open_file(self):
		fs = open(self.file_path, 'rb')
		text = fs.read()
		self.lines = text.split(b';')
		fs.close()
		self.processing_file()

	def processing_file(self):
		message_handle = ScenarioMessage()
		for line in self.lines:
			scenario_line = ScenarioLine(line) # 处理行
			# [hfu] [hfl]
			if(scenario_line.macro == 'HFUL'):
				message_handle.is_HFUL = True
				continue
			# 剧本特殊处理
			if(message_handle.need_next or message_handle.temp_need_next > 0 or scenario_line.ismessage):
				message_handle.add_line(scenario_line) # need_next 等变量可能会变化所以需要重新判断
				if(message_handle.need_handle_line == None):
					newlines = message_handle.newlines.replace('〜', '～') # ~ 号需要特殊处理
					newlines = newlines.replace('[resetfont]', '[rf]')  # 替换短链接
					self.newlines.append(newlines)
					message_handle.reset_variables()
				continue
			# /剧本特殊处理
			self.newlines.append(scenario_line.newline)

	def output_file(self):
		fs = codecs.open(os.path.splitext(self.file_path)[0]+'.ks', 'w', 'u16') # 文本方式打开
		new_file = ''
		for line in self.newlines:
			if not line == '':
				new_file += line + '\n'
		new_file = new_file.replace('\n\n', '\n') # 去除多余的换行
		new_file = new_file.replace('[lr]\n~\n', '[l]\n') # 额外处理[l]
		fs.write(new_file)
		fs.close()

def parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('input', metavar='input', help='input .ini file or folder')
	return parser, parser.parse_args()

def convert_verb(args):
	if not os.path.exists(args.input):
		parser.print_usage()
		print('Error: the following file or folder does not exist: ' + args.input)
		sys.exit(20)

	if os.path.isfile(args.input):
		ScenarioFile(args.input)
	else: # 文件夹
		for root, dirs, files in os.walk(args.input):
			for file in files:
				if file.endswith('ini'):
					print(file, file=sys.stderr)
					ScenarioFile(os.path.join(root, file))

if __name__ == '__main__':
	parser, args = parse_args()
	if (args.input != None): convert_verb(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)
