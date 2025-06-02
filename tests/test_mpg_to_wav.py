import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from swescribe.mpg_to_wav import extract_audio


def test_extract_audio(tmp_path: Path):
    mpg_file_path = tmp_path / "test.mpg"
    wav_file_path = tmp_path / "output.wav"

    # Create an empty mpg file for the sake of existence (though it won't be used)
    mpg_file_path.touch()

    expected_command = [
        "ffmpeg",
        "-y",  # Overwrite output files without asking
        "-i",
        str(mpg_file_path),  # Input file
        "-ar",
        "16000",  # Set audio sample rate to 16kHz
        "-ac",
        "1",  # Set audio channels to mono
        str(wav_file_path),
    ]

    with patch("subprocess.run") as mock_run:
        extract_audio(mpg_file_path, wav_file_path)

        # Verify that subprocess.run was called once with the correct command
        mock_run.assert_called_once_with(
            expected_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def test_extract_audio_from_missing_mpg_file(tmp_path: Path):
    mpg_file_path = tmp_path / "test.mpg"
    wav_file_path = tmp_path / "output.wav"

    with pytest.raises(FileNotFoundError, match="The file .+ does not exist."):
        extract_audio(mpg_file_path, wav_file_path)


def test_extract_audio_to_missing_output_dir(tmp_path: Path):
    mpg_file_path = tmp_path / "test.mpg"
    wav_file_path = tmp_path / "output_dir" / "output.wav"

    mpg_file_path.touch()

    with pytest.raises(
        FileNotFoundError, match="The ouput directory .+ does not exist."
    ):
        extract_audio(mpg_file_path, wav_file_path)
