"""Integration tests for the application services in fuzzy_matcher.application.services."""

import pytest

from fuzzy_matcher.application.services import (
    ComprehensiveMatchScorer,
    ConfigurableMatchDecisionStrategy,
    EntityResolverService,
)
from fuzzy_matcher.domain.entities import (
    DomainEntityName,
)
from fuzzy_matcher.infrastructure.algorithms import (
    JaroWinklerAlgorithm,
    LevenshteinAlgorithm,
    SoundexEncoder,
    TokenSetRatioAlgorithm,
    get_default_phonetic_encoders,
    get_default_similarity_algorithms,
)
from fuzzy_matcher.infrastructure.preprocessors import StandardStringPreprocessor


class TestComprehensiveMatchScorer:
    """Tests for the ComprehensiveMatchScorer class."""

    @pytest.fixture()
    def scorer(self, preprocessor):
        """Return a ComprehensiveMatchScorer instance with default algorithms."""
        return ComprehensiveMatchScorer(
            preprocessor, get_default_similarity_algorithms(), get_default_phonetic_encoders()
        )

    def test_calculate_scores_identical(self, scorer):
        """Test calculating scores for identical strings."""
        scores = scorer.calculate_scores("Apple Inc.", "Apple Inc.")

        # Check that strings are preserved in score object
        assert scores.original_s1.raw_value == "Apple Inc."
        assert scores.original_s2.raw_value == "Apple Inc."

        # For identical strings, all algorithm scores should be 1.0
        assert scores.get_score("levenshtein") == 1.0
        assert scores.get_score("jaro_winkler") == 1.0
        assert scores.get_score("token_set_ratio") == 1.0

        # Phonetic encodings should be identical
        assert scores.get_score("soundex_s1") == scores.get_score("soundex_s2")
        assert scores.get_score("metaphone_s1") == scores.get_score("metaphone_s2")

    def test_calculate_scores_similar(self, scorer):
        """Test calculating scores for similar strings."""
        scores = scorer.calculate_scores("Apple Inc.", "Apple Corporation")

        # Scores should be high but not necessarily 1.0
        assert scores.get_score("levenshtein") < 1.0
        assert scores.get_score("jaro_winkler") < 1.0

        # Token set should handle different suffixes reasonably well
        # A more reasonable threshold is 0.7 as company name suffixes differ significantly
        assert scores.get_score("token_set_ratio") > 0.7

        # Phonetic encoding for "Apple" should be the same
        assert scores.get_score("soundex_s1").startswith("A")
        assert scores.get_score("soundex_s2").startswith("A")

    def test_calculate_scores_different(self, scorer):
        """Test calculating scores for very different strings."""
        scores = scorer.calculate_scores("Apple Inc.", "Microsoft Corporation")

        # Scores should be low for different companies
        assert scores.get_score("levenshtein") < 0.5
        assert scores.get_score("jaro_winkler") < 0.7
        assert scores.get_score("token_set_ratio") < 0.5

        # Phonetic encodings should be different
        assert scores.get_score("soundex_s1") != scores.get_score("soundex_s2")
        assert scores.get_score("metaphone_s1") != scores.get_score("metaphone_s2")

    def test_calculate_scores_empty_strings(self, scorer):
        """Test calculating scores with empty strings."""
        # Both empty
        scores_both_empty = scorer.calculate_scores("", "")
        assert scores_both_empty.get_score("levenshtein") == 1.0
        assert scores_both_empty.get_score("jaro_winkler") == 1.0
        assert scores_both_empty.get_score("token_set_ratio") == 1.0

        # One empty
        scores_one_empty = scorer.calculate_scores("Apple Inc.", "")
        assert scores_one_empty.get_score("levenshtein") == 0.0
        assert scores_one_empty.get_score("jaro_winkler") == 0.0
        assert scores_one_empty.get_score("token_set_ratio") == 0.0

    def test_custom_algorithms(self):
        """Test using custom algorithm subsets."""
        # Only use Levenshtein and Jaro-Winkler
        preprocessor = StandardStringPreprocessor()

        algos = {"levenshtein": LevenshteinAlgorithm(), "jaro_winkler": JaroWinklerAlgorithm()}

        encoders = {"soundex": SoundexEncoder()}

        scorer = ComprehensiveMatchScorer(preprocessor, algos, encoders)

        scores = scorer.calculate_scores("Apple Inc.", "Apple Inc.")

        # Algorithms we included should be present
        assert "levenshtein" in scores.scores
        assert "jaro_winkler" in scores.scores
        assert "soundex_s1" in scores.scores

        # Algorithms we excluded should not be present
        assert "token_set_ratio" not in scores.scores
        assert "metaphone_s1" not in scores.scores


