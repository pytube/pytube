from unittest import mock
from unittest.mock import patch, mock_open

from pytube import Caption, CaptionQuery


def test_float_to_srt_time_format():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    assert caption1.float_to_srt_time_format(3.89) == "00:00:03,890"


def test_caption_query_all():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    assert caption_query.captions == [caption1, caption2]


def test_caption_query_get_by_language_code_when_exists():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    assert caption_query.get_by_language_code("en") == caption1


def test_caption_query_get_by_language_code_when_not_exists():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    assert caption_query.get_by_language_code("hello") is None


@mock.patch("pytube.captions.Caption.generate_srt_captions")
def test_download(srt):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        srt.return_value = ""
        caption = Caption(
            {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
        )
        caption.download("title")
        assert open_mock.call_args_list[0][0][0].split("/")[-1] == "title (en).srt"


@mock.patch("pytube.captions.Caption.generate_srt_captions")
def test_download_with_prefix(srt):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        srt.return_value = ""
        caption = Caption(
            {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
        )
        caption.download("title", filename_prefix="1 ")
        assert open_mock.call_args_list[0][0][0].split("/")[-1] == "1 title (en).srt"


@mock.patch("pytube.captions.Caption.xml_captions")
def test_download_xml_and_trim_extension(xml):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        xml.return_value = ""
        caption = Caption(
            {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
        )
        caption.download("title.xml", srt=False)
        assert open_mock.call_args_list[0][0][0].split("/")[-1] == "title (en).xml"


def test_repr():
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    assert str(caption) == '<Caption lang="name1" code="en">'
