"""Unit tests for the matching algorithms in fuzzy_matcher.infrastructure.algorithms."""

import pytest

from fuzzy_matcher.infrastructure.algorithms import (
    DamerauLevenshteinAlgorithm,
    JaroWinklerAlgorithm,
    LevenshteinAlgorithm,
    MetaphoneEncoder,
    PartialRatioAlgorithm,
    SoundexEncoder,
    TokenSetRatioAlgorithm,
    TokenSortRatioAlgorithm,
    WeightedRatioAlgorithm,
    get_default_phonetic_encoders,
    get_default_similarity_algorithms,
)


class TestSimilarityAlgorithms:
    """Tests for the similarity algorithm implementations."""

    @pytest.mark.parametrize(
        "algo_class,name",
        [
            (LevenshteinAlgorithm, "levenshtein"),
            (DamerauLevenshteinAlgorithm, "damerau_levenshtein"),
            (JaroWinklerAlgorithm, "jaro_winkler"),
            (TokenSetRatioAlgorithm, "token_set_ratio"),
            (TokenSortRatioAlgorithm, "token_sort_ratio"),
            (PartialRatioAlgorithm, "partial_ratio"),
            (WeightedRatioAlgorithm, "weighted_ratio"),
        ],
    )
    def test_algorithm_name(self, algo_class, name):
        """Test that each algorithm returns the correct name."""
        algo = algo_class()
        assert algo.name == name

    @pytest.mark.parametrize(
        "algo_class,s1,s2,expected",
        [
            # Levenshtein distance tests
            (LevenshteinAlgorithm, "kitten", "sitting", 0.5714285714285714),
            (LevenshteinAlgorithm, "same", "same", 1.0),
            (LevenshteinAlgorithm, "", "", 1.0),
            (LevenshteinAlgorithm, "test", "", 0.0),
            (LevenshteinAlgorithm, "", "test", 0.0),
            # Damerau-Levenshtein tests (better for transpositions)
            (DamerauLevenshteinAlgorithm, "abc", "acb", 0.6666666666666667),  # transposition
            (DamerauLevenshteinAlgorithm, "same", "same", 1.0),
            # Jaro-Winkler tests (weighted towards beginning matches)
            (
                JaroWinklerAlgorithm,
                "Martha",
                "Marhta",
                0.9611111111111111,
            ),  # transposition - high score
            (
                JaroWinklerAlgorithm,
                "CRATE",
                "TRACE",
                0.7333333333333334,
            ),  # same chars, different order
            # Token tests
            (TokenSetRatioAlgorithm, "fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear", 1.0),
            (TokenSortRatioAlgorithm, "fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear", 1.0),
            (
                PartialRatioAlgorithm,
                "The quick brown fox jumps over the lazy dog",
                "brown fox",
                1.0,
            ),
            (
                WeightedRatioAlgorithm,
                "The quick brown fox jumps over the lazy dog",
                "The brown fox",
                0.85,
            ),
        ],
    )
    def test_calculate_similarity(self, algo_class, s1, s2, expected):
        """Test that similarity calculation returns expected results for specific cases."""
        algo = algo_class()
        assert algo.calculate_similarity(s1, s2) == pytest.approx(expected, abs=1e-10)

    def test_edge_cases(self):
        """Test edge cases for all algorithms."""
        algorithms = [
            LevenshteinAlgorithm(),
            DamerauLevenshteinAlgorithm(),
            JaroWinklerAlgorithm(),
            TokenSetRatioAlgorithm(),
            TokenSortRatioAlgorithm(),
            PartialRatioAlgorithm(),
            WeightedRatioAlgorithm(),
        ]

        # Test empty strings
        for algo in algorithms:
            assert algo.calculate_similarity("", "") == 1.0
            assert algo.calculate_similarity("test", "") == 0.0
            assert algo.calculate_similarity("", "test") == 0.0

        # Test identical strings
        for algo in algorithms:
            assert algo.calculate_similarity("same", "same") == 1.0

    def test_similarity_direction(self):
        """Test that similarity is symmetric (a,b) == (b,a)."""
        algorithms = [
            LevenshteinAlgorithm(),
            DamerauLevenshteinAlgorithm(),
            JaroWinklerAlgorithm(),
            TokenSetRatioAlgorithm(),
            TokenSortRatioAlgorithm(),
            PartialRatioAlgorithm(),
            WeightedRatioAlgorithm(),
        ]

        test_pairs = [
            ("kitten", "sitting"),
            ("apple", "appel"),
            ("New York", "york new"),
            ("ABC Corporation", "Corporation ABC"),
        ]

        for algo in algorithms:
            for s1, s2 in test_pairs:
                assert algo.calculate_similarity(s1, s2) == algo.calculate_similarity(s2, s1)


