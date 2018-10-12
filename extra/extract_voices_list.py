# Voices Name Correspondence List Extractor
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
# FSN support by Quibi
#
# 提取语音名称与角色对应的列表

import os
import sys
import codecs
import argparse

route_list = {
    # Fate/stay night
    'プロローグ1日目': 'prg01',
    'プロローグ2日目': 'prg02',
    'プロローグ3日目': 'prg03',
    'セイバーエピローグ': 'savep',
    '凛エピローグ': 'rinep',
    '凛エピローグ2': 'rinep2',
    '桜エピローグ': 'sakep',
    '桜エピローグ2': 'sakep2',
    'タイガー道場すぺしゃる': 'tigsp',
    'ラストエピソード': 'lstep',

    # Fate/hollow ataraxia
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

# Fate/stay night
fsn_routes = ['セイバー', '凛', '桜']
routes_to_days = {'セイバー': 15, '凛': 14, '桜': 16}
routes_to_names = {'セイバー': 'sav', '凛': 'rin', '桜': 'sak'}

days = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四', '十五', '十六']
for fsn_route in fsn_routes:
    days_count = routes_to_days[fsn_route]
    for i, day in enumerate(days[:days_count]):
        route_list[f'{fsn_route}ルート{day}日目'] = f'{routes_to_names[fsn_route]}{i+1:02}'


class VoiceFile:
    def __init__(self):
        self.voice_filename = {}

    def loop_file(self, filename):
        basename = os.path.splitext(filename)[0]
        basename_split = basename.split('-')
        if len(basename_split) < 2:
            route_with_day = basename
            scene_number = ''
        else:
            route_with_day = basename_split[0]
            scene_number = basename_split[1]

        fs = open(filename, 'rb')
        text = fs.read()
        lines = text.split(b';')
        for line in lines:
            if line[:5] == b'_VPLY':
                voices = line[6:].decode().split(',')
                character = voices[0]
                voice_number = voices[1]

                if voice_number in self.voice_filename:
                    continue
                self.voice_filename[voice_number] = [route_list[route_with_day], scene_number, character]
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
