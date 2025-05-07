"""Application services for the fuzzy matching system."""

from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.application.services import (
    ComprehensiveMatchScorer,
    ConfigurableMatchDecisionStrategy,
    EntityResolverService,
)

__all__ = [
    "EntityResolutionFacade",
    "ComprehensiveMatchScorer",
    "ConfigurableMatchDecisionStrategy",
    "EntityResolverService",
]
