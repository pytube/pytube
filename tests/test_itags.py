from pytube import itags


def test_get_format_profile():
    profile = itags.get_format_profile(22)
    assert profile["resolution"] == "720p"


def test_get_format_profile_non_existant():
    profile = itags.get_format_profile(2239)
    assert profile["resolution"] is None
