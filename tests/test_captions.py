from pytube import Caption, CaptionQuery


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
