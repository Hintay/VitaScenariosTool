# Voice File Names Renamer
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016-2018 Hintay <hintay@me.com>
#
# 批量修改语音文件名

from extra.voices_character import *
import sys
import logging
from pathlib import Path

BASE_PATH = Path('.')
VOICE_PATH = (BASE_PATH.joinpath('voice1'), BASE_PATH.joinpath('voice2'))
VOICES_SUFFIX = '.at9'

hex_files = {'voice1': Path('03e5a'), 'voice2': Path('04e21')}
old_special_files = {'voice1': Path('KARE-000002'), 'voice2': Path('MAKY-0002')}

# Config Logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('VOICE_RENAME')
fileLog = logging.FileHandler('rename.log', 'w', 'utf-8')
formatter = logging.Formatter('%(levelname)s: %(message)s')
fileLog.setFormatter(formatter)
logger.addHandler(fileLog)


class ChangeVoiceName:
    def __init__(self, folder):
        logger.info("Processing directory %s" % folder)
        self.folder = folder
        self.hex_mod = folder.joinpath(hex_files[folder.stem]).with_suffix(VOICES_SUFFIX).exists()
        self.need_shrine_fix = folder.joinpath(Path('EMA_01_ARC_0000')).with_suffix(VOICES_SUFFIX).exists()

        is_from_old_extractor = folder.joinpath(old_special_files[folder.stem]).with_suffix(VOICES_SUFFIX).exists()
        self.special_name = special_name_old if is_from_old_extractor else special_name
        self.rename_files()

    def rename_files(self):
        for file in self.folder.glob('**/*{ext}'.format(ext=VOICES_SUFFIX)):
            if self.need_shrine_fix:
                if self.shrine_fix(file):
                    continue

            voice_number = self.match_number(file.stem)
            try:
                if self.hex_mod:
                    if len(voice_number) == 4:
                        continue  # 四位数则跳过（0000、0010这种）
                    voice_number = int(voice_number, 16)
                else:
                    voice_number = int(voice_number)
                    if self.folder.stem == 'voice2':
                        voice_number += 20000
                hex_number = '%05x' % voice_number
                self.rename_file(file, hex_number)
            except ValueError:  # 字母等
                continue

    @staticmethod
    def rename_file(file, hex_number):
        voice_name = voices_list.get(hex_number, '')
        if voice_name:
            if len(voice_name) == 4:
                if voice_name[0] == '':
                    new_name = '%s_%s' % (voice_name[2], voice_name[3])
                elif voice_name[0] == 'EMA_' or voice_name[0] == 'KUJI':
                    new_name = '%s_%s_%s_%s' % (voice_name[0], voice_name[1], voice_name[2], voice_name[3])
                else:
                    new_name = '%s%s_%s_%s' % (voice_name[0], voice_name[1], voice_name[2], voice_name[3])
            else:
                new_name = '%s%s_%s_%s' % (voice_name[0], voice_name[1], voice_name[2], hex_number)
            # new_name = '%s_%s' % (voice_name[2], hex_number)
        else:
            new_name = hex_number

        new_file = file.with_name(new_name).with_suffix(VOICES_SUFFIX)
        if file == new_file:
            return
        try:
            logger.info('>> Rename %s to %s' % (file.name, new_file.name))
            file.rename(new_file)
        except WindowsError:
            logger.error('   Rename FAILED!')

    # 用于修复前期脚本所导致的问题文件名
    @staticmethod
    def shrine_fix(file):
        if (file.name.startswith('EMA_') and file.name[4] != '_') or (
                file.name.startswith('KUJI') and (file.name[4] != '_' and file.name[4] != 'F')):
            new_name = file.name[:4] + '_' + file.name[4:]
            new_file = file.with_name(new_name).with_suffix(VOICES_SUFFIX)
            try:
                logger.info('>> [Shrine Fix] Rename %s to %s' % (file.name, new_file.name))
                file.rename(new_file)
            except WindowsError:
                logger.error('   Rename FAILED!')
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
            voice_number = self.special_name[self.folder.stem].get(file_name, file_name)
        return voice_number


if __name__ == '__main__':
    for voice_path in VOICE_PATH:
        if not voice_path.exists():
            logger.error('please change BASE_PATH to the outer layer of the voice and voice2 folder.')
            sys.exit(20)

    for voice_path in VOICE_PATH:
        ChangeVoiceName(voice_path)
    logger.info("DONE!")
