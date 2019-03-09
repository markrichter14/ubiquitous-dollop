import os

p = '/media/Media/Video/TV Shows'
fn = 'fn_list.txt'
with open(fn, 'w') as f:
    for dir_path, dir_names, file_names in os.walk(p):
        for n in file_names:
            if n[-4:] not in ['.nfo', '.srt']:
                f.write(str(n)+'\n')

