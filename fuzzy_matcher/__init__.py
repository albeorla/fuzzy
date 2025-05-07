"""Fuzzy Matcher - A flexible fuzzy string matching and entity resolution library.

This package provides tools for preprocessing strings, calculating string similarity
using various algorithms, and resolving entities based on fuzzy name matching.
"""

from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.domain.entities import (
    DomainEntityName,
    DomainEntityProfile,
    DomainMatchScore,
    DomainProcessedName,
    MatchCandidate,
    MatchResult,
)

__version__ = "0.1.0"

__all__ = [
    "EntityResolutionFacade",
    "DomainEntityName",
    "DomainEntityProfile",
    "DomainMatchScore",
    "DomainProcessedName",
    "MatchCandidate",
    "MatchResult",
]
