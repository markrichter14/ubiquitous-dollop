import os

p = '/media/Media/Video/Movies'
fn = 'movie_list.txt'
with open(fn, 'w') as f:
    for dir_path, dir_names, file_names in os.walk(p):
        for n in file_names:
            if n[-4:] in [".mp4", ".avi", ".m4v", ".mkv", ".mpg"]:
                f.write(str(n)+'\n')