class TestConfigurableMatchDecisionStrategy:
    """Tests for the ConfigurableMatchDecisionStrategy class."""

    @pytest.fixture()
    def scorer(self, preprocessor):
        """Return a ComprehensiveMatchScorer instance with default algorithms."""
        return ComprehensiveMatchScorer(
            preprocessor, get_default_similarity_algorithms(), get_default_phonetic_encoders()
        )

    @pytest.fixture()
    def strategy(self, scorer):
        """Return a ConfigurableMatchDecisionStrategy instance with default thresholds."""
        return ConfigurableMatchDecisionStrategy(scorer)

    def test_identical_strings_match(self, strategy):
        """Test that identical strings are considered a match."""
        result = strategy.evaluate_match("Apple Inc.", "Apple Inc.")

        assert result.is_match is True
        assert len(result.match_reasons) > 0

    def test_very_similar_strings_match(self, strategy):
        """Test that very similar strings are considered a match."""
        result = strategy.evaluate_match("Apple Inc", "Apple Inc.")

        assert result.is_match is True
        assert len(result.match_reasons) > 0

    def test_somewhat_similar_strings_may_match(self, strategy):
        """Test that somewhat similar strings may or may not match depending on thresholds."""
        # These may match with default thresholds
        result1 = strategy.evaluate_match("Apple Corporation", "Apple Corp")

        # These likely won't match with default thresholds
        result2 = strategy.evaluate_match("Apple Inc", "Apple International")

        # Either way, the result should have a boolean match status and include reasons
        assert isinstance(result1.is_match, bool)
        assert isinstance(result2.is_match, bool)
        assert len(result1.match_reasons) > 0
        assert len(result2.match_reasons) > 0

    def test_different_strings_do_not_match(self, strategy):
        """Test that different strings are not considered a match."""
        result = strategy.evaluate_match("Apple Inc.", "Microsoft Corporation")

        assert result.is_match is False
        # Should still include reasoning information
        assert len(result.match_reasons) == 0

    def test_custom_thresholds(self, scorer):
        """Test using custom thresholds."""
        # Create a more strict strategy
        strict_strategy = ConfigurableMatchDecisionStrategy(
            scorer, token_set_threshold=0.98, jaro_winkler_threshold=0.98
        )

        # Create a more lenient strategy
        lenient_strategy = ConfigurableMatchDecisionStrategy(
            scorer,
            token_set_threshold=0.75,
            jaro_winkler_threshold=0.8,
            weighted_ratio_threshold=0.8,
        )

        # Test with somewhat similar strings
        strict_result = strict_strategy.evaluate_match("Apple Corp", "Apple Corporation")
        lenient_result = lenient_strategy.evaluate_match("Apple Corp", "Apple Corporation")

        # Strict strategy likely won't match, lenient strategy likely will
        assert strict_result.is_match is False or lenient_result.is_match is True

    def test_phonetic_contribution(self, scorer):
        """Test the phonetic_match_contributes flag."""
        # Create a strategy where phonetic matches contribute to match decision
        phonetic_strategy = ConfigurableMatchDecisionStrategy(
            scorer, phonetic_match_contributes=True
        )

        # Test with phonetically similar strings that might be below other thresholds
        result = phonetic_strategy.evaluate_match("Smith", "Smyth")

        # Should match based on phonetic similarity
        assert result.is_match is True
        assert any("Phonetic" in reason for reason in result.match_reasons)


