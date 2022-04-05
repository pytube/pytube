from pytube import Search
import unittest

class TestCompletionSuggestions(unittest.TestCase):
    def test_for_missing_hashtagTileRenderer(self): 
        s = Search("#crapsnation") # check missing hashtagTileRenderer object
        self.assertTrue(s.completion_suggestions, 'No suggestions available')
    
    def test_for_no_suggestions(self):
        s = Search("crapsnation") # check for words without suggestions
        self.assertTrue(s.completion_suggestions, 'No suggestions available')

    def test_for_missing_movieRenderer(self):
        s = Search("gone with the wind") # check missing movieRenderer object
        self.assertTrue(s.completion_suggestions, 'No suggestions available')

    def test_for_showingResultsForRenderer(self):
        s = Search("rangmnam style") # check missing showingResultsForRenderer object
        res = ['gangnam style just dance', 'gangnam style parody', 'gangnam style fortnite',
                'gangnam style minecraft', 'gangnam style remix', 'gangnam style clean', 
                'gangnam style reaction', 'gangnam style live', 'psy gentleman',
                'gangnam style dance', 'gangnam style 1 hour', 'psy daddy',
                'gangnam style lyrics', 'psy new face']
        self.assertTrue(s.completion_suggestions, res)

if __name__ == '__main__':
    unittest.main()