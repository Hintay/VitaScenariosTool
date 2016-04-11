# Macros Corresponding List
# comes with ABSOLUTELY NO WARRANTY.
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# This file is part of Vita Scenarios Converter.

###########
# Special
###########
ignore_macro = ['SYNC', 'KMW2']
# 有括号
brackets_macro = ['BTXO', 'BIVF', 'MPAU']
# 无逗号
no_comma_macro = ['KHZE', 'PAGE', 'FCAL', 'NEVL', 'KFCH']

ignore_parameters = ['002', '237', '238', '239']
###########

macros = {
	'BFNT':'@font',
	'BIED':'@interlude_end',
	'BIVF':{'0':'@visibleframe', '1':'@invisibleframe'},
	'BIST':'@interlude_start',
	'BIED':'@interlude_end',
	'BRET':'@return',
	'BTXO':{'0':'@textoff', '1':'@texton'},
	'CFAD':{'0':'@fadein', '2':'@rep'},
	'CHCL':{'0':{'0':'@condoff', '2':'@red', '3':'@green', '4':'@blue', '5':'@nega', '6':'@monocro'}, '1':{'2':'@red', '8':'@sepia'}},
	'CHZB':'@haze_back',
	'CHZS':'@stophaze',
	'CHTC':{'1':'@hearttonecombo'},
	#'COND':'',
	'CTRX':'@transex',
	'CCTO':{'0':'@contrastoff'},
	'CCTR':{'1':'@contrast'},
	'FCAL':'@call', #_FCAL((1166; @call storage=街編・1日目-03.ks
	'HRDW':'@redraw',
	'HFAN':'@hfangry',
	'HFBB':'@hfburstblood',
	'HFCN':'@hfchance',
	'HFFA':'hfface',
	'HFFC':'@hffacechg',
	'HFFG':'@hffeelgood',
	'HFSG':'@hfsigh',
	'HFST':'@hfstamp',
	'HFSW':'@hfsweat',
	'HFPP':'@hfpop',
	'HFWW':'@hfwww',
	#'HFTF':'@tf',
	#'HFUL':{'2':''}, #_HFUL(2; [hfu]字[hfl] 须特殊处理
	'HSMG':{'0':'@smudge'},
	'KDSH':'@dash',
	'KDSS':{'0':'@stopdash'},
	'KDSW':'@wdash',
	'KFCH':'@chgfg',
	'KFG0':'@fg',
	'KFMV':'@movefg', # @monocro
	'KMST':'@stopmove', # @stopsplinemove
	'KMWT':'@wm',
	#'KMW2':'',
	'KMVE':'@move',
	'KMLP':'@loopmove',
	'KSMW':'@wsplinemove',
	'KHZE':'@haze',
	'KFND':'@find',
	'KSMV':'@splinemove',
	'KIMG':'@image',
	'MPLY':{'0':'@play', '2':'@xchgbgm'},
	'MPAU':{'0':'@playresume', '1':'@playpause'},
	'MSTP':{'0':'@playstop'},
	'NEVL':'@eval', #_NEVL(exp=Scripts.execStorage(HanafudaPlugin.tjs);
	'NCL0':'@cl',
	'NCLF':'@clfg',
	'NCIN':{'0':'@cinesco'},
	'NCTR':'@cltransparent',
	'NNOB':'@noise_back',
	'NNOI':{'0':'@noise'},
	'NNOS':{'0':'@stopnoise'}, # @noise_off
	'NQUS':'@stopquake',
	'NQUL':'@lquake',
	'NQLS':'@stoplquake',
	'NSHK':{'0':'@shock'},
	'PAGE':'*page',
	#'PEND':'', #_PEND(; 占位符？
	#'QSET':{'0':'@call storage=QuizSystem.ks\n@iscript'},
	'QADE':'@endscript',
	'QADS':'.quiz	= %[%s]',
	'QADD':'quiz:[%s]',
	'SESF':'@sestop',
	'SEPF':{'0':'@se', '2':'@seloop', '0tdeepdaytime':'@setdeepdaytime', '0thscene':'@sethscene'},
	'SEFF':'@fadese',
	'SNOW':{'0':'@snowuninit', '1':{'800':'@snowinit forevisible=false backvisible=true'}}, #@snowopt backvisible=false
	'TDSP':{'0':'@displayedoff', '1':'@displayedon'},
	'TPG0':'@pg',
	'TWND':{'0':'@setdaytime', '1':'@setnighttime'},
	'WTFT':{'0':'@wait', '0acanskip=false':'@wait acanskip=false'},
	'WTKY':'@lr',
	'WNDS':{'0':'@window_start', '1':'@window_end', '2':''},
	'MFNR':'@resetfont', # and @rf
	#'SYNC;:'@starttag',
	#'WKST':'',
	#'MVPL':{2:'@playmovie'},
	#'MSAD':'', #文本框
}
# @smudge @blur @smudgeoff @bluroff @slideopencombo @slideclosecombo @pasttime 被_CFAD所替代
# @shortcutkey @history 被去除

# _WKST(G054,1; @night_start _WKST(G011,1; 真・冒頭-16.ini
# _QJMP(_D990,quiz14_correct,quiz14_incorrect; @quiz success=*page11 failed=*page12
# _HFTF(0,`026:クイズタイガー編クリア,`235:1; @eval exp="tf['クイズタイガー編クリア']=true"

