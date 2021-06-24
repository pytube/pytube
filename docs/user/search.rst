.. _search:

Using the search feature
========================

Pytube includes functionality to search YouTube and return results almost
identical to those you would find using the search bar on YouTube's website.
The integration into pytube means that we can directly provide you with
YouTube objects that can be inspected and dowloaded, instead of needing to do
additional processing.

Using the Search object is really easy::

    >>> from pytube import Search
    >>> s = Search('YouTube Rewind')
    >>> len(s.results)
    17
    >>> s.results
    [\
        <pytube.__main__.YouTube object: videoId=YbJOTdZBX1g>, \
        <pytube.__main__.YouTube object: videoId=PKtnafFtfEo>, \
        ...\
    ]
    >>> 

Due to the potential for an endless stream of results, and in order to prevent
a user from accidentally entering an infinite loop of requesting additional
results, the ``.results`` attribute will only ever request the first set of
search results. Additional results can be explicitly requested by using the
``.get_next_results()`` method, which will append any additional results to
the ``.results`` attribute::

    >>> s.get_next_results()
    >>> len(s.results)
    34
    >>> 

Additional functionality
========================

In addition to the basic search functionality which returns YouTube objects,
searches also have associated autocomplete suggestions. These can be accessed
as follows::

    >>> s.completion_suggestions
    [\
        'can this video get 1 million dislikes', \
        'youtube rewind 2020 musical', \
        ...\
    ]
