from unittest import mock
from pytube import Search

@mock.patch('pytube.request.get')
def test_for_missing_hashtagTileRenderer(request_get, search_suggestion):
    request_get.return_value = search_suggestion
    s = Search("#crapsnation")
    assert s.completion_suggestions == 'No suggestions available'

@mock.patch('pytube.request.get')
def test_test_for_no_suggestions(request_get, search_suggestion):
    request_get.return_value = search_suggestion
    s = Search("crapsnation")
    assert s.completion_suggestions == 'No suggestions available'

@mock.patch('pytube.request.get')
def test_for_missing_movieRenderer(request_get, search_suggestion):
    request_get.return_value = search_suggestion
    s = Search("gone with the wind")
    assert s.completion_suggestions == 'No suggestions available'

@mock.patch('pytube.request.get')
def test_for_showingResultsForRenderer(request_get, search_suggestion):
    request_get.return_value = search_suggestion
    s = Search("rangmnam style")
    assert s.completion_suggestions == [
        'gangnam style just dance', 'gangnam style parody', 'gangnam style fortnite',
        'gangnam style minecraft', 'gangnam style remix', 'gangnam style clean', 
        'gangnam style reaction', 'gangnam style live', 'psy gentleman',
        'gangnam style dance', 'gangnam style 1 hour', 'psy daddy',
        'gangnam style lyrics', 'psy new face'
    ]