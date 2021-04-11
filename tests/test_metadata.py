"""Unit tests for the :module:`metadata <metadata>` module."""
from pytube import extract


def test_extract_metadata_empty():
    ytmd = extract.metadata({})
    assert ytmd._raw_metadata == []


def test_metadata_from_initial_data(stream_dict):
    initial_data = extract.initial_data(stream_dict)
    ytmd = extract.metadata(initial_data)
    assert len(ytmd.raw_metadata) > 0
    assert 'contents' in ytmd.raw_metadata[0]
    assert len(ytmd.metadata) > 0
    assert 'Song' in ytmd.metadata[0]
