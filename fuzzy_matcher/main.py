"""Main demo module for the fuzzy matching system.

This module demonstrates the usage of the fuzzy matching system with
examples for string matching, entity resolution, and finding best matches.
"""

from typing import cast

from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.domain.entities import DomainEntityProfile


def demo_string_matching() -> None:
    """Demonstrate string comparison functionality.

    This demo compares pairs of strings using the fuzzy matching system
    and prints detailed match information.
    """
    facade = EntityResolutionFacade()

    string_pairs = [
        ("Apple Incorporated", "Apple, Inc."),
        ("Apple Incorporated", "Apple inc."),
        ("Apple Incorporated", "Apple   inc"),
        ("Apple Incorporated", "Microsoft Corp."),
        ("Apple Incorporated", "appel incorporated"),  # Typo
        ("Apple Incorporated", "Incorporated Apple"),
        ("Smith & Jones LLC", "Smith and Jones L.L.C."),
        ("John Doe", "Jonh Doe"),  # Typo
        ("International Business Machines", "IBM"),
        ("Société Générale", "Societe Generale SA"),
        ("", "Something"),  # Test empty string
        ("Test", "Test"),  # Test identical
    ]

    print("=== String Matching Demo ===")
    for s1, s2 in string_pairs:
        result = facade.compare_strings(s1, s2)
        print(f"Comparing '{s1}' and '{s2}':")
        print(f"  Processed: '{result['processed']['s1']}' vs '{result['processed']['s2']}'")
        print(f"  Match: {result['is_match']}")

        scores_str = ", ".join(
            [
                f"{name.replace('_ratio','').upper()}={score:.2f}"
                for name, score in result["scores"].items()
                if isinstance(score, float)
            ]
        )
        print(f"  Scores: {scores_str}")

        if result["phonetic"]["soundex_match"]:
            print(f"  Soundex: {result['phonetic']['soundex_s1']} (Match)")

        if result["phonetic"]["metaphone_match"]:
            print(f"  Metaphone: {result['phonetic']['metaphone_s1']} (Match)")

        if result["match_reasons"]:
            print(f"  Reasons: {'; '.join(result['match_reasons'])}")

        print("-" * 20)


def demo_entity_resolution_and_finding() -> None:
    """Demonstrate entity registration and finding functionality.

    This demo registers several entities and demonstrates finding them
    by name using exact matching and fuzzy resolution.
    """
    facade = EntityResolutionFacade()

    # Register some entities
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
        ["Google", "Alphabet Inc."],  # Alphabet is parent, but often used
        {"industry": "Technology", "founded": 1998, "ticker": "GOOGL"},
    )

    print("\n=== Entity Resolution & Finding Demo ===")
    queries = [
        "Apple",
        "apple inc",
        "appel incorporated",  # Typo
        "Microsoft",
        "MS Corp",  # Abbreviation and slight change
        "International Business Machines Corp",  # Full name + suffix
        "IBM Corp",
        "Google Inc",  # Different suffix
        "NonExistent Company",
    ]

    for query_str in queries:
        print(f"Searching for entity: '{query_str}'")
        found_entity_profile = facade.find_by_name(query_str)
        # Cast the found entity to DomainEntityProfile for the get_entity_profile_dict call
        entity_dict = facade.get_entity_profile_dict(
            cast(DomainEntityProfile, found_entity_profile)
        )

        if entity_dict:
            print(f"  Found: {entity_dict['primary_name']} (ID: {entity_dict['entity_id']})")
            print(f"  Attributes: {entity_dict['attributes']}")
        else:
            # If not found, try finding best matches from the list of known entities
            print(f"  No exact entity resolution. Finding best matches for '{query_str}'...")
            all_entity_names_str = [
                name.raw_value for name in facade.repository.get_all_entity_names()
            ]

            # Use a generally good algorithm for this fallback search
            best_matches = facade.find_best_matches_in_list(
                query_str,
                all_entity_names_str,
                algorithm_name="weighted_ratio",
                threshold=0.7,  # Lower threshold for "best guess"
                limit=3,
            )

            if best_matches:
                print(f"  Potential matches for '{query_str}':")
                for match in best_matches:
                    name = match["matched_candidate_original"]
                    score = match["score"]
                    print(f"    - '{name}' (Score: {score:.2f})")
            else:
                print(f"  No strong candidates found for '{query_str}'.")

        print("-" * 20)


def demo_find_best_matches_in_list() -> None:
    """Demonstrate finding best matches in a list of candidates.

    This demo shows how to find the best matching strings for a query string
    from a list of candidate strings using different algorithms.
    """
    facade = EntityResolutionFacade()

    query = "Jonh Doe"  # Typo
    choices = [
        "John Doe",
        "Jane Doe",
        "Jonathan Doering",
        "john doe llc",
        "Doe, John",
        "Peter Jones",
    ]

    print("\n=== Find Best Matches in List Demo ===")
    print(f"Finding best matches for '{query}' in {choices}:")

    # Try different algorithms
    for algorithm_name in ["token_set_ratio", "jaro_winkler", "weighted_ratio", "levenshtein"]:
        print(f"\n  Using {algorithm_name}:")
        matches = facade.find_best_matches_in_list(
            query, choices, algorithm_name=algorithm_name, threshold=0.6
        )

        if matches:
            for match in matches:
                print(
                    f"    - '{match['matched_candidate_original']}' "
                    f"(Processed: '{match['matched_candidate_processed']}', "
                    f"Score: {match['score']:.2f})"
                )
        else:
            print("    No matches found above threshold.")

    print("-" * 20)


def run_demos() -> None:
    """Run all demos to showcase the fuzzy matching functionality."""
    demo_string_matching()
    demo_entity_resolution_and_finding()
    demo_find_best_matches_in_list()


def main() -> None:
    """Run the fuzzy matcher application.

    This function provides an interactive demo of the fuzzy matching functionality.
    Users can choose what type of matching to test.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Fuzzy Matcher CLI")
    parser.add_argument(
        "--demo",
        choices=["all", "string", "entity", "list"],
        default="all",
        help="Which demo to run (all, string, entity, or list)",
    )
    args = parser.parse_args()

    print("🔍 Fuzzy Matcher Demo")
    print("=====================")

    if args.demo == "all" or args.demo == "string":
        demo_string_matching()

    if args.demo == "all" or args.demo == "entity":
        demo_entity_resolution_and_finding()

    if args.demo == "all" or args.demo == "list":
        demo_find_best_matches_in_list()

    print("\nDemo completed. Thank you for using Fuzzy Matcher! 🎉")


if __name__ == "__main__":
    run_demos()
