"""End-to-end tests for exact matching behavior in the fuzzy matching system."""

import pytest

from fuzzy_matcher.application.facades import EntityResolutionFacade


class TestExactMatching:
    """Tests for exact entity matching behavior."""

    @pytest.fixture()
    def facade(self):
        """Return an EntityResolutionFacade instance with default components."""
        return EntityResolutionFacade()

    def test_exact_match_prioritization(self, facade):
        """Test that exact matches are prioritized over fuzzy matches."""
        # Register entities with similar names
        facade.register_entity(
            "E001",
            "Apple Inc.",
            ["Apple", "Apple Computer"],
            {"industry": "Technology", "founded": 1976},
        )
        facade.register_entity(
            "E002",
            "Apple Incorporated",
            ["Apple Inc", "Apple"],
            {"industry": "Technology", "founded": 1976},
        )

        # Test that an exact match is prioritized
        result = facade.find_by_name("Apple Inc.")
        assert result is not None
        assert result.entity_id == "E001"

        # Test that an exact match with an alternate name is prioritized
        result = facade.find_by_name("Apple Computer")
        assert result is not None
        assert result.entity_id == "E001"

    def test_exact_match_in_list(self, facade):
        """Test that exact matches are prioritized in list comparison."""
        # Create a set of candidates
        candidates = [
            "Apple Inc.",
            "Apple Incorporated",
            "Apple Computer",
            "Microsoft Corporation",
            "Google LLC",
        ]

        # Test that an exact match is found first
        results = facade.find_best_matches_in_list("Apple Inc.", candidates)
        assert len(results) > 0
        assert results[0]["matched_candidate_original"] == "Apple Inc."
        assert results[0]["score"] == 1.0

        # Test that very similar strings match with high scores
        results = facade.find_best_matches_in_list("Apple", candidates)
        assert len(results) >= 3  # Should find the three Apple variants
        apple_results = [r for r in results if "Apple" in r["matched_candidate_original"]]
        assert len(apple_results) >= 3

    def test_fuzzy_but_not_exact_match(self, facade):
        """Test that fuzzy matches work for non-exact matches."""
        candidates = [
            "Apple Inc.",
            "Apple Incorporated",
            "Microsoft Corporation",
            "Google LLC",
        ]

        # This is close to "Apple" but not an exact match
        results = facade.find_best_matches_in_list("Aple", candidates)
        assert len(results) > 0
        assert "Apple" in results[0]["matched_candidate_original"]
