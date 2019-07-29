# Vita Scenarios Tools
Vita scenarios converter and tools for "HuneX" game engine. Test for FHA and FSN in Vita.

# Usage
## Vita Scenarios Converter
comes with ABSOLUTELY NO WARRANTY.
```
usage: psvstool.py [-h] input

positional arguments:
  input       input .ini file or folder

optional arguments:
  -h, --help  show this help message and exit
```



## Voices Name Correspondence List Extractor

comes with ABSOLUTELY NO WARRANTY.

*Only for FSN and FHA in Vita.*

```
usage: extract_voices_list.py [-h] input

positional arguments:
  input       input .ini file or folder

optional arguments:
  -h, --help  show this help message and exit
```



## Voice Filenames List from Ema Scene Extractor

comes with ABSOLUTELY NO WARRANTY.

*This script is only for Vita FHA.*

```
usage: extract_voices_list_from_ema.py [-h] input

positional arguments:
  input       input .ini file or folder

optional arguments:
  -h, --help  show this help message and exit
```



## Voice Filenames Renamer

comes with ABSOLUTELY NO WARRANTY.

Rename indexed filenames for voices from Vita to regular. Please change `BASE_PATH` to your voices folder path that include `voice`  and `voice2` folder.



##  TROPHY.TRP Extractor

comes with ABSOLUTELY NO WARRANTY.

Python version for TROPHY.TRP Extractor, the original C version code by Red Squirrel.

```
usage: trpex.py [-h] input_file output_folder

positional arguments:
  input_file     path of your TROPHY.TRP.
  output_folder  output folder.

optional arguments:
  -h, --help     show this help message and exit
```

