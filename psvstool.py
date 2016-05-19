# Vita Scenarios Converter
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# The scenario files that extracted from PSV conversion utility

from macroslist import *
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
		self.parameters = ''
		self.newparameters = ''
		self.matchs = None
		self.ismessage = False
		self.messageid = None
		self.match_line()

	# 正则匹配提取数据
	def match_line(self):
		self.matchs = re.match(b'^_(.*?)\((.*)', self.line)
		if(self.matchs): # 匹配至(宏)(宏参数)
			self.macro = self.matchs.group(1).decode()
			if(self.macro in ignore_macro):
				return

			# 判断文本
			elif(self.macro[:3] == 'MSA'):
				self.ismessage = True
				self.parameters = self.matchs.group(2)
				return
			elif(self.macro[:2] == 'ZM' or self.macro[:2] == 'ZZ'):
				self.ismessage = True
				self.parameters = self.matchs.group(2)
				self.messageid = self.macro[2:] # ID
				return
			# /判断文本

			elif(self.macro in macros.keys()): # macro 列表中有匹配
				if self.matchs.group(2): # 若有参数
					self.parameters = self.matchs.group(2).split(bytes(',`', encoding)) # 分割后[0]为宏参数
			#else: #找不到相应的macro
		else:
			# 没匹配到任何数据
			if not self.line == b'':
				print(self.line)
			else: # 空行
				return

		self.get_macro()

	# 匹配宏类型
	def match_macro_type(self):
		if self.macro in brackets_macro and self.parameters[0][-1:] == b')':
			self.parameters[0] = self.parameters[0][:-1]
		if not self.parameters or self.ismessage or self.macro in no_comma_macro:
			return
		parameter = self.parameters[0]
		macro_types = parameter.decode(encoding).split(',')
		self.macro_type = macro_types[0]
		if len(macro_types) > 1: # 宏子类型
			if self.macro == 'BTXO': # 特殊处理，无额外参数的
				self.parameters.append(b'003:'+macro_types[1].encode(encoding))
			else:
				self.macro_subtype = macro_types[1]
		try: # 有对应macro则删除参数
			macros[self.macro][self.macro_type]
			del self.parameters[0] # 使用后移除参数
		# 无对应macro，例：*page
		except TypeError:
			pass
		except KeyError:
			pass

	# 获取宏名字
	def get_macro_name(self):
		if( self.macro and self.macro in macros.keys()):
			#print(self.macro)
			#print(self.macro_type)
			if self.macro_type != None and self.macro_type != '':
				if self.macro_subtype != None and self.macro_subtype != '':
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
				if(parsplit[0] in parameters.keys()):
					# 特殊对应参数
					if parameters[parsplit[0]] in special_macro.keys():
						if parsplit[1] in special_macro[parameters[parsplit[0]]].keys():
							self.newparameters += ' %s=%s' % (parameters[parsplit[0]], special_macro[parameters[parsplit[0]]][parsplit[1]])
							continue
					# /特殊对应参数
					if self.macro == 'IRIW' and parsplit[0] == '075' and parsplit[1][:6] == '_PAGE(':
						# 特殊修正
						self.newparameters += ' ' + parameters[parsplit[0]] + '=*page' + parsplit[1][6] + ' ' + parsplit[1][7:]
					else:
						self.newparameters += ' %s=%s' % (parameters[parsplit[0]], parsplit[1])
				else: # 没有相应的参数
					if parsplit[0] in ignore_parameters:
						continue
					self.newparameters += ' `%s=%s' % (parsplit[0], parsplit[1])
			else:
				# 语音标签
				if self.macro == 'VPLY':
					voice_split = parsplit[0].split(',')
					try: # 格式检查
						voice_storage = ' storage=%s_%05x' % (voice_split[0], int(voice_split[1], 16))
					except ValueError: # '_____' 或其它
						self.macro_comment_out = True
						voice_storage = ' ' + parsplit[0]
						#voice_storage = ' storage=%s_%s' % (voice_split[0], voice_split[1])
					self.newparameters += voice_storage
				# 语音等待标签
				elif self.macro == 'WTVT':
					self.newparameters += ' time=%s' % parsplit[0]
				elif self.macro == 'KDLY':
					self.newparameters += ' speed=%s' % 'user' if parsplit[0] == '0' else parsplit[0]
				elif self.macro == 'FCAL':
					self.newparameters += ' storage=%s' % (call[parsplit[0]] if parsplit[0] in call.keys() else parsplit[0])
				elif parsplit[0] == 'extoff=0': # 修复错误
					self.newparameters += ' textoff=0'
				elif parsplit[0]:
					if not self.macro == 'PAGE': self.newparameters += ' '
					self.newparameters += parsplit[0]

	def get_macro(self):
		if self.ismessage: # 文本内容直接退出
			return
		self.match_macro_type()
		macro = self.get_macro_name()
		if(macro): # 有对应的 macro 名
			self.get_parameters() # 格式化参数
			if(self.macro_comment_out): self.newline += ';'
			self.newline += macro
			self.newline += self.newparameters
		else:
			self.newline += ';%s' % self.line.decode(encoding)

