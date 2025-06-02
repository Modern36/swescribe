import logging

import pytest

from swescribe.alignment_to_srt import alignment_to_srt, format_timestamp

# Set up logging to capture debug logs during tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="function")
def aligned_result():
    return {
        "segments": [
            {"start": 1.0, "end": 2.0, "text": "--Hello World"},
            {"start": 3.0, "end": 4.0, "text": "Ja, Ja, Ja, Ja,"},
            {"start": 5.0, "end": 6.0, "text": "Textning.nu"},
            {"start": 7.0, "end": 8.0, "text": "Musik."},
            {"start": 9.0, "end": 10.0, "text": "Clean text here"},
        ]
    }


def test_alignment_to_srt(aligned_result):
    expected_output = (
        "1\n00:00:01,000 --> 00:00:02,000\nHello World\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nJa, Ja,\n\n"
        "3\n00:00:09,000 --> 00:00:10,000\nClean text here\n\n"
    )
    assert alignment_to_srt(aligned_result) == expected_output


def test_format_timestamp():
    assert format_timestamp(123.456) == "00:02:03,456"


def test_skipping_empty_segments():
    aligned_result_with_empty = {
        "segments": [
            {"start": 3.0, "end": 4.0, "text": ""},
            {"start": 5.0, "end": 6.0, "text": "Clean text here"},
        ]
    }
    expected_output = "1\n00:00:05,000 --> 00:00:06,000\nClean text here\n\n"
    assert alignment_to_srt(aligned_result_with_empty) == expected_output


def test_skipping_artefact_segments():
    aligned_result_with_artefacts = {
        "segments": [
            {"start": 3.0, "end": 4.0, "text": "Textning.nu"},
            {"start": 5.0, "end": 6.0, "text": "Musik."},
        ]
    }
    expected_output = ""
    assert alignment_to_srt(aligned_result_with_artefacts) == expected_output
