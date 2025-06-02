from pathlib import Path

import pytest

from swescribe import srt_to_txt


def test_convert_srt_to_txt(tmpdir: Path):
    num_test_cases = 1

    # Write a sample SRT file to the input directory
    srt_content = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
This is a test
"""

    input_file_path = tmpdir / "test.srt"
    with open(input_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # Call the conversion function
    srt_to_txt.num_test_cases = num_test_cases
    srt_to_txt.convert_srt_to_txt(str(tmpdir), str(tmpdir))

    # Verify that the output file is created and has the correct content
    expected_content = "Hello world\n\nThis is a test\n"
    output_file_path = tmpdir / "test.txt"

    with open(output_file_path, "r", encoding="utf-8") as f:
        assert f.read() == expected_content


def test_convert_srt_to_txt_multiple_files(tmpdir: Path):
    num_test_cases = 2

    # Create temporary directories using pytest's tmpdir fixture and convert to Path
    input_dir = Path(tmpdir.mkdir("input"))
    output_dir = Path(tmpdir.mkdir("output"))

    # Write sample SRT files to the input directory
    srt_content_1 = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
This is a test
"""

    srt_content_2 = """1
00:00:05,000 --> 00:00:06,000
Another line

2
00:00:07,000 --> 00:00:08,000
Yet another test
"""

    input_file_path_1 = input_dir / "test1.srt"
    with open(input_file_path_1, "w", encoding="utf-8") as f:
        f.write(srt_content_1)

    input_file_path_2 = input_dir / "test2.srt"
    with open(input_file_path_2, "w", encoding="utf-8") as f:
        f.write(srt_content_2)

    # Call the conversion function
    srt_to_txt.num_test_cases = num_test_cases
    srt_to_txt.convert_srt_to_txt(str(input_dir), str(output_dir))

    # Verify that the output files are created and have the correct content
    expected_content_1 = "Hello world\n\nThis is a test\n"
    expected_content_2 = "Another line\n\nYet another test\n"

    output_file_path_1 = output_dir / "test1.txt"
    with open(output_file_path_1, "r", encoding="utf-8") as f:
        assert f.read() == expected_content_1

    output_file_path_2 = output_dir / "test2.txt"
    with open(output_file_path_2, "r", encoding="utf-8") as f:
        assert f.read() == expected_content_2


def test_convert_srt_to_txt_no_files(tmpdir: Path):
    # Define the number of test cases (SRT files)
    num_test_cases = 1

    # Create temporary directories using pytest's tmpdir fixture and convert to Path
    input_dir = Path(tmpdir.mkdir("input"))
    output_dir = Path(tmpdir.mkdir("output"))

    # Call the conversion function and expect a ValueError
    with pytest.raises(ValueError, match="Expected 1 SRT files, found 0"):
        srt_to_txt.num_test_cases = num_test_cases
        srt_to_txt.convert_srt_to_txt(str(input_dir), str(output_dir))


def test_convert_srt_to_txt_mismatched_files(tmpdir: Path):
    # Define the number of test cases (SRT files)
    num_test_cases = 1

    # Create temporary directories using pytest's tmpdir fixture and convert to Path
    input_dir = Path(tmpdir.mkdir("input"))
    output_dir = Path(tmpdir.mkdir("output"))

    # Write sample SRT files to the input directory
    srt_content_1 = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
This is a test
"""

    input_file_path_1 = input_dir / "test1.srt"
    with open(input_file_path_1, "w", encoding="utf-8") as f:
        f.write(srt_content_1)

    # Call the conversion function and expect a ValueError
    with pytest.raises(ValueError, match="Expected 2 SRT files, found 1"):
        srt_to_txt.num_test_cases = num_test_cases + 1
        srt_to_txt.convert_srt_to_txt(str(input_dir), str(output_dir))


def test_convert_srt_to_txt_cleaner_files(tmpdir: Path):
    # Define the number of test cases (SRT files)
    num_test_cases = 1

    # Create temporary directories using pytest's tmpdir fixture and convert to Path
    input_dir = Path(tmpdir.mkdir("input"))
    output_dir = Path(tmpdir.mkdir("output"))

    # Write sample SRT files to the input directory
    srt_content = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
This is a test
"""

    input_file_path = input_dir / "noisy_file.srt"
    with open(input_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # Call the conversion function
    srt_to_txt.num_test_cases = num_test_cases

    srt_to_txt.NOISY_SEGMENTS = {
        "noisy_file": [("00:00:01,000", "00:00:02,000")]
    }

    srt_to_txt.convert_srt_to_txt(input_dir, output_dir)

    # Verify that the output file is created and has the correct content
    expected_content = "This is a test\n"
    output_file_path = output_dir / "noisy_file.txt"

    with open(output_file_path, "r", encoding="utf-8") as f:
        assert f.read() == expected_content
