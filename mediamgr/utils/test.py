'''
    utils.test.py
'''
import unittest
import os
import shutil
from pathlib import Path
import mediamgr.utils as ut

class Test_parse_movie_fn(unittest.TestCase):
    '''
        test case for parse_movie_fn
    '''

    def test_parse_movie_fn_typical(self):
        '''
            test typical file names
        '''
        self.assertEqual(ut.parse_movie_fn('Casino.Royale.2006.1080p.BRrip.x264.YIFY.mp4'),
                         ('Casino Royale', '2006'), msg='typical with dots, 20**')
        self.assertEqual(ut.parse_movie_fn('Chinatown.1974.720p.HDTV.x264.YIFY.mp4'),
                         ('Chinatown', '1974'), msg='typical with dots, 19**')
        self.assertEqual(ut.parse_movie_fn('Chinatown (1974) 720p.HDTV.x264.YIFY.mp4'),
                         ('Chinatown', '1974'), msg='typical with parens')
        self.assertEqual(ut.parse_movie_fn('Blade.Runner.Final.Cut.1997.720p.BluRay.x264.YIFY.mp4'),
                         ('Blade Runner Final Cut', '1997'), msg='typical with dots, 19**')

    def test_parse_movie_fn_title_w_year(self):
        '''
            test file names with title that contain years
        '''
        self.assertEqual(ut.parse_movie_fn('Blade Runner 2049.2017.1080p.WEB-DL.H264.mkv'),
                         ('Blade Runner 2049', '2017'), msg='title with year, spaces/dots')
        self.assertEqual(ut.parse_movie_fn('Blade.Runner.2049.2017.1080p.WEB-DL.H264.mkv'),
                         ('Blade Runner 2049', '2017'), msg='title with year, dots')
        self.assertEqual(ut.parse_movie_fn('Blade Runner 2049 (2017) 1080p.WEB-DL.H264.mkv'),
                         ('Blade Runner 2049', '2017'), msg='title with year, parens')

    def test_parse_movie_fn_title_is_year(self):
        '''
            test file names with title that are years
        '''
        self.assertEqual(ut.parse_movie_fn('1922.2017.720p.NF.WEB-DL.800MB.MkvCage.mkv'),
                         ('1922', '2017'), msg='title is year, dots')
        self.assertEqual(ut.parse_movie_fn('1922.(2017).720p.NF.WEB-DL.800MB.MkvCage.mkv'),
                         ('1922', '2017'), msg='title is year, dots/parens')
        self.assertEqual(ut.parse_movie_fn('1922 (2017) 720p.NF.WEB-DL.800MB.MkvCage.mkv'),
                         ('1922', '2017'), msg='title is year, parens')

class Test_rm_extra_files(unittest.TestCase):
    '''
        Test rm_extra_files Class
    '''
    TEST_PATH = '/tmp/nas_util_test_dir'

    def setUp(self):
        shutil.rmtree(self.TEST_PATH, ignore_errors=True)
        test_path = Path(self.TEST_PATH)
        test_path.mkdir()
        pth = Path(test_path / 'movie.mkv')
        with pth.open(mode='w'):
            pth.write_bytes(b'Binary file contents... '*1000)
        Path(test_path / 'movie.nfo').touch()
        Path(test_path / 'sample.avi').touch()
        dir1 = Path(test_path / 'screens')
        dir1.mkdir()
        Path(dir1 / 'movie.jpg').touch()
        dir2 = Path(test_path / 'subs')
        dir2.mkdir()
        Path(dir2 / 'movie.srt').touch()

    def tearDown(self):
        shutil.rmtree(self.TEST_PATH)

    @staticmethod
    def get_files_set(top_dir):
        '''
            takes dir path
            returns list of contained files
        '''
        res = set([])
        for root, __, files in os.walk(top_dir):
            res.add(root)
            for file in files:
                res.add('/'.join([root, file]))
        return res

    def test_rm_extra_files(self):
        '''
            test rm_extra_files
        '''
        before = set([self.TEST_PATH,
                      self.TEST_PATH + '/movie.mkv',
                      self.TEST_PATH + '/movie.nfo',
                      self.TEST_PATH + '/sample.avi',
                      self.TEST_PATH + '/screens',
                      self.TEST_PATH + '/screens/movie.jpg',
                      self.TEST_PATH + '/subs',
                      self.TEST_PATH + '/subs/movie.srt'])
        after = set([self.TEST_PATH,
                     self.TEST_PATH + '/movie.mkv',
                     self.TEST_PATH + '/subs',
                     self.TEST_PATH + '/subs/movie.srt'])
        actual = self.get_files_set(self.TEST_PATH)
        self.assertSetEqual(actual, before, msg='check test files before')
        result = ut.rm_extra_files(self.TEST_PATH)
        self.assertEqual(result, (self.TEST_PATH + '/movie.mkv', 24000),
                         msg='check big file data')
        actual = self.get_files_set(self.TEST_PATH)
        self.assertSetEqual(actual, after, msg='check test files after')

class Test_tmdb(unittest.TestCase):
    '''
        test tmdb
    '''

    # TODO

class Test_get_data(unittest.TestCase):
    '''
        test get_data
    '''

    # TODO

class Test_fix_filename(unittest.TestCase):
    '''
        test fix_filename
    '''

    # TODO

if __name__ == '__main__':
    unittest.main(verbosity=2)
