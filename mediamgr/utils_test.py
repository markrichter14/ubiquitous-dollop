from utils import *
import unittest, os, shutil
from pathlib import Path

class Test_parse_movie_fn(unittest.TestCase):

    def test_parse_movie_fn_typical(self):
        self.assertEqual(parse_movie_fn('Casino.Royale.2006.1080p.BRrip.x264.YIFY.mp4'),
                         ('Casino Royale', '2006'), msg='typical with dots, 20**')
        self.assertEqual(parse_movie_fn('Chinatown.1974.720p.HDTV.x264.YIFY.mp4'),
                         ('Chinatown', '1974'), msg='typical with dots, 19**')
        self.assertEqual(parse_movie_fn('Chinatown (1974) 720p.HDTV.x264.YIFY.mp4'), 
                         ('Chinatown', '1974'), msg='typical wit parens')
        self.assertEqual(parse_movie_fn('Blade.Runner.Final.Cut.1997.720p.BluRay.x264.YIFY.mp4'), 
                         ('Blade Runner Final Cut', '1997'), msg='typical with dots, 19**')
    
    def test_parse_movie_fn_title_w_year(self):
        self.assertEqual(parse_movie_fn('Blade Runner 2049.2017.1080p.WEB-DL.H264.AC3-EVO.mkv'), 
                         ('Blade Runner 2049', '2017'), msg='title with year, spaces/dots')
        self.assertEqual(parse_movie_fn('Blade.Runner.2049.2017.1080p.WEB-DL.H264.AC3-EVO.mkv'), 
                         ('Blade Runner 2049', '2017'), msg='title with year, dots')
        self.assertEqual(parse_movie_fn('Blade Runner 2049 (2017) 1080p.WEB-DL.H264.AC3-EVO.mkv'), 
                         ('Blade Runner 2049', '2017'), msg='title with year, parens')
    
    def test_parse_movie_fn_title_is_year(self):
        self.assertEqual(parse_movie_fn('1922.2017.720p.NF.WEB-DL.800MB.MkvCage.mkv'), 
                         ('1922', '2017'), msg='title is year, dots')
        self.assertEqual(parse_movie_fn('1922.(2017).720p.NF.WEB-DL.800MB.MkvCage.mkv'), 
                         ('1922', '2017'), msg='title is year, dots/parens')
        self.assertEqual(parse_movie_fn('1922 (2017) 720p.NF.WEB-DL.800MB.MkvCage.mkv'), 
                         ('1922', '2017'), msg='title is year, parens')

class Test_rm_extra_files(unittest.TestCase):

    TEST_PATH = '/tmp/nas_util_test_dir'
    
    def setUp(self):
        shutil.rmtree(self.TEST_PATH, ignore_errors=True)
        test_path = Path(self.TEST_PATH)
        test_path.mkdir()
        p = Path(test_path / 'movie.mkv')
        with p.open(mode='w'):
            p.write_bytes(b'Binary file contents... '*1000)
        Path(test_path / 'movie.nfo').touch()
        Path(test_path / 'sample.avi').touch()
        d1 = Path(test_path / 'screens')
        d1.mkdir()
        Path(d1 / 'movie.jpg').touch()
        d2 = Path(test_path / 'subs')
        d2.mkdir()
        Path(d2 / 'movie.srt').touch()
        
    def tearDown(self):
        shutil.rmtree(self.TEST_PATH)
    
    @staticmethod
    def get_files_set(d):
        res = set([])
        for root, __, files in os.walk(d):
            res.add(root)
            for file in files:
                res.add('/'.join([root, file]))
        return res

    def test_rm_extra_files(self):
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
        result = rm_extra_files(self.TEST_PATH)
        self.assertEqual(result, (self.TEST_PATH + '/movie.mkv', 24000), 
                         msg='check big file data')
        actual = self.get_files_set(self.TEST_PATH)
        self.assertSetEqual(actual, after, msg='check test files after')

class Test_tmdb(unittest.TestCase):
    # TODO
    pass

class Test_get_data(unittest.TestCase):
    # TODO
    pass

class Test_fix_filename(unittest.TestCase):
    # TODO
    pass

if __name__ == '__main__':
    unittest.main(verbosity=2)