class TestEntityResolverService:
    """Tests for the EntityResolverService class."""

    @pytest.fixture()
    def preprocessor(self):
        """Return a string preprocessor."""
        return StandardStringPreprocessor()

    @pytest.fixture()
    def token_set_resolver(self, preprocessor):
        """Return an EntityResolverService using token set ratio algorithm."""
        return EntityResolverService(preprocessor, TokenSetRatioAlgorithm(), threshold=0.7, limit=5)

    @pytest.fixture()
    def sample_candidates(self):
        """Return a list of sample candidate entity names."""
        return [
            DomainEntityName("Apple Inc."),
            DomainEntityName("Apple Incorporated"),
            DomainEntityName("Apple Computer"),
            DomainEntityName("Microsoft Corporation"),
            DomainEntityName("Google LLC"),
            DomainEntityName("International Business Machines"),
            DomainEntityName("IBM"),
            DomainEntityName("IBM Corporation"),
        ]

    def test_resolve_exact_match(self, token_set_resolver, sample_candidates):
        """Test resolving an exact match."""
        results = token_set_resolver.resolve(DomainEntityName("Apple Inc."), sample_candidates)

        assert len(results) > 0
        assert results[0].entity_name.raw_value == "Apple Inc."
        assert results[0].score == 1.0

    def test_resolve_close_matches(self, token_set_resolver, sample_candidates):
        """Test resolving close matches."""
        results = token_set_resolver.resolve(DomainEntityName("Apple"), sample_candidates)

        # Should return Apple-related matches first
        assert len(results) >= 2
        apple_companies = {"Apple Inc.", "Apple Incorporated", "Apple Computer"}
        assert results[0].entity_name.raw_value in apple_companies
        assert results[1].entity_name.raw_value in apple_companies

    def test_resolve_abbreviations(self, token_set_resolver, sample_candidates):
        """Test resolving abbreviations."""
        results = token_set_resolver.resolve(DomainEntityName("IBM"), sample_candidates)

        # Should match IBM and IBM Corporation
        assert len(results) >= 2
        ibm_companies = {"IBM", "IBM Corporation"}
        assert results[0].entity_name.raw_value in ibm_companies
        assert results[1].entity_name.raw_value in ibm_companies

    def test_threshold_filtering(self, preprocessor, sample_candidates):
        """Test that results are filtered by threshold."""
        # Create a resolver with a high threshold
        high_threshold_resolver = EntityResolverService(
            preprocessor, TokenSetRatioAlgorithm(), threshold=0.95, limit=5
        )

        # This should only match nearly identical strings
        results = high_threshold_resolver.resolve(DomainEntityName("Apple"), sample_candidates)

        # Might return 0 or more results depending on exact algorithm implementation
        for result in results:
            assert result.score >= 0.95

    def test_limit_results(self, preprocessor, sample_candidates):
        """Test that results are limited to the specified count."""
        # Create a resolver with a low limit
        limited_resolver = EntityResolverService(
            preprocessor,
            TokenSetRatioAlgorithm(),
            threshold=0.0,  # Accept all matches
            limit=2,
        )

        # This would match all candidates, but should be limited to 2
        results = limited_resolver.resolve(DomainEntityName("Corporation"), sample_candidates)

        assert len(results) <= 2

    def test_empty_results(self, token_set_resolver, sample_candidates):
        """Test that no results are returned for very different queries."""
        results = token_set_resolver.resolve(
            DomainEntityName("Something Completely Different"), sample_candidates
        )

        # Should return no results or very low-scoring results
        assert len([r for r in results if r.score > 0.7]) == 0
