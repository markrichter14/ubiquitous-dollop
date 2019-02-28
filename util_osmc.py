import os
import string
import shutil
import re

MOVE_DIR = ''
TV_DIR = ''

FILE_TYPES = [".mp4", ".avi", ".srt", ".m4v", ".mkv", ".mpg"]
EXCLUDE_FOLDERS = ["Sample"]

#########1#########2#########3#########4#########5#########6#########7#########8
# Directories

def get_shows(remote_path, include_seasons=False):
    '''
    Takes strings, remote_path, for remote path.
    Returns a dict, show_info, that contains the shows and seasons.
    '''
    # show info
    show_info = {} # {"show_name":set([season_nums]}

    #remote_tv_path = remote_path + VIDEO_DIR + TV_DIR
    remote_tv_path = TV_DIR
    len_tv_path = len(remote_tv_path)

    for dir_path, dir_names, file_names in os.walk(remote_tv_path):
        if dir_path == remote_tv_path:
            for d in dir_names:
                show_info[d] = set()
                print d
        if include_seasons:
            for d in dir_names:
                if d[:7] == 'Season ':
                    show_name = dir_path[len_tv_path:]
                    season_num = int(d[7:])
                    seasons = show_info.get(show_name, set())
                    seasons.add(season_num)
                    show_info[show_name] = seasons
                    print show_name + "\\" + d
        else:
            return show_info
##            while len(dir_names) > 0:
##                del dir_names[0]

    return show_info

#def create_local_dirs(remote_path, local_path, make_folders=True, make_path=True):
#    '''
#    Takes strings, remote_path and local_path, for remote and local paths.
#    Reads media center file structure, creates local copy of folders, returns a
#    dict, show_info, that contains the shows and seasons.
#    '''
#    # show info
#    show_info = {} # {"show_name":set([season_nums]}
#
#    # top dirs
#    if make_path: create_local_top_dirs(local_path)
#
#    remote_tv_path = remote_path + VIDEO_DIR + TV_DIR
#    len_tv_path = len(remote_tv_path)
#
#    for dir_path, dir_names, file_names in os.walk(remote_tv_path):
#        for d in dir_names:
#            if d[:7] == 'Season ':
#                show_name = dir_path[len_tv_path:]
#                season_num = int(d[7:])
#                seasons = show_info.get(show_name, set())
#                seasons.add(season_num)
#                show_info[show_name] = seasons
#                print local_tv_path + show_name + "\\" + d
#                if make_folders: os.makedirs(local_tv_path + show_name + "\\" + d)
#
#    return show_info
#
#def create_local_top_dirs(local_path):
#    '''
#    Takes strings, local_path, for local path.
#    Creates local copy of Video, Movies, and TV Shows.
#    '''
#    # Movies
#    os.makedirs(local_path + VIDEO_DIR + MOVIE_DIR)
#    # TV Shows
#    local_tv_path = local_path + VIDEO_DIR + TV_DIR
#    os.makedirs(local_tv_path)

def get_file_names(path):
    '''
    Take the path for a directory of video files
    Returns a list of the file names for files of the type matching FILE_TYPES.
    '''
    result = []
    print "Getting file names..."
    for dir_path, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            if file_name[-4:] in FILE_TYPES:
                result.append(file_name)
                print "  Adding", file_name

    return result

def verify_match(file_name, show_name):
    '''
    Returns true if user confirms show_name match to file_name.
    '''
    result = raw_input("\n'" + file_name + "'  was matched to  '" + show_name
                                               + "'\n\nIs this correct? (Y/n)")
    return result.lower() in ["y", "yes", ""]

def prompt_to_move():
    '''
    Returns true if user confirms.
    '''
    result = raw_input("\nWould you like to move local files to the media server? (Y/n) ")
    return result.lower() in ["y", "yes", ""]

def prompt_for_season(file_name, show_name):

    pattern_string = '.*?Season.?(\d{1,2}).*'
    pattern = re.compile(pattern_string, re.IGNORECASE)
    match = pattern.match(file_name)
    if match != None:
        return int(match.group(1))

    done = False
    while not done:
        result = raw_input("\n'" + file_name + "' was matched to '" + show_name
                                        + "'\n\nWhat is the correct season?  ")
        try:
            result = int(result)
        except:
            pass

        if type(result) == int and result >= 0:
            done = True
        else:
            print "\n\nThat input was not understood."

    return result

