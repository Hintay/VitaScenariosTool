# Voices Name Correspondence List Extractor
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# 提取语音名称与角色对应的列表

import os
import sys
import codecs
import argparse

route_list = {
    'カレン': 'KAREN',
    '合宿編': 'CAMPH',
    '夜編1': 'NGH01',
    '夜編2': 'NGH02',
    '学校・1日目': 'SCH01',
    '学校・2日目': 'SCH02',
    '学校・3日目': 'SCH03',
    '学校・4日目': 'SCH04',
    '柳洞寺・1日目': 'RUY01',
    '柳洞寺・2日目': 'RUY02',
    '柳洞寺・3日目': 'RUY03',
    '柳洞寺・4日目': 'RUY04',
    '真・冒頭': 'SNPLG',
    'ランサー港': 'LANCR',
    '街・特別編': 'CTYEH',
    '街編・1日目': 'CTY01',
    '街編・2日目': 'CTY02',
    '街編・3日目': 'CTY03',
    '街編・4日目': 'CTY04',
    '衛宮邸・1日目': 'EMI01',
    '衛宮邸・2日目': 'EMI02',
    '衛宮邸・3日目': 'EMI03',
    '衛宮邸・4日目': 'EMI04',
    '衛宮邸・夜マップ': 'EMIMP',
    '衛宮邸・夜開始': 'EMING',
    '裏マップ': 'MAPEC',
    '魔境編': 'MAKYO'
}


class VoiceFile:
    def __init__(self):
        self.voice_filename = {}

    def loop_file(self, filename):
        basename = os.path.splitext(filename)[0]
        basename_split = basename.split('-')
        if len(basename_split) < 2:
            return

        fs = open(filename, 'rb')
        text = fs.read()
        lines = text.split(b';')
        for line in lines:
            if line[:5] == b'_VPLY':
                voices = line[6:].decode().split(',')
                if voices[1] in self.voice_filename:
                    continue
                self.voice_filename[voices[1]] = [voices[0], route_list[basename_split[0]], basename_split[1]]
        fs.close()

    def output_file(self):
        fs = codecs.open('voices.py', 'w', 'utf-8')  # 文本方式打开
        sorted_filename = sorted(self.voice_filename.items(), key=lambda d: d[0], reverse=False)
        new_filename = '{\n'
        for item in sorted_filename:
            new_filename += "\t'" + item[0] + "': " + str(item[1]) + ",\n"
        new_filename += '}'
        fs.write(new_filename)
        # fs.write(repr(self.voice_filename))
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
