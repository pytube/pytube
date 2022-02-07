from pytube import Search
#  might have to handle new objects that might be created by YouTube in the future
def test_completion_suggestions():
    temp = "#crapsnation" #  handled missing hashtagTileRenderer object
    s = Search(temp)
    assert s.completion_suggestions

    temp_1 = "No Time To Die Billie Eilish" #  handled missing movieRenderer object
    s = Search(temp_1)
    assert s.completion_suggestions

    temp_2 = "rangmnam style" #  handled missing showingResultsForRenderer object
    s = Search(temp_2)
    assert s.completion_suggestions

test_completion_suggestions()