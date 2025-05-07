"""End-to-end tests based on the examples from main.py."""

import pytest

from fuzzy_matcher.application.facades import EntityResolutionFacade


class TestMainExamples:
    """End-to-end tests that validate the example use cases from main.py."""

    @pytest.fixture()
    def facade(self):
        """Return a fresh EntityResolutionFacade instance."""
        return EntityResolutionFacade()

    def test_string_matching_examples(self, facade):
        """Test the string comparison examples from main.py."""
        # Test a subset of the string pairs from demo_string_matching
        string_pairs = [
            ("Apple Incorporated", "Apple, Inc."),
            ("Apple Incorporated", "Apple inc."),
            ("Apple Incorporated", "Microsoft Corp."),
            ("Apple Incorporated", "appel incorporated"),  # Typo
            ("Smith & Jones LLC", "Smith and Jones L.L.C."),
            ("John Doe", "Jonh Doe"),  # Typo
            ("", "Something"),  # Test empty string
            ("Test", "Test"),  # Test identical
        ]

        for s1, s2 in string_pairs:
            result = facade.compare_strings(s1, s2)

            # Basic validation of the result structure
            assert isinstance(result, dict)
            assert "is_match" in result
            assert "scores" in result
            assert "processed" in result
            assert "phonetic" in result

            # Identical strings should match
            if s1 == s2 and s1:
                assert result["is_match"] is True

            # Very different strings should not match
            if s1 == "Apple Incorporated" and s2 == "Microsoft Corp.":
                assert result["is_match"] is False

            # Empty strings should have special handling
            if not s1 or not s2:
                assert result["processed"]["s1"] == "" or result["processed"]["s2"] == ""

    def test_entity_resolution_examples(self, facade):
        """Test the entity resolution examples from main.py."""
        # Register entities as in demo_entity_resolution_and_finding
        facade.register_entity(
            "E001",
            "Apple Inc.",
            ["Apple Incorporated", "Apple Computer", "Apple"],
            {"industry": "Technology", "founded": 1976, "ticker": "AAPL"},
        )

        facade.register_entity(
            "E002",
            "Microsoft Corporation",
            ["Microsoft Corp", "MSFT", "Microsoft"],
            {"industry": "Technology", "founded": 1975, "ticker": "MSFT"},
        )

        facade.register_entity(
            "E003",
            "International Business Machines",
            ["IBM", "IBM Corporation", "Big Blue"],
            {"industry": "Technology", "founded": 1911, "ticker": "IBM"},
        )

        facade.register_entity(
            "E004",
            "Google LLC",
            ["Google", "Alphabet Inc.", "Google Inc"],  # Added Google Inc as alternate name
            {"industry": "Technology", "founded": 1998, "ticker": "GOOGL"},
        )

        # Test finding entities by various queries
        queries = [
            "Apple",
            "apple inc",
            "appel incorporated",  # Typo
            "Microsoft",
            "IBM Corp",
            "Google Inc",  # Different suffix
            "NonExistent Company",
        ]

        for query_str in queries:
            entity = facade.find_by_name(query_str)

            # Verify that we can find entities or get appropriate results for all test cases
            if "Apple" in query_str or "apple" in query_str or "appel" in query_str:
                assert entity is not None
                assert entity.entity_id == "E001"

            elif "Microsoft" in query_str:
                assert entity is not None
                assert entity.entity_id == "E002"

            elif "IBM" in query_str:
                assert entity is not None
                assert entity.entity_id == "E003"

            elif "Google" in query_str:
                print(f"Query: {query_str}, Result: {entity}")
                assert entity is not None
                assert entity.entity_id == "E004"

            else:  # NonExistent Company
                assert entity is None

                # In this case, try the fallback search
                all_entity_names_str = [
                    name.raw_value for name in facade.repository.get_all_entity_names()
                ]

                best_matches = facade.find_best_matches_in_list(
                    query_str, all_entity_names_str, algorithm_name="weighted_ratio", threshold=0.7
                )

                # Should return some results or empty list
                assert isinstance(best_matches, list)

    def test_find_best_matches_examples(self, facade):
        """Test the best matches examples from main.py."""
        query = "Jonh Doe"  # Typo
        choices = [
            "John Doe",
            "Jane Doe",
            "Jonathan Doering",
            "john doe llc",
            "Doe, John",
            "Peter Jones",
        ]

        # Test with different algorithms
        for algorithm_name in ["token_set_ratio", "jaro_winkler", "weighted_ratio", "levenshtein"]:
            matches = facade.find_best_matches_in_list(
                query, choices, algorithm_name=algorithm_name, threshold=0.6
            )

            # Verify basic structure
            assert isinstance(matches, list)

            # Should find at least one match with our relaxed threshold
            assert len(matches) > 0

            # Top match should be to "John Doe" (correcting the typo)
            if matches:
                assert matches[0]["matched_candidate_original"] == "John Doe"

                # Verify result structure
                assert "original_query" in matches[0]
                assert "matched_candidate_original" in matches[0]
                assert "matched_candidate_processed" in matches[0]
                assert "score" in matches[0]
                assert "algorithm_used" in matches[0]

                # Algorithm should be correctly reported
                assert matches[0]["algorithm_used"] == algorithm_name
