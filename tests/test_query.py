"""Unit tests for the :class:`StreamQuery <StreamQuery>` class."""
import pytest


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        ({"progressive": True}, [17, 18, 22]),
        ({"resolution": "720p"}, [22, 136, 247, 398]),
        ({"res": "720p"}, [22, 136, 247, 398]),
        ({"fps": 24, "resolution": "480p"}, [135, 244, 397]),
        ({"mime_type": "audio/mp4"}, [139, 140]),
        ({"type": "audio"}, [139, 140, 249, 250, 251]),
        ({"subtype": "3gpp"}, [17]),
        ({"abr": "128kbps"}, [140]),
        ({"bitrate": "128kbps"}, [140]),
        ({"audio_codec": "opus"}, [249, 250, 251]),
        ({"video_codec": "vp9"}, [248, 247, 244, 243, 242, 278]),
        ({"only_audio": True}, [139, 140, 249, 250, 251]),
        ({"only_video": True, "video_codec": "avc1.4d4015"}, [133]),
        ({"adaptive": True, "resolution": "1080p"}, [137, 248, 399]),
        ({"custom_filter_functions": [lambda s: s.itag == 18]}, [18]),
    ],
)
def test_filters(test_input, expected, cipher_signature):
    """Ensure filters produce the expected results."""
    result = [s.itag for s in cipher_signature.streams.filter(**test_input)]
    assert result == expected


@pytest.mark.parametrize("test_input", ["first", "last"])
def test_empty(test_input, cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.last` and
    :meth:`~pytube.StreamQuery.first` return None if the resultset is
    empty.
    """
    query = cipher_signature.streams.filter(video_codec="vp20")
    fn = getattr(query, test_input)
    assert fn() is None


def test_get_last(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.last` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams[-1].itag == 251


def test_get_first(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.first` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams.first().itag == cipher_signature.streams[0].itag


def test_order_by(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.order_by` sorts the list of
    :class:`Stream <Stream>` instances in the expected order.
    """
    itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio").order_by("itag")
    ]
    expected_itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio")
    ]
    expected_itags.sort()

    assert itags == expected_itags


def test_order_by_descending(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.desc` sorts the list of
    :class:`Stream <Stream>` instances in the reverse order.
    """
    # numerical values
    itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio")
        .order_by("itag")
        .desc()
    ]
    expected_itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio")
    ]
    expected_itags.sort(reverse=True)
    assert itags == expected_itags


def test_order_by_non_numerical(cipher_signature):
    mime_types = [
        s.mime_type
        for s in cipher_signature.streams.filter(res="360p")
        .order_by("mime_type")
        .desc()
    ]
    assert mime_types == ["video/webm", "video/mp4", "video/mp4", "video/mp4"]


def test_order_by_ascending(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.desc` sorts the list of
    :class:`Stream <Stream>` instances in ascending order.
    """
    # numerical values
    itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio")
        .order_by("itag")
        .asc()
    ]
    expected_itags = [
        s.itag
        for s in cipher_signature.streams.filter(type="audio")
    ]
    assert itags == expected_itags


def test_order_by_non_numerical_ascending(cipher_signature):
    mime_types = [
        s.mime_type
        for s in cipher_signature.streams.filter(res="360p")
        .order_by("mime_type")
        .asc()
    ]
    assert mime_types == ["video/mp4", "video/mp4", "video/mp4", "video/webm"]


def test_order_by_with_none_values(cipher_signature):
    abrs = [s.abr for s in cipher_signature.streams.order_by("abr").asc()]
    assert abrs == [
        "24kbps",
        "48kbps",
        "50kbps",
        "70kbps",
        "96kbps",
        "128kbps",
        "160kbps",
        "192kbps"
    ]


def test_get_by_itag(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.get_by_itag` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams.get_by_itag(18).itag == 18


def test_get_by_non_existent_itag(cipher_signature):
    assert not cipher_signature.streams.get_by_itag(22983)


def test_get_by_resolution(cipher_signature):
    assert cipher_signature.streams.get_by_resolution("360p").itag == 18


def test_get_lowest_resolution(cipher_signature):
    assert cipher_signature.streams.get_lowest_resolution().itag == 18


def test_get_highest_resolution(cipher_signature):
    assert cipher_signature.streams.get_highest_resolution().itag == 22


def test_filter_is_dash(cipher_signature):
    streams = cipher_signature.streams.filter(is_dash=False)
    itags = [s.itag for s in streams]
    assert itags == [17, 18, 22]


def test_get_audio_only(cipher_signature):
    assert cipher_signature.streams.get_audio_only().itag == 140


def test_get_audio_only_with_subtype(cipher_signature):
    assert cipher_signature.streams.get_audio_only(subtype="webm").itag == 251


def test_sequence(cipher_signature):
    assert len(cipher_signature.streams) == 26
    assert cipher_signature.streams[0] is not None


def test_otf(cipher_signature):
    non_otf = cipher_signature.streams.otf()
    assert len(non_otf) == 26

    otf = cipher_signature.streams.otf(True)
    assert len(otf) == 0


def test_repr(cipher_signature):
    assert repr(
        cipher_signature.streams.filter(
            progressive=True, subtype="mp4", resolution="360p"
        )
    ) == (
        '[<Stream: itag="18" mime_type="video/mp4" '
        'res="360p" fps="24fps" vcodec="avc1.42001E" '
        'acodec="mp4a.40.2" progressive="True" type="video">]'
    )
