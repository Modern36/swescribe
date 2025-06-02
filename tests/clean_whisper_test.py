from itertools import permutations

import pytest

from swescribe.clean_whisper import (
    clean_dashes,
    clean_elipsis,
    clean_for,
    clean_ja_repeat,
    clean_line_artefact,
    clean_spaces,
    clean_text,
    clean_urls,
    line_artefact_check,
)


class TestCleanDash:
    def test_empty(self):
        assert "" == clean_dashes("")

    def test_spaces(self):
        assert "" == clean_dashes("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_dashes(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_dashes(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_dashes(test_text)

    def test_end_dashes(self):
        test_text = "This is a text that has --"
        assert test_text == clean_urls(test_text)


class TestCleanURLs:
    def test_empty(self):
        assert "" == clean_urls("")

    def test_spaces(self):
        assert "" == clean_urls("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_urls(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_urls(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_urls(test_text)

    def test_URL(self):
        test_text = "This is a text that has a url"
        assert "" == clean_urls(test_text + " https://www.google.com")

    def test_punkt_nu(self):
        test_text = "This is a text that has a punkt-nu"
        assert "" == clean_urls(test_text + " url.nu")


class TestCleanElipsis:
    def test_empty(self):
        assert "" == clean_elipsis("")

    def test_spaces(self):
        assert "" == clean_elipsis("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_elipsis(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_elipsis(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_elipsis(test_text)

    def test_elipsis(self):
        test_text = "This is a text that has an"
        assert test_text == clean_elipsis(test_text + " ...")

    def test_four_dots(self):
        test_text = "This is a text that has an"
        assert test_text == clean_elipsis(test_text + " ....")


class TestCleanSpaces:
    def test_empty(self):
        assert "" == clean_spaces("")

    def test_spaces(self):
        assert "" == clean_spaces("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_spaces(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_spaces(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_spaces(test_text)

    def test_spaces_between_text(self):
        test_text = "This is a text that has an "
        assert (test_text * 2).strip() == clean_spaces(
            test_text + "       " + test_text
        )


class TestCleanFor:
    def test_empty(self):
        assert "" == clean_for("")

    def test_spaces(self):
        assert "" == clean_for("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_for(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_for(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_for(test_text)

    def test_one_instance(self):
        test_text = "This is a text that has an"
        assert test_text == clean_for(test_text + " För. ")

    def test_between_text(self):
        test_text = "This is a text that has an between"
        assert test_text + "  " + test_text == clean_for(
            test_text + " För." + test_text
        )

    def test_multiple_between_text(self):
        test_text = "This is a text that has an between"
        assert test_text + "  " * 5 + test_text == clean_for(
            test_text + " För." * 5 + test_text
        )

    def test_greed(self):
        test_text = "This is a text that has a relevant aFör."
        assert test_text == clean_for(test_text)


class TestCleanJa:
    def test_empty(self):
        assert "" == clean_ja_repeat("")

    def test_spaces(self):
        assert "" == clean_ja_repeat("  ")

    def test_None(self):
        with pytest.raises(TypeError):
            clean_ja_repeat(None)

    def test_integer(self):
        with pytest.raises(TypeError):
            clean_ja_repeat(9)

    def test_clean(self):
        test_text = "This is a text that does not need cleaning"
        assert test_text == clean_ja_repeat(test_text)

    def test_one_instance(self):
        test_text = "This is a text that has one ja,"
        assert test_text == clean_ja_repeat(test_text)

    def test_two_instance(self):
        test_text = "This is a text that has two ja, ja,"
        assert test_text == clean_ja_repeat(test_text)

    def test_one_too_many_instance(self):
        test_text = "This is a text that has one too many ja, ja,"
        assert test_text == clean_ja_repeat(test_text + " ja, ")

    def test_between_text(self):
        test_text = "This is a text that has an between"
        test_text += " ja, " + test_text
        assert test_text == clean_ja_repeat(test_text)

    def test_multiple_between_text(self):
        test_text = "This is a text that has an between"
        assert test_text + " ja, ja, " + test_text == clean_ja_repeat(
            test_text + " ja," * 5 + " " + test_text
        )

    def test_multiple(self):
        test_text = "This is a text that has many, many ja, ja,"
        assert test_text == clean_ja_repeat(test_text + " ja," * 100)

    def test_multiple_with_case_insensitivity(self):
        test_text = "This is a text that has many, many Ja, ja,"
        assert test_text == clean_ja_repeat(test_text + " ja, Ja," * 100)


@pytest.mark.xfail(strict=True, reason="Changing function output")
def test_line_artefact_check():
    # Test with line artefact
    artefact_text = "Textning.nu"
    assert line_artefact_check(artefact_text)

    # Test without line artefact
    normal_text = "Clean text here"
    assert not line_artefact_check(normal_text)


class TestOrder:
    tests = [
        clean_elipsis,
        clean_dashes,
        clean_for,
        clean_line_artefact,
        clean_ja_repeat,
        clean_urls,
    ]

    test_text = "".join(
        (
            "And a repetition of 'Ja, ' " + "Ja, ja, " * 100,
            "Some elipsis are good: " + " ..." + " ..." + " ..........",
            "And a repetition of 'Ja, ' " + "ja, Ja, " * 100,
        )
    )

    target_text = "".join(
        (
            "And a repetition of 'Ja, ' " + "Ja, ja, ",
            "Some elipsis are good: ",
            "And a repetition of 'Ja, ' " + "ja, Ja,",
        )
    )

    @pytest.mark.parametrize("tests", list(permutations(tests)))
    def test_order_independence(self, tests):
        result = self.test_text[:]
        for test in tests:
            result = test(result)
        result = clean_spaces(result)

        assert result == self.target_text

    @pytest.mark.xfail(
        strict=True, reason="Making sure that spaces needs to be last"
    )
    def test_order_dependence(self, tests):
        result = clean_spaces(self.test_text[:])
        for test in tests:
            result = test(result)

        assert result == self.target_text

    def test_cleaner(self):
        result = self.test_text[:]
        result = clean_text(result)
        assert result == self.target_text


class TestKnownErrors:
    @staticmethod
    def text_textning():
        assert "" == clean_text("Textning.nu")

    @staticmethod
    def test_svensktextning():
        assert "" == clean_text("Svensktextning.nu")

    @staticmethod
    def test_svansktextning():
        assert "" == clean_text("Svansktextning.nu")

    @staticmethod
    def test_undertexter_från_amara_org_gemenskapen():
        assert "" == clean_text("Undertexter från Amara.org-gemenskapen")

    @staticmethod
    def test_musik_():
        assert "" == clean_text("Musik.")

    @staticmethod
    def test_musik_with_elipsis():
        assert "" == clean_text("...Musik...")
        assert "" == clean_text("...musik...")

    @staticmethod
    def test_musik():
        assert "" == clean_text("Musik")

    @staticmethod
    def test_för_():
        assert "" == clean_text("För.")

    @staticmethod
    def test_men_():
        assert "" == clean_text("Men.")

    @staticmethod
    def test_den_():
        assert "" == clean_text("Den.")

    @staticmethod
    def test_jag_har_en_():
        assert "" == clean_text("Jag har en.")

    @staticmethod
    def test_musik_musik():
        assert "" == clean_text("Musik Musik")

    @staticmethod
    def test_musik_musik_musik():
        assert "" == clean_text("Musik Musik Musik")

    @staticmethod
    def test_textning_stina_hedin_www_btistudios_com():
        assert "" == clean_text("Textning Stina Hedin www.btistudios.com")

    @staticmethod
    def test_stina_hedin_iyuno_media_group():
        assert "" == clean_text("Stina Hedin Iyuno Media Group")

    @staticmethod
    def test_textat_av_karin_schill_():
        assert "" == clean_text("Textat av Karin Schill.")
