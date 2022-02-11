from pytube import Search


def test_for_completion_suggestions():

    temp_0 = "#crapsnation"  # check missing hashtagTileRenderer object
    try:
        s = Search(temp_0)
        if 'Unexpected renderer encountered.' not in s.completion_suggestions:
            assert True
    except KeyError:
        assert False

    temp = "crapsnation"  # check for words without suggestions
    try:
        s = Search(temp)
        if 'Unexpected renderer encountered.' not in s.completion_suggestions:
            assert True
    except KeyError:
        assert False

    temp_1 = "gone with the wind"  # check missing movieRenderer object
    try:
        s = Search(temp_1)
        if 'Unexpected renderer encountered.' not in s.completion_suggestions:
            assert True
    except KeyError:
        assert False

    temp_2 = "rangmnam style"  # check missing showingResultsForRenderer object
    try:
        s = Search(temp_2)
        if 'Unexpected renderer encountered.' not in s.completion_suggestions:
            assert True
    except KeyError:
        assert False