# 处理剧本Message
class ScenarioMessage:
	def __init__(self):
		self.need_next = False
		self.temp_need_next = 0 # @n 临时下一行 搜索有几个@n就重复几次
		self.WTVT_macro = False
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
			if self.temp_need_next > 0 or self.WTVT_macro == True:
				self.end_inline_macros('n')
			# 若需要添加下一行但本行又为文本的话则封闭 Macro 再处理本行
			if self.need_next:
				self.end_inline_macros('a')
			# /特殊情况重置

			if lineinfo.messageid: # 有 ID 则加上 ID 注释
				if self.newlines != '': self.newlines += '\n'
				self.newlines += ';%d, %s\n' % (int(lineinfo.messageid, 16), lineinfo.messageid)

			if lineinfo.parameters: # 内容处理
				self.handle_message_line(lineinfo.parameters)
		else:
			# 特殊情况重置 - 语音
			if lineinfo.macro in end_inline_macro:
				if self.temp_need_next > 0:
					self.end_inline_macros('n')
				elif self.need_next:
					self.end_inline_macros('a')
				self.newlines += '\n'+lineinfo.newline
				return

			# 将 Macro 的 @ 替换为 [
			if lineinfo.newline[:1] == '@':
				self.inline_macros += '[' + lineinfo.newline[1:] +']'
			elif not lineinfo.newline == '':
				self.inline_macros += '\n' + lineinfo.newline + '\n'

			# 行内 @n 要包含的 Macro 块也在这里处理
			if self.temp_need_next > 0 and self.WTVT_macro == False:
				# 语音等待符号
				if lineinfo.macro == 'WTVT':
					self.WTVT_macro = True
					return
				self.temp_need_next -= 1
				if self.temp_need_next == 0:
					self.end_inline_macros('n')

	# 处理Message
	def handle_message_line(self, content):
		# 先匹配特殊字符 注意：返回值为 Unicode 字符串
		newlines = self.handle_special_character(content)

		# [hfu] [hfl]
		if(self.is_HFUL):
			self.is_HFUL = False
			newlines = self.handle_hful_macro(newlines)

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
		# 有需要处理的行代表暂时不能直接返回
		if self.need_handle_line:
			return
		# /处理行内的 Marco

		self.newlines += newlines

	@classmethod
	def handle_hful_macro(cls, content):
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
			self.WTVT_macro = False
			# 正则替换行内的@n
			self.newlines += re.sub('(@n)+', self.inline_macros, self.need_handle_line)
		# 重置部分参数
		self.need_handle_line = None
		self.inline_macros = ''

	# 处理特殊字符 (基本以 \xec 开头)
	# \xec\x4a = Line Macro Start
	# \xec\x46 = Line Macro Padding Character
	# \xec\x48 = Line Macro End
	# \xec\x5a = [argz]
	# \xec\x5c = [nusz]
	# \xec\x59 = [ansz]
	# \xec\x5b = [ingz]
	# \xec\x45 = [heart]
	# \xec\x5d = Append Macro End Tag 行内macro结束标记
	# \xec\x4b = Block Macro Start
	# \xec\x47 = Block Macro Padding Character
	# \xec\x49 = Block Macro End
	# \xec\x50 = Wacky Macro Length 3
	# \xec\x52 = Wacky Macro Length 6
	# \xec\x53 = Wacky Macro Length 9
	# \xec\x54 = Wacky Macro Length 12
	def handle_special_character(self, content):
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
			print(content)
			sys.exit(20)

		# 上标文字 Ruby
		content = re.sub('<(.*?),(.*?)>', self.get_ruby_macro, content)
		# 开头的换行标记 ^
		content = re.sub('^(\^+)', self.get_beginning_r_macro, content)
		# 剩下的换行标记 ^
		content = re.sub('(\^+)(@n)?(.)?', self.get_remained_r_macro, content)
		# 颜色标记 @c(r,g,b) = [font color=0x000000]
		content = re.sub('@c\((\d+),(\d+),(\d+)\)',
			lambda m: '[font color=0x{:0>2}{:0>2}{:0>2}]'.format(m.group(1), m.group(2), m.group(3)), content)
		# @s(28) [large] @s(16) [small]
		content = '@large' if(content[:6] == '@s(28)') else content.replace('@s(28)', '[large]')
		content = '@small' if(content[:6] == '@s(16)') else content.replace('@s(16)', '[small]')
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
		if(not m.group(3) or m.group(3) == '@'):
			text = '\n@r' * br_count + '\n'
		else:
			text = '[r]' + m.group(3)
		return text

# 处理剧本文件
class ScenarioFile:
	def __init__(self, filename):
		self.lines = None
		self.newlines = []
		self.filename = filename
		self.basename = filename.split('.')[0]
		self.open_file()
		self.output_file()

	def open_file(self):
		fs = open(self.filename, 'rb')
		text = fs.read()
		self.lines = text.split(bytes(';', encoding))
		fs.close()
		self.handle_file()

	def handle_file(self):
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
				if(message_handle.need_next == False and message_handle.temp_need_next == 0):
					self.newlines.append(message_handle.newlines)
					message_handle.reset_variables()
				continue
			# /剧本特殊处理
			self.newlines.append(scenario_line.newline)

	def output_file(self):
		fs = codecs.open(self.basename+'.ks', 'w', 'u16') # 文本方式打开
		new_file = ''
		for line in self.newlines:
			if not line == '':
				# ~ 号需要特殊处理
				line = line.replace('〜', '～')
				new_file += line + '\n'
		# 去除多余的换行
		new_file = new_file.replace('\n\n', '\n')
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
		os.chdir(args.input)
		for file in os.listdir('.'):
			if file.endswith('ini'):
				#print(file.encode('GBK', 'ignore').decode('GBK'))
				ScenarioFile(file)

if __name__ == '__main__':
	parser, args = parse_args()
	if (args.input != None): convert_verb(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)
