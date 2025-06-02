import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Mock the transcribe module to prevent importing torch
sys.modules["swescribe.transcribe"] = Mock()

sys.modules["swescribe.transcribe"].transcription_result = Mock()

sys.modules["swescribe.transcribe"].align_results = Mock(
    return_value={
        "segments": [
            {"start": 1.0, "end": 2.0, "text": "--Hello World"},
            {"start": 3.0, "end": 4.0, "text": "Ja, Ja, Ja, Ja,"},
            {"start": 5.0, "end": 6.0, "text": "Textning.nu"},
            {"start": 7.0, "end": 8.0, "text": "Musik."},
            {"start": 9.0, "end": 10.0, "text": "Clean text here"},
        ]
    }
)


from swescribe.__main__ import cli, pipeline


@patch("swescribe.__main__.wavpath_to_srt", return_value="Mocked SRT content")
def test_pipeline(mock_wavpath_to_srt, tmpdir):
    input_path = Path(tmpdir) / "test_audio.wav"
    output_path = Path(tmpdir) / "test_output.srt"

    pipeline(input_path, output_path)

    assert output_path.read_text() == "Mocked SRT content"
    mock_wavpath_to_srt.assert_called_once_with(input_path)


@patch("swescribe.__main__.pipeline")
def test_cli(mock_pipeline, tmpdir: Path):
    test_audio = Path(tmpdir) / "test_audio.wav"
    test_audio.touch()

    # Test with valid input file
    test_args = ["-i", str(test_audio), "-o", "test_output.srt"]
    cli(test_args)

    mock_pipeline.assert_called_once_with(test_audio, Path("test_output.srt"))


@patch("swescribe.__main__.pipeline")
def test_cli_fake_input(mock_pipeline, tmpdir):
    fake_input = tmpdir / "test_output"

    test_args = ["-i", str(fake_input), "-o", "a"]
    with pytest.raises(
        FileNotFoundError, match="Input file does not exist: .+"
    ):
        cli(test_args)


@patch("swescribe.__main__.pipeline")
def test_cli_file_to_none(mock_pipeline, tmpdir):
    fake_input = tmpdir / "test_output"

    test_args = ["-i", str(fake_input)]
    with pytest.raises(
        FileNotFoundError, match="Input file does not exist: .+"
    ):
        cli(test_args)


@patch("swescribe.__main__.pipeline")
def test_cli_file_to_fix_srt(mock_pipeline, tmpdir):
    fake_input = Path(tmpdir) / "test_.wav"

    fake_input.touch()

    test_args = ["-i", str(fake_input)]
    cli(test_args)

    mock_pipeline.assert_called_once_with(
        fake_input, fake_input.with_suffix(".srt")
    )


@patch("swescribe.__main__.pipeline")
def test_cli_flie_to_file(mock_pipeline, tmpdir: Path):
    test_audio = Path(tmpdir)

    out_file = Path(tmpdir) / "test.srt"

    # Test with valid input file
    test_args = [
        "-i",
        str(test_audio),
        "-o",
        str(out_file),
    ]
    with pytest.raises(
        ValueError, match="Output file is a file, but input is a directory."
    ):
        cli(test_args)


@patch("swescribe.__main__.pipeline")
def test_cli_dir_with_files_to_dir(mock_pipeline, tmpdir: Path, capsys):
    test_audio = Path(tmpdir)

    audio1 = test_audio / "audio1.wav"
    audio1.touch()

    audio2 = test_audio / "audio2.mpg"
    audio2.touch()
    out2 = audio2.with_suffix(".srt")

    # Test with valid input file
    test_args = [
        "-i",
        str(test_audio),
    ]
    cli(test_args)

    assert capsys.readouterr().out.startswith("Converting 2 audios in ")

    mock_pipeline.assert_called_with(audio2, out2, force=False)


@patch("swescribe.__main__.pipeline")
def test_cli_dir_with_files_to_dir_force(mock_pipeline, tmpdir: Path, capsys):
    test_audio = Path(tmpdir)

    audio1 = test_audio / "audio1.wav"
    audio1.touch()

    audio2 = test_audio / "audio2.mpg"
    audio2.touch()
    out2 = audio2.with_suffix(".srt")

    # Test with valid input file
    test_args = [
        "-i",
        str(test_audio),
        "-f",
    ]
    cli(test_args)

    assert capsys.readouterr().out.startswith("Converting 2 audios in ")

    mock_pipeline.assert_called_with(audio2, out2, force=True)


@patch("swescribe.__main__.pipeline")
def test_cli_file_non_wav_extension(mock_pipeline, tmpdir):
    # Test with a file that has a non-wav extension
    fake_input = Path(tmpdir) / "test_audio.mp4"
    fake_input.touch()

    output = Path(tmpdir / "test_output.srt")

    test_args = ["-i", str(fake_input), "-o", str(output)]
    cli(test_args)

    mock_pipeline.assert_called_once_with(fake_input, output)