def cleanup_file_name(name):
    '''
    Code and concepts taken from tw-video-scraper (c)2011, Daniel Vijge
    https://github.com/danielvijge/tw-video-scraper
    '''
    name = name.lower()
    name = name.replace('.',' ')
    name = name.replace('_',' ')
    name = name.strip()
    while name.endswith('-'):
        name = name.strip('-')
        name = name.strip()
    return name

def split_file_name(file_name):
    '''
    takes a string, file_name, of a tv show and parses the name, season, and
    episode.

    Returns a tuple of the name, season, and episode or a tuple of None if not
    matched.

    Code and concepts taken from tw-video-scraper (c)2011, Daniel Vijge
    https://github.com/danielvijge/tw-video-scraper
    '''
    patterns = ['(.*?)S(\d{1,2})[._x]?E(\d{2})(.*)', #S01E02, S1E2, S01.E02, S01_E02, S01xE02
                '(.*?)\[?(\d{1,2})x(\d{2})\]?(.*)', #1x02, 
                '(.*?)Season.?(\d{1,2}).*?Episode.?(\d{1,2})(.*)', #season 1 - episode 01
                '(.*?[20\d{2}|19\d{2}]*.*?)\[?(\d{1,2})(\d{2})\]?(.*)', #20dd|19dd 102
                '(.*?20\d{2}.*?)\[?(\d{1,2})(\d{2})\]?(.*)', #20dd 102
                '(.*?19\d{2}.*?)\[?(\d{1,2})(\d{2})\]?(.*)', #19dd 102
                '(.*?)\[?(\d{1,2})(\d{2})\]?(.*)'] #102

    seriepatterns = ['(.*?)S(\d{1,2})E(\d{2})(.*)',
					    '(.*?)\[?(\d{1,2})x(\d{2})\]?(.*)',
                        '(.*?)Season.?(\d{1,2}).*?Episode.?(\d{1,2})(.*)']

    moviepatterns = ['(.*?)\((\d{4})\)(.*)',
					    '(.*?)\[(\d{4})\](.*)',
					    '(.*?)\{(\d{4})\}(.*)',
					    '(.*?)(\d{4})(.*)',
					    '(.*?)\.(avi|mkv|mpg|mgep|mp4)',
                        '(.*)']

    for pattern in patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        match = regex.match(file_name)
        if match != None:
            return (cleanup_file_name(match.group(1)), int(match.group(2)),
                                                            int(match.group(3)))
    return (None, None, None)

def move_files(search_path, dest_path, show_info):
    '''

    '''
    MIN_MATCH = 80

    alfa_str = string.lowercase + string.digits + "!#$%&'()+,-.;=@[]^_`{}~ "
    alfa = set([char for char in alfa_str])
    spaces = [' ', '_', '.', '(', ')']
    match_score = 10
    scoring_matrix = build_scoring_matrix3(alfa, spaces, match_score,
                                    -match_score, match_score/2, -match_score/2)

    for dir_path, dir_names, file_names in os.walk(search_path):
        parent = dir_path.split("\\")[-1]
        for file_name in file_names:
            if file_name[-4:] in FILE_TYPES and parent not in EXCLUDE_FOLDERS:
                best_score = float('-inf')
                split = split_file_name(file_name)
                if split[0] != None:
                    file_seq = split[0]
                else:
                    file_seq = file_name.lower()
                for show_name in show_info:
                    show_seq = show_name.lower()
                    local_align_matrix = compute_alignment_matrix(file_seq,
                                                show_seq, scoring_matrix, False)
                    result = compute_local_alignment(file_seq, show_seq,
                                             scoring_matrix, local_align_matrix)
                    score = (1. * result[0] * len(result[2]) / len(show_name))
                    #print result, score, show_name
                    if score > best_score:
                        best_score = score
                        best_match = show_name
                        best_result = result

                percent_match = (100 * best_result[0] /
                                                (len(best_match) * match_score))
                #print percent_match,
                season = split[1]
                if percent_match >= MIN_MATCH or verify_match(file_name,
                                                                    best_match):
                    if split[1] == None:
                        season = prompt_for_season(file_name, best_match)
                    print ("\nMoving '" + file_name + "' to '" + best_match
                                               + "\Season " + str(season) + "'")
                    dest_dir = dest_path + best_match + "\\Season " + str(season)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.move(dir_path + "\\" + file_name, dest_dir)


