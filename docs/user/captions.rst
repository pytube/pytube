.. _captions:

Subtitle/Caption Tracks
=======================

Pytube exposes the caption tracks in much the same way as querying the media
streams. Let's begin by switching to a video that contains them::

    >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
    >>> yt.captions
    {'ar': <Caption lang="Arabic" code="ar">, 'zh-HK': <Caption lang="Chinese (Hong Kong)" code="zh-HK">, 'zh-TW': <Caption lang="Chinese (Taiwan)" code="zh-TW">, 'hr': <Caption lang="Croatian" code="hr">, 'cs': <Caption lang="Czech" code="cs">, 'da': <Caption lang="Danish" code="da">, 'nl': <Caption lang="Dutch" code="nl">, 'en': <Caption lang="English" code="en">, 'en-GB': <Caption lang="English (United Kingdom)" code="en-GB">, 'et': <Caption lang="Estonian" code="et">, 'fil': <Caption lang="Filipino" code="fil">, 'fi': <Caption lang="Finnish" code="fi">, 'fr-CA': <Caption lang="French (Canada)" code="fr-CA">, 'fr-FR': <Caption lang="French (France)" code="fr-FR">, 'de': <Caption lang="German" code="de">, 'el': <Caption lang="Greek" code="el">, 'iw': <Caption lang="Hebrew" code="iw">, 'hu': <Caption lang="Hungarian" code="hu">, 'id': <Caption lang="Indonesian" code="id">, 'it': <Caption lang="Italian" code="it">, 'ja': <Caption lang="Japanese" code="ja">, 'ko': <Caption lang="Korean" code="ko">, 'lv': <Caption lang="Latvian" code="lv">, 'lt': <Caption lang="Lithuanian" code="lt">, 'ms': <Caption lang="Malay" code="ms">, 'no': <Caption lang="Norwegian" code="no">, 'pl': <Caption lang="Polish" code="pl">, 'pt-BR': <Caption lang="Portuguese (Brazil)" code="pt-BR">, 'pt-PT': <Caption lang="Portuguese (Portugal)" code="pt-PT">, 'ro': <Caption lang="Romanian" code="ro">, 'ru': <Caption lang="Russian" code="ru">, 'sk': <Caption lang="Slovak" code="sk">, 'es-419': <Caption lang="Spanish (Latin America)" code="es-419">, 'es-ES': <Caption lang="Spanish (Spain)" code="es-ES">, 'sv': <Caption lang="Swedish" code="sv">, 'th': <Caption lang="Thai" code="th">, 'tr': <Caption lang="Turkish" code="tr">, 'uk': <Caption lang="Ukrainian" code="uk">, 'ur': <Caption lang="Urdu" code="ur">, 'vi': <Caption lang="Vietnamese" code="vi">}

Now let's checkout the english captions::

    >>> caption = yt.captions.get_by_language_code('en')

Great, now let's see how YouTube formats them::

    >>> caption.xml_captions
    '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="10.2" dur="0.94">K-pop!</text>...'

Oh, this isn't very easy to work with, let's convert them to the srt format::

    >>> print(caption.generate_srt_captions())
    1
    00:00:10,200 --> 00:00:11,140
    K-pop!

    2
    00:00:13,400 --> 00:00:16,200
    That is so awkward to watch.
    ...