from pathlib import Path

import pandas as pd
import pytest

from swescribe import wer


def test_read_normal_transcript(tmp_path: Path):
    # Create a temporary file with some text
    transcript_path = tmp_path / "transcript.txt"
    transcript_path.write_text("Hello world! This is a test.")

    result = wer.read_transcript(transcript_path)
    assert result == "Hello world! This is a test."


def test_read_empty_file(tmp_path: Path):
    # Create an empty file
    transcript_path = tmp_path / "empty_transcript.txt"
    transcript_path.write_text("")

    with pytest.raises(
        ValueError, match="Error: The file .+ contains no text."
    ):
        wer.read_transcript(transcript_path)


def test_read_file_with_only_xzy(tmp_path: Path):
    # Create a file containing only "xzy"
    transcript_path = tmp_path / "only_xzy.txt"
    transcript_path.write_text("xzy")

    with pytest.raises(
        ValueError, match="Error: The file .+ contains no text."
    ):
        wer.read_transcript(transcript_path)


def test_read_file_with_multiple_lines_and_spaces(tmp_path: Path):
    # Create a file with multiple lines and spaces
    transcript_path = tmp_path / "multiline_transcript.txt"
    transcript_path.write_text("xzyHello world! \nxzyThis is a test.xzy")

    result = wer.read_transcript(transcript_path)
    assert result == "Hello world! \n This is a test."


@pytest.fixture
def setup_test_data(tmpdir):
    test_dir = Path(tmpdir.mkdir("test"))
    transcription_dir = test_dir / "transcriptions"
    ground_truth_dir = test_dir / "ground_truth"
    output_csv_file = test_dir / "wer_results.csv"

    transcription_dir.mkdir()
    ground_truth_dir.mkdir()

    # Creating mock files with known contents
    test_cases = [
        ("Transcribed text 1", "Ground truth text 1"),
        ("This is a test.", "This is a test."),
        ("Hello world!", "Hallo world!"),
        ("Correct transcription", "Incorrect transcription"),
        ("Short", "Longer text"),
    ]

    for i, (transcription, ground_truth) in enumerate(test_cases):
        with open(transcription_dir / f"file_{i}.txt", "w") as f:
            f.write(transcription)
        with open(ground_truth_dir / f"file_{i}.txt", "w") as f:
            f.write(ground_truth)

    return transcription_dir, ground_truth_dir, output_csv_file


def test_perform_wer_analysis(setup_test_data):
    wer.num_test_cases = 5

    # Unpack the fixture values
    transcription_dir, ground_truth_dir, output_csv_file = setup_test_data

    wer.perform_wer_analysis(
        transcription_dir, ground_truth_dir, output_csv_file
    )

    # Check if the output CSV file was created and contains the correct data
    assert output_csv_file.exists()

    df = pd.read_csv(output_csv_file)
    expected_filenames = [f"file_{i}" for i in range(5)]
    expected_wer_scores = [
        0.500001,  # "Transcribed text 1" vs "Ground truth text 1"
        0.0,  # "This is a test." vs "This is a test."
        0.5,  # "Hello world!" vs "Hallo world!"
        0.499991,  # "Correct transcription" vs "Incorrect transcription"
        1.0,  # "Short" vs "Longer text"
    ]

    assert list(df["filename"]) == expected_filenames
    for expected, actual in zip(expected_wer_scores, df["WER"]):
        assert abs(expected - actual) < 1e-4


def test_file_in_missing_dir(tmpdir):
    transcription = tmpdir / "trans"
    ground_truth = tmpdir / "groundtruth"
    output = tmpdir / "nope" / "output.csv"
    with pytest.raises(
        FileNotFoundError,
        match="Parent directory of summary file does not exist: .+",
    ):
        wer.perform_wer_analysis(
            transcription_dir=transcription,
            ground_truth_dir=ground_truth,
            output_csv_file=output,
            summary_file=Path(tmpdir) / "nope" / "output.csv",
        )


def test_incorrect_file_count(tmpdir):
    tst_dir = Path(tmpdir)

    transcription = tst_dir / "trans"
    ground_truth = tst_dir / "groundtruth"
    output = tst_dir / "nope" / "output.csv"
    with pytest.raises(
        ValueError,
        match=(
            r"Expected \d+ input files in each directory found: .+(0).+(0).+"
        ),
    ):
        wer.perform_wer_analysis(
            transcription_dir=transcription,
            ground_truth_dir=ground_truth,
            output_csv_file=output,
        )


def test_empty_wer_results(tmpdir):
    tst_dir = Path(tmpdir)

    wer.num_test_cases = 0

    transcription = tst_dir
    ground_truth = tst_dir
    output = tst_dir
    with pytest.raises(
        ValueError,
        match=("Error: No valid WER results to write. Exiting."),
    ):
        wer.perform_wer_analysis(
            transcription_dir=transcription,
            ground_truth_dir=ground_truth,
            output_csv_file=output,
        )


def test_calculate_wer_different_names():
    with pytest.raises(ValueError, match="Expected .+ to equal .+"):
        wer.calculate_wer(Path("test1"), Path("test2"))


def test_incorrext_data_len(tmpdir):
    csv_path = Path(tmpdir) / "wer_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("transcription,ground_truth,wer\n")
    wer.num_test_cases = 3

    with pytest.raises(ValueError, match="Expected .+ rows found .+"):
        wer.summarize_wer(csv_path, "a")
