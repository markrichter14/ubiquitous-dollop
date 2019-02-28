import os

p = '/media/Media/Video/TV Shows'
fn = 'show_list.txt'
with open(fn, 'w') as f:
    for dir_path, dir_names, file_names in os.walk(p):
        for n in dir_names:
            f.write(str(n)+'\n')
        break