class TestPhoneticEncoders:
    """Tests for the phonetic encoder implementations."""

    @pytest.mark.parametrize(
        "encoder_class,name",
        [
            (SoundexEncoder, "soundex"),
            (MetaphoneEncoder, "metaphone"),
        ],
    )
    def test_encoder_name(self, encoder_class, name):
        """Test that each encoder returns the correct name."""
        encoder = encoder_class()
        assert encoder.name == name

    @pytest.mark.parametrize(
        "input_str,expected_soundex",
        [
            ("Robert", "R163"),
            ("Rupert", "R163"),
            ("Rubin", "R150"),
            ("Ashcraft", "A261"),
            ("Ashcroft", "A261"),
            ("Tymczak", "T522"),
            ("Pfister", "P236"),
            ("", ""),
        ],
    )
    def test_soundex_encoder(self, input_str, expected_soundex):
        """Test that Soundex encoder returns expected encodings."""
        encoder = SoundexEncoder()
        assert encoder.encode(input_str) == expected_soundex

    @pytest.mark.parametrize(
        "input_str,expected_metaphone",
        [
            ("Smith", "SM0"),
            ("Schmidt", "XMT"),
            ("Johnson", "JNSN"),
            ("Williams", "WLMS"),
            ("Jones", "JNS"),
            ("Brown", "BRN"),
            ("", ""),
        ],
    )
    def test_metaphone_encoder(self, input_str, expected_metaphone):
        """Test that Metaphone encoder returns expected encodings."""
        encoder = MetaphoneEncoder()
        assert encoder.encode(input_str) == expected_metaphone

    def test_phonetic_similarity(self):
        """Test that phonetically similar words have the same encoding."""
        soundex = SoundexEncoder()
        metaphone = MetaphoneEncoder()

        # Soundex test pairs (should have same encoding)
        soundex_pairs = [
            ("Robert", "Rupert"),
            ("Ashcraft", "Ashcroft"),
            ("Smith", "Smyth"),
            ("Catherine", "Katherine"),
        ]

        for s1, s2 in soundex_pairs:
            assert soundex.encode(s1) == soundex.encode(s2)

        # Test metaphone directly for a single pair
        assert metaphone.encode("Smith") == metaphone.encode("Smyth")
        assert metaphone.encode("phone") == metaphone.encode("fone")
        assert metaphone.encode("Knight") == metaphone.encode("Night")


class TestFactoryFunctions:
    """Tests for the algorithm and encoder factory functions."""

    def test_get_default_similarity_algorithms(self):
        """Test that get_default_similarity_algorithms returns all expected algorithms."""
        algorithms = get_default_similarity_algorithms()

        expected_names = {
            "levenshtein",
            "damerau_levenshtein",
            "jaro_winkler",
            "token_set_ratio",
            "token_sort_ratio",
            "partial_ratio",
            "weighted_ratio",
        }

        assert set(algorithms.keys()) == expected_names

        # Check types
        for name, algo in algorithms.items():
            assert algo.name == name

    def test_get_default_phonetic_encoders(self):
        """Test that get_default_phonetic_encoders returns all expected encoders."""
        encoders = get_default_phonetic_encoders()

        expected_names = {"soundex", "metaphone"}

        assert set(encoders.keys()) == expected_names

        # Check types
        for name, encoder in encoders.items():
            assert encoder.name == name