def write_var(var, file_name):
    '''
    Takes a variable, var, and a string, file_name, for the path/file.
    Writes var as a string to file_name.
    '''
    with open(file_name, "w") as f:
        f.write(str(var))


def read_var(file_name):
    '''
    Returns a variable from path/file, file_name.
    '''
    with open(file_name, "r") as f:
        var = eval(f.read())
    return var


#########1#########2#########3#########4#########5#########6#########7#########8
# Matrix functions

def build_scoring_matrix3(alphabet, spaces, diag_score, off_diag_score,
                           space_score, dash_score):
    '''
    Takes as input two sets of characters, alphabet and spaces, and scores:
        diag_score, off_diag_score, space_score, dash_score.

    Returns a dictionary of dictionaries whose entries are indexed by pairs of
        characters in alphabet plus '*'.
    '''
    result = {}
    characters = set(char for char in alphabet)
    characters.add('*')
    for char_i in characters:
        temp_dict = {}
        for char_j in characters:
            if char_i == '*' or char_j == '*':
                temp_dict[char_j] = dash_score
            elif char_i == char_j:
                temp_dict[char_j] = diag_score
            elif char_i in spaces and char_j in spaces:
                temp_dict[char_j] = space_score
            else:
                temp_dict[char_j] = off_diag_score
        result[char_i] = temp_dict
    return result

def compute_alignment_matrix(seq_x, seq_y, scoring_matrix, global_flag=True):
    '''
    Takes as input two sequences, seq_x and seq_y, whose elements share a common
    alphabet with the scoring matrix, scoring_matrix. The function computes and
    returns the alignment matrix for seq_x and seq_y. If global_flag is True,
    each entry of the alignment matrix is computed using global alignment. If
    global_flag is False, each entry is computed using Local Pairwise Alignment.
    '''
    len_x = len(seq_x)
    len_y = len(seq_y)
    result = [[0]]
    for index_j in range(1, len_y + 1):
        y_char = seq_y[index_j - 1]
        if y_char not in scoring_matrix:
            y_char = "*"
        value = result[0][index_j - 1] + scoring_matrix['*'][y_char]
        if not global_flag:
            value = max(value, 0)
        result[0].append(value)
    for index_i in range(1, len_x + 1):
        x_char = seq_x[index_i - 1]
        if x_char not in scoring_matrix:
            x_char = "*"
        value = result[index_i - 1][0] + scoring_matrix[x_char]['*']
        if not global_flag:
            value = max(value, 0)
        result.append([value])
        for index_j in range(1, len_y + 1):
            y_char = seq_y[index_j - 1]
            if y_char not in scoring_matrix:
                y_char = "*"
            cell_diag = result[index_i - 1][index_j - 1] \
                        + scoring_matrix[x_char][y_char]
            cell_up = result[index_i - 1][index_j] \
                      + scoring_matrix[x_char]['*']
            cell_left = result[index_i][index_j - 1] \
                        + scoring_matrix['*'][y_char]
            value = max(cell_diag, cell_up, cell_left)
            if not global_flag:
                value = max(value, 0)
            result[index_i].append(value)
    return result

#########1#########2#########3#########4#########5#########6#########7#########8
# Alignment functions