# 以`开头
parameters = {
	#'002':'haverule', # 2=on 0=none ?
	'003':'time',
	'004':'vague',
	'005':'storage', # bg for @rep?
	'008':'canskip',
	'010':'page',
	'012':'layer', # -2=&no -1=base 255=all
	'013':'left',
	'014':'top',
	'015':'opacity',
	'017':'accel',
	'018':'cx',
	'019':'cy',
	'020':'imag',
	'021':'mag',
	'023':'range', #_HSMG
	'024':'level',
	#'026':'tf', #_HFTF ??
	'032':'pos',
	'033':'index',
	'034':'noclear',
	'035':'fliplr',
	'036':'flipud',
	'037':'poss',
	'039':'indexes',
	'040':'opacities',
	'041':'vmax',
	'042':'count',
	'043':'delay',
	'044':'type',
	'045':'nowait',
	'046':'textoff',
	'047':'irot',
	'048':'mx',
	'049':'my',
	'050':'rot',
	'051':'face',
	'067':'hmax',
	'068':'upper',
	'069':'lower',
	'074':'volume',
	'075':'target',
	'076':'hidefg',
	'086':'color',
	'087':'storages',
	'089':'center',
	'090':'upperpow',
	'091':'lowerpow',
	'092':'centerpow',
	#'094':'id', #_SYNC starttag
	'096':'lwaves',
	'098':'base',
	'099':'px',
	'100':'py',
	'101':'deg',
	'111':'overlap',
	#'113':'', #_KDSH @dash
	'114':'monocro', 
	'115':'both', #_KFMV @movefg
	'116':'mover', #_KMLP @loopmove
	'117':'frame',
	'118':'decel',
	'119':'spread', #_KMVE @move
	'121':'intime',
	'122':'waves',
	'124':'standard',
	'128':'edgecolor',
	'131':'italic',
	#'139':'bg', #? _KDSH @dash _COND
	'141':'indexs',
	'164':'rule',
	'170':'spline',
	'171':'affine',
	'172':'path',
	'216':'last',
	'217':'lv2off',
	'218':'fliplrs',
	'219':'flipuds',
	'220':'avoid',
	'221':'force',
	'222':'layers',
	'223':'lefts',
	'224':'tops',
	'227':'colors',
	'228':'monos',
	'229':'mono',
	'230':'noquake',
	'231':'bluroff',
	'232':'chara',
	'233':'question',
	'234':'alters',
	#'235':'result',
	'236':'nospline',
	#'237':'', #@loopmove
	#'238':'', #@chgfg
	#'239':'', #@loopmove
}

target = {
	'1':'bg',
	'2':'fg',
	'3':'all',
}

page = {
	'0':'back',
	'1':'fore'
}

call = {
	'(1013':'カレン-01.ks',
	'(1166':'街編・1日目-03.ks',
	'(1179':'街編・1日目-24.ks'
}

rule = {
	'001':'crystal_bt',
	'002':'l2r_half',
	'003':'l2r_ss',
	'004':'mosaic_lt_rb',
	'005':'pageleft',
	'006':'pageright',
	'007':'r2l_half',
	'008':'r2l_sfs',
	'009':'r2l_ss',
	'010':'sparm',
	'011':'trans000',
	'012':'カーテン左から',
	'013':'カーテン上から',
	'014':'シャッター下から',
	'015':'シャッター左から',
	'016':'シャッター上から',
	'022':'モザイク',
	'027':'やや細かい縦ブラインド(中央から左右へ)',
	'028':'右から左へ',
	'029':'右渦巻き',
	'030':'右下から左上へ',
	'031':'右上から左下へ',
	'032':'円形(外から中へ)',
	'033':'円形(中から外へ)',
	'036':'下から上へ',
	'037':'左から右へ',
	'038':'左下から右上へ',
	'039':'左回り',
	'041':'左上から右下へ',
	'048':'斜めチェッカー',
	'052':'上から下へ',
	'053':'走る感じ(右から)',
	'054':'走る感じ(下から)',
	'055':'走る感じ(上から)',
	'056':'走る感じ',
	'058':'短冊(下から)',
	'059':'短冊(上から)',
	'060':'短冊細(右から)',
	'061':'短冊細(左から)',
	'062':'虫食い',
	'063':'波',
	'064':'放射状(時計回り)',
	'066':'koyama02r',
	'067':'カレン割',
	'070':'crystal_bt_r',
	'071':'forfd05',
	'072':'forfd05_2',
	'073':'forfd逆月07',
	'074':'forRider01',
	'075':'koyama01r',
	'076':'koyama02r2',
	'078':'中央から左右へ',
	'079':'左回り連続2',
}

pos = {
	'-1':'all',
	'1':'l',
	'2':'r',
	'3':'lc',
	'4':'rc',
	'5':'c',
	'1ower':'lower', #替换文本 
}

layer = {
	'-2':'&no',
	'-1':'base',
	'255':'all'
}

special_macro = { 'target':target, 'page':page, 'call':call, 'rule':rule, 'pos':pos, 'layer':layer }

# @s(28) @large @s(16) @small
