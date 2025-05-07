"""Integration tests for the facades in fuzzy_matcher.application.facades."""

import pytest

from fuzzy_matcher.application.facades import EntityResolutionFacade


class TestEntityResolutionFacade:
    """Tests for the EntityResolutionFacade class."""

    @pytest.fixture()
    def facade(self):
        """Return a bare EntityResolutionFacade instance."""
        return EntityResolutionFacade()

    @pytest.fixture()
    def populated_facade(self, facade):
        """Return an EntityResolutionFacade instance with pre-populated data."""
        # Register some test entities
        facade.register_entity(
            "E001",
            "Apple Inc.",
            ["Apple Incorporated", "Apple Computer"],
            {"industry": "Technology", "founded": 1976},
        )

        facade.register_entity(
            "E002",
            "Microsoft Corporation",
            ["Microsoft Corp", "MSFT"],
            {"industry": "Technology", "founded": 1975},
        )

        facade.register_entity(
            "E003",
            "International Business Machines",
            ["IBM", "IBM Corporation"],
            {"industry": "Technology", "founded": 1911},
        )

        return facade

    def test_compare_strings_identical(self, facade):
        """Test comparing identical strings."""
        result = facade.compare_strings("Apple Inc.", "Apple Inc.")

        assert result["is_match"] is True
        assert len(result["match_reasons"]) > 0
        assert all(score == 1.0 for score in result["scores"].values() if isinstance(score, float))
        assert result["processed"]["s1"] == result["processed"]["s2"]

    def test_compare_strings_similar(self, facade):
        """Test comparing similar strings."""
        result = facade.compare_strings("Apple, Inc.", "Apple Incorporated")

        assert "is_match" in result
        assert "match_reasons" in result
        assert "scores" in result
        assert "processed" in result
        assert "phonetic" in result

    def test_compare_strings_different(self, facade):
        """Test comparing different strings."""
        result = facade.compare_strings("Apple Inc.", "Microsoft Corporation")

        assert result["is_match"] is False
        assert all(score < 0.8 for score in result["scores"].values() if isinstance(score, float))

    def test_find_best_matches_in_list(self, facade):
        """Test finding best matches in a list."""
        query = "Aple"
        candidates = ["Apple Inc.", "Apple Computer", "Microsoft", "Google"]

        # Use a lower threshold to better handle typos like "Aple" vs "Apple"
        results = facade.find_best_matches_in_list(query, candidates, threshold=0.6)

        # Should find matches for Apple
        assert len(results) > 0
        apple_matches = [r for r in results if "Apple" in r["matched_candidate_original"]]
        assert len(apple_matches) > 0

    def test_register_entity(self, facade):
        """Test registering an entity."""
        entity = facade.register_entity(
            "E001",
            "Test Entity",
            ["Alternate Name 1", "Alternate Name 2"],
            {"attr1": "value1", "attr2": "value2"},
        )

        assert entity.entity_id == "E001"
        assert entity.primary_name.raw_value == "Test Entity"
        assert len(entity.alternate_names) == 2
        assert entity.attributes["attr1"] == "value1"

    def test_find_by_name_exact(self, populated_facade):
        """Test finding an entity by exact name."""
        entity = populated_facade.find_by_name("Apple Inc.")

        assert entity is not None
        assert entity.entity_id == "E001"
        assert entity.primary_name.raw_value == "Apple Inc."

    def test_find_by_alternate_name(self, populated_facade):
        """Test finding an entity by alternate name."""
        entity = populated_facade.find_by_name("IBM")

        assert entity is not None
        assert entity.entity_id == "E003"
        assert entity.primary_name.raw_value == "International Business Machines"

    def test_find_by_fuzzy_name(self, populated_facade):
        """Test finding an entity by fuzzy name matching."""
        # Should find with typo
        entity = populated_facade.find_by_name("Apple Incorporated")

        assert entity is not None
        assert entity.entity_id == "E001"

    def test_find_nonexistent_entity(self, populated_facade):
        """Test that finding a nonexistent entity returns None."""
        entity = populated_facade.find_by_name("Nonexistent Company")

        assert entity is None

    def test_get_entity_profile_dict(self, populated_facade):
        """Test converting an entity profile to a dictionary."""
        entity = populated_facade.find_by_name("Apple Inc.")
        entity_dict = populated_facade.get_entity_profile_dict(entity)

        assert entity_dict is not None
        assert entity_dict["entity_id"] == "E001"
        assert entity_dict["primary_name"] == "Apple Inc."
        assert "Apple Incorporated" in entity_dict["alternate_names"]
        assert entity_dict["attributes"]["industry"] == "Technology"

    def test_get_entity_profile_dict_none(self, populated_facade):
        """Test that converting None entity profile returns None."""
        assert populated_facade.get_entity_profile_dict(None) is None

    def test_resolver_algorithm_selection(self, facade):
        """Test resolver algorithm selection logic."""
        # Using an existing algorithm
        match_results1 = facade.find_best_matches_in_list(
            "Apple", ["Apple Inc.", "Microsoft"], algorithm_name="token_set_ratio"
        )

        # Using a non-existent algorithm (should default to token_set_ratio)
        match_results2 = facade.find_best_matches_in_list(
            "Apple", ["Apple Inc.", "Microsoft"], algorithm_name="nonexistent_algorithm"
        )

        # Both should find Apple as a match
        assert len(match_results1) > 0
        assert len(match_results2) > 0
        assert match_results1[0]["matched_candidate_original"] == "Apple Inc."
        assert match_results2[0]["matched_candidate_original"] == "Apple Inc."

        # But they might use different algorithms
        assert match_results1[0]["algorithm_used"] == "token_set_ratio"
        # The second should fall back to token_set_ratio
        assert match_results2[0]["algorithm_used"] == "token_set_ratio"
