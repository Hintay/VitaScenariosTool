# Vita Scenarios Converter
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016-2018 Hintay <hintay@me.com>
#
# The scenario files that extracted from PSV conversion utility

from macroslist import *
import re
import sys
import codecs
import argparse
from pathlib import Path
from collections import defaultdict

# 'fate', 'hollow' or other
MODE = 'hollow'
ENCODING = '932'

# 临时处理
if MODE == 'fate':
    from extra.voices_character_fsn import *  # in 'extra' directory
    BGM = {}
elif MODE == 'hollow':
    from extra.voices_character import *  # in 'extra' directory
else:
    voices_list = {}
    special_name = {}
    BGM = {}


# 处理行
class ScenarioLine:
    def __init__(self, line, voice_number_dict):
        self.line = line
        self.newline = ''
        self.macro = None
        self.macro_type = None
        self.macro_subtype = None
        self.macro_comment_out = False  # 该行是否需要注释
        self.macro_convert = True
        self.macro_converted = None
        self.parameters = []
        self.new_parameters = ''
        self.is_message = False
        self.message_id = None
        self.voice_number_dict = voice_number_dict
        self.match_line()

    # 正则匹配提取数据
    def match_line(self):
        if self.line == b'':
            return  # 空行
        matches = re.match(b'^_(.*?)\((.*)', self.line)
        if matches:  # 匹配至(宏)(宏参数)
            self.macro = matches.group(1).decode()
            if self.macro in IGNORE_MACROS:
                return

            # 判断文本
            # MSA2 上行只可能有 WTKY；MSAD上方可能有其他代码，并等运行完才会显示。（应该适用于文本快进）
            elif self.macro[:3] == 'MSA':
                self.is_message = True
                self.parameters = matches.group(2)
                return
            elif self.macro[:2] == 'ZM' or self.macro[:2] == 'ZZ':  # ZZ为剧本开头
                self.is_message = True
                self.parameters = matches.group(2)
                self.message_id = self.macro[2:]  # ID
                return
            # /判断文本

            elif self.macro == 'EVT0':
                self.newline += '@call storage=staffroll.ks'
                return
            elif self.macro == 'HFTF':
                self.get_hftf(matches.group(2))
                return

            elif MACROS.get(self.macro):  # macro 列表中有匹配
                if matches.group(2):  # 若有参数
                    self.parameters = matches.group(2).split(bytes(',`', ENCODING))  # 分割后[0]为宏参数
            else:  # 找不到相应macro时不处理
                self.newline += ';%s' % self.line.decode(ENCODING)
                return
        else:  # 未匹配到任何数据，一般不会出现
            print(self.line, file=sys.stderr)

        self.get_macro()

    def get_hftf(self, parameters):
        par_dict = {}
        par_keys = {'026': 'eval', '235': 'result'}
        for parameter in parameters.decode(ENCODING).split(',`'):
            if parameter == '0':
                continue
            par_split = parameter.split(':')
            par_dict[par_keys[par_split[0]]] = par_split[1]
        self.newline += '@eval exp="tf[\'%s\']=%s"' % (par_dict['eval'], TRUE_FALSE[par_dict['result']])

    # 匹配宏类型
    def match_macro_type(self):
        if self.macro in BRACKET_END_MACROS and self.parameters[0][-1:] == b')':
            self.parameters[0] = self.parameters[0][:-1]
        if not self.parameters or self.is_message or self.macro in MACROS_WITHOUT_COMMA:
            return
        parameter = self.parameters[0]
        macro_types = parameter.decode(ENCODING).split(',')
        if len(macro_types) > 1:  # 宏有子类型
            if self.macro == 'BTXO':  # 特殊处理，无额外参数的
                self.parameters.append(b'003:' + macro_types[1].encode(ENCODING))
            else:
                self.macro_subtype = macro_types[1]
        try:  # 有对应macro则删除参数
            if MACROS[self.macro][macro_types[0]] is not None:
                self.macro_type = macro_types[0]
                del self.parameters[0]  # 使用后移除参数
        # 无对应macro，例：*page
        except TypeError:
            pass
        except KeyError:  # 无对应字典中的键值，返回的应该是字典
            self.macro_convert = False
            pass

    # 获取宏名字
    def get_macro_name(self):
        if self.macro and MACROS.get(self.macro) and self.macro_convert:
            # print(self.macro)
            # print(self.macro_type)
            try:
                if self.macro_type is not None:
                    if self.macro_subtype is not None:
                        return MACROS[self.macro][self.macro_type][self.macro_subtype]
                    else:
                        return MACROS[self.macro][self.macro_type]
                else:
                    return MACROS[self.macro]
            except KeyError:
                self.macro_comment_out = True
                print(self.line)
            except TypeError:
                self.macro_comment_out = True
                print(self.line)
        else:
            return  # 无对应的macro type

    # 获取参数文本
    def get_parameters(self):
        for par in self.parameters:
            par_split = par.decode(ENCODING).split(':')
            # 若分割出的参数小于2则没有参数可分割
            if not len(par_split) < 2:
                par_key = par_split[0]
                par_value = par_split[1]
                if PARAMETERS.get(par_key):
                    par_key = PARAMETERS[par_key]

                    if par_key in SPECIAL_PARAMETER.keys():
                        par_value = SPECIAL_PARAMETER[par_key].get(par_value, par_value)

                    if par_key == 'storages' or par_key == 'storage' or par_key == 'last':
                        storages = [STORAGES.get(storage, storage) for storage in par_value.split(',')]
                        par_value = ','.join(storages)
                    if par_key == 'poss':
                        poss = [POS.get(pos, pos) for pos in par_value.split(',')]
                        par_value = ','.join(poss)
                    elif self.macro == 'MPLY' and par_key == 'storage':
                        par_value = BGM.get(par_split[1], par_split[1])
                    elif self.macro_converted == '@rep' and par_key == 'storage':
                        par_key = 'bg'
                    elif self.macro == 'KMVE' and par_key == 'mag':
                        par_key = 'magnify'
                    elif self.macro == 'IRIW' and par_key == 'target' and par_split[1][:6] == '_PAGE(':
                        par_value = '*page%s %s' % (par_split[1][6], par_split[1][7:])
                else:
                    if par_key in IGNORE_PARAMETERS:
                        continue
                    par_key = '`' + par_key
            else:
                par_key = None
                par_value = par_split[0]
                if self.macro == 'PAGE':  # 页面标签
                    self.macro_converted += par_split[0]
                    return
                elif self.macro == 'NEVL':  # @eval
                    par_key = 'exp'
                    if par_value[:3] == 'exp':
                        par_value = '"%s"' % par_value[4:]
                elif self.macro == 'VPLY':  # 语音标签
                    voice_split = par_value.split(',')
                    char_name = voice_split[0]
                    if MODE == 'fate':
                        char_name = char_name.lower()
                    try:  # 格式检查
                        # par_value = '%s_%05x' % (voice_split[0], int(voice_split[1], 16))
                        voice_number = '%05x' % int(voice_split[1], 16)
                        voice_desc = voices_list.get(voice_number, '')
                        par_key = 'storage'
                        if voice_desc:
                            if MODE == 'fate':
                                converted_voice_number = '%03d0' % self.voice_number_dict[char_name]
                                self.voice_number_dict[char_name] += 1
                            else:
                                converted_voice_number = voice_number
                            par_value = '%s%s_%s_%s' % (voice_desc[0], voice_desc[1], char_name, converted_voice_number)
                        else:
                            par_value = '%s_%s' % (char_name, voice_number)
                    except ValueError:  # '_____' 或其它
                        self.macro_comment_out = True
                    except IndexError:
                        self.macro_comment_out = True
                    # par_key = 'storage'
                    # par_value = '%s_%s' % (voice_split[0], voice_split[1])
                elif self.macro == 'WTVT':  # 语音等待标签
                    par_key = 'time'
                elif self.macro == 'KDLY':
                    par_key = 'speed'
                    if par_value == '0':
                        par_value = 'user'
                elif self.macro == 'FCAL':
                    par_key = 'storage'
                    par_value = CALL.get(par_value, par_value)
                elif self.macro == 'MTLK':
                    say_key = par_value.split(',')[1]
                    say_value = SAY_NAME.get(say_key, say_key)
                    if say_value:
                        self.new_parameters += ' name=%s' % say_value
                    return
                elif self.macro == 'KFCH' and par_value == 'extoff=0':  # 修复错误
                    par_key = 'textoff'
                    par_value = '0'

            if par_key:
                if par_value == '':
                    par_value = '""'
                self.new_parameters += ' %s=%s' % (par_key, par_value)
            elif par_value:
                self.new_parameters += ' ' + par_value

    def get_macro(self):
        if self.is_message:  # 文本内容直接退出
            return
        self.match_macro_type()
        self.macro_converted = self.get_macro_name()
        if self.macro_converted:  # 有对应的 macro 名
            self.get_parameters()  # 格式化参数
            if self.macro_comment_out:
                self.newline += ';'
            self.newline += self.macro_converted
            self.newline += self.new_parameters
        else:
            self.newline += ';%s' % self.line.decode(ENCODING)