def compute_global_alignment(seq_x, seq_y, scoring_matrix, alignment_matrix):
    '''
    Takes as input two sequences, seq_x and seq_y, whose elements share a common
    alphabet with the scoring matrix, scoring_matrix. This function computes a
    global alignment of seq_x and seq_y using the global alignment matrix,
    alignment_matrix.

    The function returns a tuple of the form (score, align_x, align_y) where
    score is the score of the global alignment, align_x and align_y. Note that
    align_x and align_y should have the same length and may include the padding
    character '*'.
    '''
    idx_i = len(seq_x)
    idx_j = len(seq_y)
    score = alignment_matrix[idx_i][idx_j]
    align_x = ""
    align_y = ""

    while idx_i > 0 and idx_j > 0:
        x_char = seq_x[idx_i - 1]
        if x_char not in scoring_matrix:
            x_char = "*"
        y_char = seq_y[idx_j - 1]
        if y_char not in scoring_matrix:
            y_char = "*"
        if alignment_matrix[idx_i][idx_j] == alignment_matrix[idx_i - 1][idx_j - 1] \
                                               + scoring_matrix[x_char][y_char]:
            align_x = x_char + align_x
            align_y = y_char + align_y
            idx_i -= 1
            idx_j -= 1
        elif alignment_matrix[idx_i][idx_j] == alignment_matrix[idx_i - 1][idx_j] \
                                                  + scoring_matrix[x_char]['*']:
            align_x = x_char + align_x
            align_y = '*' + align_y
            idx_i -= 1
        else:
            align_x = '*' + align_x
            align_y = y_char + align_y
            idx_j -= 1

    while idx_i > 0:
        x_char = seq_x[idx_i - 1]
        if x_char not in scoring_matrix:
            x_char = "*"
        align_x = x_char + align_x
        align_y = '*' + align_y
        idx_i -= 1
    while idx_j > 0:
        y_char = seq_y[idx_j - 1]
        if y_char not in scoring_matrix:
            y_char = "*"
        align_x = '*' + align_x
        align_y = y_char + align_y
        idx_j -= 1

    return (score, align_x, align_y)

def compute_local_alignment(seq_x, seq_y, scoring_matrix, alignment_matrix):
    '''
    Takes as input two sequences, seq_x and seq_y, whose elements share a common
    alphabet with the scoring matrix scoring_matrix. This function computes a
    local alignment of seq_x and seq_y using the local alignment matrix,
    alignment_matrix.

    The function returns a tuple of the form (score, align_x, align_y) where
    score is the score of the optimal local alignment, align_x and align_y. Note
    that align_x and align_y should have the same length and may include the
    padding character '*'.
    '''

    score = float("-inf")
    for index_i in range(len(seq_x) + 1):
        for index_j in range(len(seq_y) + 1):
            if alignment_matrix[index_i][index_j] > score:
                score = alignment_matrix[index_i][index_j]
                max_cell = (index_i, index_j)
    align_x = ""
    align_y = ""
    idx_i = max_cell[0]
    idx_j = max_cell[1]

    while alignment_matrix[idx_i][idx_j] != 0:
        x_char = seq_x[idx_i - 1]
        if x_char not in scoring_matrix:
            x_char = "*"
        y_char = seq_y[idx_j - 1]
        if y_char not in scoring_matrix:
            y_char = "*"
        if alignment_matrix[idx_i][idx_j] == alignment_matrix[idx_i - 1][idx_j - 1] \
                                               + scoring_matrix[x_char][y_char]:
            align_x = x_char + align_x
            align_y = y_char + align_y
            idx_i -= 1
            idx_j -= 1
        elif alignment_matrix[idx_i][idx_j] == alignment_matrix[idx_i - 1][idx_j] \
                                                  + scoring_matrix[x_char]['*']:
            align_x = x_char + align_x
            align_y = '*' + align_y
            idx_i -= 1
        else:
            align_x = '*' + align_x
            align_y = y_char + align_y
            idx_j -= 1

    return (score, align_x, align_y)

#########1#########2#########3#########4#########5#########6#########7#########8
# Execution

#shows_file = LOCAL_DIR + "Shows.txt"
#shows = read_var(shows_file)
#shows = create_local_dirs(REMOTE_DIR, LOCAL_DIR, False)
#create_local_top_dirs(LOCAL_DIR)
shows = get_shows(TV_DIR)
#write_var(shows, shows_file)

move_files(MOVE_DIR, TV_DIR, shows)
#if prompt_to_move():
#    shutil.move(LOCAL_DIR + VIDEO_DIR, REMOTE_DIR)