@patch("swescribe.__main__.pipeline")
def test_cli_directory_input_with_existing_file(mock_pipeline, tmpdir):
    # Test with a directory as input and files inside it
    dir_path = Path(tmpdir) / "test_dir"
    dir_path.mkdir()

    audio1 = dir_path / "audio1.mpg"
    audio1.touch()
    out1 = dir_path / audio1.with_suffix(".srt")

    test_args = ["-i", str(dir_path)]
    cli(test_args)

    mock_pipeline.assert_called_once_with(audio1, out1, force=False)


@patch("swescribe.__main__.pipeline")
def test_cli_directory_input_with_existing_file_forced(mock_pipeline, tmpdir):
    # Test with a directory as input and files inside it
    dir_path = Path(tmpdir) / "test_dir"
    dir_path.mkdir()

    audio1 = dir_path / "audio1.mpg"
    audio1.touch()
    out1 = dir_path / audio1.with_suffix(".srt")

    test_args = ["-i", str(dir_path), "-f"]
    cli(test_args)

    mock_pipeline.assert_called_once_with(audio1, out1, force=True)


@patch("swescribe.__main__.extract_audio")
def test_cli_extracts_audio(mock_extract_audio, tmpdir):
    # Test with a directory as input and files inside it
    dir_path = Path(tmpdir) / "test_dir"
    dir_path.mkdir()

    video = dir_path / "video1.mpg"
    video.touch()

    out1 = dir_path / video.with_suffix(".srt")

    test_args = ["-i", str(dir_path)]
    cli(test_args)

    mock_extract_audio.assert_called_once()

    assert out1.exists()


@patch("swescribe.__main__.extract_audio")
def test_cli_remove_hyphen(mock_extract_audio, tmpdir):
    # Test with a directory as input and files inside it
    dir_path = Path(tmpdir) / "test_dir"
    dir_path.mkdir()

    video = dir_path / "video1.mpg"
    video.touch()

    out1 = dir_path / video.with_suffix(".srt")

    test_args = ["-i", str(dir_path)]
    cli(test_args)

    assert out1.exists()


# Clean up the mocked module after tests
def teardown_module(module):
    del sys.modules["swescribe.transcribe"]


class TestForce:
    @staticmethod
    @patch("swescribe.__main__.pipeline")
    def test_cli_dir_with_files_to_not_overwrite(
        mock_pipeline, tmpdir: Path, capsys
    ):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()
        out1 = audio1.with_suffix(".srt")
        out1.touch()

        audio2 = test_audio / "audio2.mpg"
        audio2.touch()
        out2 = audio2.with_suffix(".srt")

        # Test with valid input file
        test_args = [
            "-i",
            str(test_audio),
        ]
        cli(test_args)

        assert capsys.readouterr().out.startswith("Converting 1 audios in ")

        mock_pipeline.assert_called_with(audio2, out2, force=False)

    @staticmethod
    @patch("swescribe.__main__.pipeline")
    def test_cli_dir_with_files_to_overwrite(
        mock_pipeline, tmpdir: Path, capsys
    ):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()
        out1 = audio1.with_suffix(".srt")
        out1.touch()

        audio2 = test_audio / "audio2.mpg"
        audio2.touch()
        out2 = audio2.with_suffix(".srt")
        out2.touch()

        # Test with valid input file
        test_args = [
            "-i",
            str(test_audio),
            "-f",
        ]
        cli(test_args)

        assert capsys.readouterr().out.startswith("Converting 2 audios in ")

        mock_pipeline.assert_called_with(audio2, out2, force=True)


class TestDuplicateFilenames:
    @staticmethod
    def test_cli_dir_with_duplicate_names(tmpdir: Path, capsys):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()

        audio2 = test_audio / "audio1.mpg"
        audio2.touch()

        test_args = [
            "-i",
            str(test_audio),
        ]
        with pytest.raises(
            FileExistsError, match="Files with same output.srt detected: "
        ):
            cli(test_args)

    @staticmethod
    def test_cli_dir_with_duplicate_names_force(tmpdir: Path, capsys):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()

        audio2 = test_audio / "audio1.mpg"
        audio2.touch()

        test_args = [
            "-i",
            str(test_audio),
            "-f",
        ]
        with pytest.raises(
            FileExistsError, match="Files with same output.srt detected: "
        ):
            cli(test_args)

    @staticmethod
    def test_cli_dir_with_duplicate_names_andoutput_force(
        tmpdir: Path, capsys
    ):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()

        audio2 = test_audio / "audio1.mpg"
        audio2.touch()

        output = audio1.with_suffix(".srt")
        output.touch()

        test_args = [
            "-i",
            str(test_audio),
            "-f",
        ]
        with pytest.raises(
            FileExistsError, match="Files with same output.srt detected: "
        ):
            cli(test_args)

    @staticmethod
    def test_cli_dir_with_files_to_overwrite(tmpdir: Path, capsys):
        test_audio = Path(tmpdir)

        audio1 = test_audio / "audio1.wav"
        audio1.touch()
        out1 = audio1.with_suffix(".srt")
        out1.touch()

        audio2 = test_audio / "audio1.mpg"
        audio2.touch()

        test_args = [
            "-i",
            str(test_audio),
        ]
        cli(test_args)

        assert capsys.readouterr().out.startswith("Converting 0 audios in ")
