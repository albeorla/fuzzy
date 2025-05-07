"""Protocol definitions for the fuzzy matching system."""

from fuzzy_matcher.protocols.interfaces import (
    EntityName,
    EntityProfile,
    EntityRepository,
    EntityResolver,
    MatchDecisionStrategy,
    MatchingAlgorithm,
    MatchScore,
    PhoneticEncoder,
    ProcessedName,
    StringOrNumeric,
    StringPreprocessor,
)

__all__ = [
    "EntityName",
    "EntityProfile",
    "EntityRepository",
    "EntityResolver",
    "MatchDecisionStrategy",
    "MatchingAlgorithm",
    "MatchScore",
    "PhoneticEncoder",
    "ProcessedName",
    "StringOrNumeric",
    "StringPreprocessor",
]
