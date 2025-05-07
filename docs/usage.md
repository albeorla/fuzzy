# Usage Guide

This document provides detailed examples of how to use the Fuzzy Matcher library.

## Basic String Comparison

The simplest use case is comparing two strings for similarity:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

# Create a facade with default components
facade = EntityResolutionFacade()

# Compare two strings
result = facade.compare_strings("Apple Inc.", "Apple Incorporated")

# Check if they match
print(f"Is match: {result['is_match']}")  # Should print: Is match: True

# Examine detailed scores
print(f"Scores: {result['scores']}")
# Example output:
# Scores: {'levenshtein': 0.765, 'jaro_winkler': 0.887, 'token_set_ratio': 1.0, ...}

# Check the preprocessed strings
print(f"Processed: '{result['processed']['s1']}' vs '{result['processed']['s2']}'")
# Example output:
# Processed: 'apple inc' vs 'apple incorporated'

# Check phonetic encoding matches
if result["phonetic"]["soundex_match"]:
    print(f"Soundex: {result['phonetic']['soundex_s1']} (Match)")
```

## Finding Best Matches in a List

You can find the best matches for a query string from a list of candidate strings:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

facade = EntityResolutionFacade()

query = "Jonh Doe"  # Typo
choices = ["John Doe", "Jane Doe", "Jonathan Doering", "Peter Smith"]

# Find matches using a specific algorithm
matches = facade.find_best_matches_in_list(
    query,
    choices,
    algorithm_name='jaro_winkler',  # Algorithm to use
    threshold=0.7,                  # Minimum similarity score [0.0, 1.0]
    limit=2                         # Maximum number of matches to return
)

# Print matches
for match in matches:
    print(f"Match: {match['matched_candidate_original']} (Score: {match['score']:.2f})")

# Try different algorithms
for algorithm in ['levenshtein', 'token_set_ratio', 'weighted_ratio']:
    print(f"\nUsing {algorithm}:")
    matches = facade.find_best_matches_in_list(
        query, choices, algorithm_name=algorithm, threshold=0.6
    )
    for match in matches:
        print(f"  {match['matched_candidate_original']} (Score: {match['score']:.2f})")
```

## Entity Registration and Resolution

For more complex scenarios, you can register entities with primary and alternate names:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

facade = EntityResolutionFacade()

# Register entities
facade.register_entity(
    entity_id="E001",
    primary_name_str="Apple Inc.",
    alternate_names_str=["Apple Incorporated", "Apple Computer", "Apple"],
    attributes={"industry": "Technology", "founded": 1976, "ticker": "AAPL"}
)

facade.register_entity(
    entity_id="E002",
    primary_name_str="Microsoft Corporation",
    alternate_names_str=["Microsoft Corp", "MSFT", "Microsoft"],
    attributes={"industry": "Technology", "founded": 1975}
)

# Find entity by name (exact or fuzzy)
entity = facade.find_by_name("apple incorporated")

if entity:
    # Get entity as a dictionary for easy access
    entity_dict = facade.get_entity_profile_dict(entity)
    print(f"Found entity: {entity_dict['primary_name']} (ID: {entity_dict['entity_id']})")
    print(f"Attributes: {entity_dict['attributes']}")
    print(f"Alternate names: {entity_dict['alternate_names']}")
else:
    print("Entity not found")

# Try a slightly misspelled name
entity = facade.find_by_name("appel inc")  # Typo
if entity:
    entity_dict = facade.get_entity_profile_dict(entity)
    print(f"Found entity despite typo: {entity_dict['primary_name']}")
```

## Advanced Usage

### Custom Preprocessing

You can customize the string preprocessing pipeline:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.infrastructure.preprocessors import (
    AccentRemovalStep,
    LowercaseConversionStep,
    PunctuationRemovalStep,
    StandardStringPreprocessor,
    WhitespaceNormalizationStep,
)

# Create a custom preprocessor with specific steps
custom_preprocessor = StandardStringPreprocessor(steps=[
    LowercaseConversionStep(),  # Convert to lowercase first
    AccentRemovalStep(),        # Then remove accents
    PunctuationRemovalStep(),   # Then remove punctuation
    WhitespaceNormalizationStep(),  # Finally normalize whitespace
])

# Create a facade with the custom preprocessor
facade = EntityResolutionFacade(preprocessor=custom_preprocessor)

# Use the facade as normal
result = facade.compare_strings("Société Générale", "Societe Generale")
print(f"Is match: {result['is_match']}")
```

### Custom Matching Algorithms

You can provide custom algorithms or select specific ones to use:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.infrastructure.algorithms import (
    JaroWinklerAlgorithm,
    LevenshteinAlgorithm,
    TokenSetRatioAlgorithm,
)

# Create a facade with specific algorithms
facade = EntityResolutionFacade(
    similarity_algorithms={
        "levenshtein": LevenshteinAlgorithm(),
        "jaro_winkler": JaroWinklerAlgorithm(),
        "token_set": TokenSetRatioAlgorithm(),
    }
)

# Use the facade as normal
result = facade.compare_strings("Apple Inc.", "Apple Incorporated")
print(f"Available algorithms: {list(result['scores'].keys())}")
```

### Using the Repository Directly

For more advanced entity management, you can work with the repository directly:

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.domain.entities import DomainEntityName, DomainEntityProfile

facade = EntityResolutionFacade()
repository = facade.repository

# Create an entity profile directly
entity = DomainEntityProfile(
    entity_id="E003",
    primary_name=DomainEntityName("Google LLC"),
    alternate_names=[
        DomainEntityName("Google"),
        DomainEntityName("Alphabet Inc."),
    ],
    attributes={"industry": "Technology", "founded": 1998}
)

# Save the entity
repository.save(entity)

# Find entity by ID
found_entity = repository.find_by_id("E003")
if found_entity:
    print(f"Found by ID: {found_entity.primary_name.raw_value}")

# Find entities with phonetic similarity
candidates = repository.find_candidates_by_name(DomainEntityName("Googel"))  # Typo
for candidate in candidates:
    print(f"Candidate: {candidate.primary_name.raw_value}")
```

## Command-Line Interface

The library includes a simple command-line interface for demonstration purposes:

```bash
# Run the full demo
poetry run demo

# Run specific demo categories
poetry run fuzzy --demo string   # String matching demo
poetry run fuzzy --demo entity   # Entity resolution demo
poetry run fuzzy --demo list     # List matching demo
```