# 处理剧本Message
class ScenarioMessage:
    def __init__(self, scenario_handler):
        self.is_start_line = False
        self.scenario_handler = scenario_handler
        self.need_next = False
        self.temp_need_next = 0  # @n 临时下一行 搜索有几个@n就重复几次
        self.fore_need_next = False  # 遇到 WTVT 等标签时不按@n个数，连续包含行内宏
        self.is_HFUL = False
        self.processing_line = None
        self.inline_macros = ''  # 转换好的macros
        self.new_line = ''  # 处理好的行

    # 添加一行
    def add_line(self, lineinfo: ScenarioLine):
        if lineinfo.is_message:  # 若为 Message
            if lineinfo.message_id:  # 有 ID 则加上 ID 注释
                if self.new_line:
                    self.append_message_line()
                self.scenario_handler.newlines.append(';%d, %s' % (int(lineinfo.message_id, 16), lineinfo.message_id))
                self.is_start_line = True
            else:
                self.is_start_line = False

            # 若需要添加下一行但本行又为文本的话则封闭 Macro 再处理本行
            if self.temp_need_next > 0 or self.fore_need_next is True:
                self.end_inline_macros('n')
            if self.need_next:
                self.end_inline_macros('a')

            # 需要该行的开头 ^ 来判断要不要换行
            content = self.check_start_reline(lineinfo.parameters)

            if content:  # 内容处理
                if content == b'~@n':
                    return  # 特殊
                self.processing_message_line(content)
        else:
            if not lineinfo.newline:
                return
            # 特殊情况封闭行内标签 - 语音等
            elif lineinfo.macro in CLOSE_INLINE_MACRO:
                if self.temp_need_next > 0:
                    self.end_inline_macros('n')
                elif self.need_next:
                    self.end_inline_macros('a')
                self.append_message_line()
                self.scenario_handler.newlines.append(lineinfo.newline)
                return

            # 将 Macro 的 @ 替换为 [
            if lineinfo.newline[:1] == '@':
                self.inline_macros += '[' + lineinfo.newline[1:] + ']'
            # else:
            #     print(lineinfo.newline)

            # 行内 @n 要包含的 Macro 块也在这里处理
            if self.temp_need_next > 0 and self.fore_need_next is False:
                # 语音等待符号
                if lineinfo.macro == 'WTVT':
                    self.fore_need_next = True
                    return
                self.temp_need_next -= 1
                if self.temp_need_next == 0:
                    self.end_inline_macros('n')

    def check_start_reline(self, content):
        if not self.is_start_line and content and content[:1] == b'^':
            if self.new_line:
                l_index = self.new_line.rfind('[l]')
                if l_index != -1:
                    self.new_line = self.new_line[:l_index] + '[lr]' + self.new_line[l_index + 3:]
                    self.append_message_line()
                else:
                    self.new_line += '[br]'
                    if content != b'^@n':
                        self.append_message_line()
            else:
                l_index = self.scenario_handler.newlines[self.scenario_handler.last_message_index].rfind('[l]')
                if l_index != -1 and self.scenario_handler.last_message_index != -1:
                    self.scenario_handler.newlines[self.scenario_handler.last_message_index] = \
                        self.scenario_handler.newlines[self.scenario_handler.last_message_index][:l_index] + '[lr]' + \
                        self.scenario_handler.newlines[self.scenario_handler.last_message_index][l_index + 3:]
                else:
                    self.scenario_handler.newlines[self.scenario_handler.last_message_index] += '[br]'
            content = content[1:]
        return content

    # 处理Message
    def processing_message_line(self, content):
        # 先匹配特殊字符 注意：返回值为 Unicode 字符串
        content = self.processing_special_character(content)

        # [hfu] [hfl]
        content = self.processing_hful(content)

        # 处理行内的 Marco： @n 或 @a(id)
        # ！注意！ @a 与 @n 会出现在同一行！@a 比 @n 先出现
        # ！注意！ @a 可能会多次出现！
        #
        # @a(ID) ID与 _SYNC( 中 ID 相同
        # 不用管有 @a 行中的 @n
        if content.find('@a') >= 0:
            if content[-2:] == '@n':
                content = content[:-2]

            self.processing_line = content
            self.need_next = True
            return
        # @n 重复几次即为包含下面几行
        n_count = content.count(r'@n')
        if n_count:
            self.processing_line = content
            self.temp_need_next = n_count
            return
        # 有需要处理的行代表暂时不能直接添加该行
        if self.processing_line:
            return
        # /处理行内的 Marco

        self.new_line += content
        self.append_message_line()

    def processing_hful(self, content):
        if not self.is_HFUL:
            return content
        self.is_HFUL = False
        new_content = ''
        for index, value in enumerate(content):
            if value == '。':
                continue
            try:
                char = (value + content[index + 1]) if content[index + 1] == '。' else value
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
            new_line = re.sub('(@a\(\d+\))', self.inline_macros, self.processing_line)
        else:
            self.temp_need_next = 0
            self.fore_need_next = False
            # 正则替换行内的@n
            new_line = re.sub('(@n)+', self.inline_macros, self.processing_line)
        # 替换短标签
        self.new_line += new_line.replace('[resetfont]', '[rf]')

        # 重置参数
        self.processing_line = None
        self.inline_macros = ''

    def append_message_line(self):
        self.scenario_handler.last_message_index = len(self.scenario_handler.newlines)
        self.scenario_handler.newlines.append(self.new_line)
        self.new_line = ''

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
        content = content.replace(b'\xec\x5d', b'')  # 直接去掉结束标记
        content = content.replace(b'\xec\x5a', b'[argz]')
        content = content.replace(b'\xec\x5c', b'[nusz]')
        content = content.replace(b'\xec\x59', b'[ansz]')
        content = content.replace(b'\xec\x5b', b'[ingz]')
        content = content.replace(b'\xec\x40', b'[troya]')
        content = content.replace(b'\xec\x41', b'[aero]')
        content = content.replace(b'\xec\x42', b'[atlas]')
        content = content.replace(b'\xec\x43', b'[margos]')
        content = content.replace(b'\xec\x44', b'[keraino]')
        content = content.replace(b'\xec\x45', b'[heart]')
        content = content.replace(b'\xec\x50', b'[wacky len=3]')
        content = content.replace(b'\xec\x51', b'[wacky len=5]')
        content = content.replace(b'\xec\x52', b'[wacky len=6]')
        content = content.replace(b'\xec\x53', b'[wacky len=9]')
        content = content.replace(b'\xec\x54', b'[wacky len=12]')
        content = content.replace(b'\xec\x55', b'[wacky len=13]')
        content = content.replace(b'\xec\x56', b'[wacky len=14]')
        content = content.replace(b'\xec\x57', b'[wacky len=15]')
        content = content.replace(b'\xec\x58', b'[wacky len=16]')
        # 处理Line宏
        content = re.sub(b'((?:\xec\x4a)(?:\xec\x46)*(?:\xec\x48))',
                         self.get_line_macro, content)
        # 处理Block宏
        content = re.sub(b'((?:\xec\x4b)(?:\xec\x47)*(?:\xec\x49))',
                         lambda m: b'[block len=' + str(int(len(m.group(1)) / 2)).encode(ENCODING) + b']', content)
        # 解码为unicode
        try:
            content = content.decode(ENCODING)
        except UnicodeDecodeError:
            print(content, file=sys.stderr)
            sys.exit(20)

        # @s(40) [quad]; @s(28) [large]; @s(16) [small]
        if content.find('@s(') >= 0:
            matches = re.match(r'^(?:\^)*@s\((\d{2})\)(?:@n)?$', content)
            if matches:
                content = content.replace('@s(40)@n', '@quad')
                content = content.replace('@s(28)@n', '@large')
                content = content.replace('@s(16)@n', '@small')
            else:
                content = content.replace('@s(40)', '[quad]')
                content = content.replace('@s(28)', '[large]')
                content = content.replace('@s(16)', '[small]')

        # 上标文字 Ruby
        content = re.sub('<(.*?),(.*?)>', self.get_ruby_macro, content)

        # 开头的换行标记 ^
        content = re.sub('^(\^+)', lambda m: '@r\n' * (len(m.group(1))), content)
        # 剩下的换行标记 ^
        content = re.sub('(\^+)(@n)?(.{0,2})', self.get_reline_macro, content)

        # 颜色标记 @c(r,g,b) = [font color=0x000000]
        content = re.sub('@c\((\d+),(\d+),(\d+)\)',
                         lambda m: '[font color=0x{:02X}{:02X}{:02X}]'.format(int(m.group(1)), int(m.group(2)),
                                                                              int(m.group(3))), content)
        # 描边
        if content.find('@m') >= 0:
            content = re.sub('@m(\d)', self.replace_font_edge, content)
        # 斜体
        content = content.replace('@i', '[font italic=1]')
        content = content.replace('@e', '[er]')

        # 替换特殊字符
        content = content.replace('〜', '～')

        return content

    def replace_font_edge(self, m):
        edge_text = EDGE_SETTING.get(m.group(1))
        if edge_text:
            self.scenario_handler.newlines.append('@font ' + edge_text)
        return ''  # 替换为空

    # For re.sub
    @classmethod
    def get_line_macro(cls, m):
        text = b'[line'
        if MODE == 'hollow':
            text += b' len='
        text += str(len(m.group(1)) // 2).encode(ENCODING) + b']'
        return text

    # For re.sub
    @classmethod
    def get_ruby_macro(cls, m):
        ruby_macro = '[ruby text=' + m.group(2)
        if len(m.group(1)) > 1:
            ruby_macro += ' char=' + str(len(m.group(1)))
        ruby_macro += ']' + m.group(1)
        return ruby_macro

    # For re.sub
    @classmethod
    def get_reline_macro(cls, m):
        br_count = len(m.group(1))
        if not m.group(3) or m.group(3)[0] == '@':
            text = '\n@r' * br_count + '\n'
        elif m.group(3)[0] == '　':
            text = '[br]' * br_count + '\n'
        else:
            text = '[br]'
        if m.group(3) != '@n':
            text += m.group(3)
        return text


# 处理剧本文件
class ScenarioFile:
    def __init__(self, file_path: Path):
        self.lines = None
        self.last_message_index = -1
        self.newlines = []
        self.file_path = file_path
        self.voice_number_dict = defaultdict(int)
        self.open_file()
        self.output_file()

    def open_file(self):
        fs = self.file_path.open('rb')
        text = fs.read()
        self.lines = text.split(b';')
        fs.close()
        self.processing_file()

    def processing_file(self):
        message_handler = ScenarioMessage(self)
        for line in self.lines:
            scenario_line = ScenarioLine(line, self.voice_number_dict)  # 处理行
            # [hfu] [hfl]
            if scenario_line.macro == 'HFUL':
                message_handler.is_HFUL = True
                continue
            # 剧本特殊处理
            if message_handler.need_next or message_handler.temp_need_next > 0 or scenario_line.is_message:
                message_handler.add_line(scenario_line)  # need_next 等变量可能会变化所以需要重新判断
                continue
            # /剧本特殊处理
            if message_handler.new_line:
                message_handler.append_message_line()
            self.newlines.append(scenario_line.newline)

    def output_file(self):
        fs = codecs.open(self.file_path.with_suffix('.ks'), 'w', 'u16')  # 文本方式打开
        new_file = ''
        for line in self.newlines:
            if not line == '':
                new_file += line + '\n'
        new_file = new_file.replace('\n\n', '\n')  # 去除多余的换行
        # if MODE == 'fate':
        #     new_file = new_file.replace('@fadein storage=WHITE_F', '@flushover')
        #     new_file = new_file.replace('@fadein storage=BLACK_F', '@blackout')
        fs.write(new_file)
        fs.close()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', metavar='input', help='input .ini file or folder')
    return parser, parser.parse_args()


def convert_verb(args):
    input_path = Path(args.input)
    if not input_path.exists():
        parser.print_usage()
        print('Error: the following file or folder does not exist: ' + args.input, file=sys.stderr)
        sys.exit(20)

    if input_path.is_file():
        ScenarioFile(args.input)
    else:  # 文件夹
        for file_path in input_path.glob('**/*'):
            if file_path.suffix == '.ini':
                print(file_path, file=sys.stderr)
                ScenarioFile(file_path)


if __name__ == '__main__':
    parser, args = parse_args()
    if args.input is not None:
        convert_verb(args)
    else:
        parser.print_usage()
        sys.exit(20)
    sys.exit(0)
