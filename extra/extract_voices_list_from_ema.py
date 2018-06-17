# Voice Filenames List from Ema Scene Extractor
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 从绘马脚本中提取语音名称对应列表

import os
import sys
import codecs
import argparse

file_id = 0x04fa9


class EmaFile:
    def __init__(self):
        self.voice_filename = {}
        self.voice_list = 'EMA_ = {\n'

    def loop_file(self, filename):
        global file_id
        fs = open(filename, 'r')
        basename = filename.split('.')[0]

        if basename[-2:] in ['37', '38']:
            self.voice_list += "\t# %s - Deleted scene\n" % basename
            file_id = 0x050D5
            return

        self.voice_list += "\t# %s\n" % basename
        for line in fs:
            if file_id == 0x04fd2:
                self.voice_list += "\t'04fd2': " + str(['EMA_', '07', 'RIN', '0020']) + ", \n"
                file_id += 1
            if line[:5] == '@talk':
                if line[-17:-13] != 'EMA_':
                    continue
                content = line[-12:-1].split('_')
                self.voice_list += "\t'%05x': %s, \n" % (file_id, str(['EMA_', content[0], content[1], content[2]]))
                file_id += 1
        fs.close()

    def output_file(self):
        fs = codecs.open('voices.py', 'w', 'utf-8')  # 文本方式打开
        self.voice_list += '}'
        fs.write(self.voice_list)
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

    voices = EmaFile()
    os.chdir(args.input)
    for file in os.listdir('.'):
        if file.endswith('ini'):
            voices.loop_file(file)
    voices.output_file()


if __name__ == '__main__':
    parser, args = parse_args()
    if args.input is not None:
        extract_verb(args)
    else:
        parser.print_usage()
        sys.exit(20)
    sys.exit(0)
