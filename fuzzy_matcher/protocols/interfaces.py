"""Protocol definitions for the fuzzy matching system.

This module defines the interfaces (protocols) for the various components
of the fuzzy matching system. These protocols establish the contracts that
implementations must adhere to.
"""

from __future__ import annotations

from typing import Any, Protocol, TypeVar, Union

# Forward references to domain entities
from fuzzy_matcher.domain.entities import MatchCandidate, MatchResult

# Type definitions
T = TypeVar("T")
StringOrNumeric = Union[str, int, float]  # Input type for preprocessing


class EntityName(Protocol):
    """Protocol defining the interface for an entity name."""

    raw_value: str

    def __str__(self) -> str:
        """Return the string representation of the entity name."""
        ...


class ProcessedName(Protocol):
    """Protocol defining the interface for a processed entity name."""

    original: EntityName
    processed_value: str

    def __str__(self) -> str:
        """Return the string representation of the processed name."""
        ...


class MatchScore(Protocol):
    """Protocol defining the interface for match scores between entities."""

    original_s1: EntityName
    original_s2: EntityName
    processed_s1: ProcessedName
    processed_s2: ProcessedName
    scores: dict[str, float | str]

    def get_score(self, algorithm: str) -> float | str:
        """Get score by algorithm name.

        Args:
        ----
            algorithm: Name of the scoring algorithm

        Returns:
        -------
            Score as float or string depending on algorithm type

        """
        ...


class EntityProfile(Protocol):
    """Protocol defining the interface for entity profiles."""

    entity_id: str
    primary_name: EntityName
    alternate_names: list[EntityName]
    attributes: dict[str, Any]
    relationships: dict[str, list[str]]

    def add_alternate_name(self, name: EntityName) -> None:
        """Add an alternate name to the entity.

        Args:
        ----
            name: The alternate name to add

        """
        ...

    def add_attribute(self, key: str, value: Any) -> None:
        """Add or update an attribute for the entity.

        Args:
        ----
            key: Attribute name
            value: Attribute value

        """
        ...

    def add_relationship(self, relation_type: str, related_entity_id: str) -> None:
        """Add a relationship to another entity.

        Args:
        ----
            relation_type: Type of the relationship
            related_entity_id: ID of the related entity

        """
        ...


class StringPreprocessor(Protocol):
    """Protocol defining string preprocessor interface."""

    def preprocess(self, text: StringOrNumeric) -> str:
        """Preprocess input string to standardized form.

        Args:
        ----
            text: Input text to preprocess

        Returns:
        -------
            Preprocessed string in standardized form

        """
        ...


class MatchingAlgorithm(Protocol):
    """Protocol defining matching algorithm interface."""

    @property
    def name(self) -> str:
        """Returns the unique name of the algorithm."""
        ...

    def calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings.

        Args:
        ----
            s1: First string
            s2: Second string

        Returns:
        -------
            Similarity score in range [0.0, 1.0]

        """
        ...


class PhoneticEncoder(Protocol):
    """Protocol defining phonetic encoder interface."""

    @property
    def name(self) -> str:
        """Returns the unique name of the encoder."""
        ...

    def encode(self, text: str) -> str:
        """Encode text using a phonetic algorithm.

        Args:
        ----
            text: Text to encode

        Returns:
        -------
            Phonetic encoding of the text

        """
        ...


class MatchDecisionStrategy(Protocol):
    """Protocol defining overall matching decision strategy."""

    def evaluate_match(self, s1: str, s2: str) -> MatchResult:
        """Determine if two strings match according to strategy and provide result.

        Args:
        ----
            s1: First string
            s2: Second string

        Returns:
        -------
            Match result with decision and reasoning

        """
        ...


class EntityResolver(Protocol):
    """Protocol defining entity resolver interface."""

    def resolve(self, query: EntityName, candidates: list[EntityName]) -> list[MatchCandidate]:
        """Find best matching entities for the query entity name.

        Args:
        ----
            query: Query entity name
            candidates: List of candidate entity names

        Returns:
        -------
            List of match candidates ordered by relevance

        """
        ...


class EntityRepository(Protocol):
    """Protocol for entity data access."""

    def find_by_id(self, entity_id: str) -> EntityProfile | None:
        """Find entity by ID.

        Args:
        ----
            entity_id: ID of the entity to find

        Returns:
        -------
            Entity profile if found, None otherwise

        """
        ...

    def find_by_primary_name(self, name: EntityName) -> EntityProfile | None:
        """Find entity by primary name.

        Args:
        ----
            name: Primary name to find

        Returns:
        -------
            Entity profile if found, None otherwise

        """
        ...

    def find_candidates_by_name(self, name: EntityName, limit: int = 10) -> list[EntityProfile]:
        """Find candidate entities by name.

        Args:
        ----
            name: Name to search for
            limit: Maximum number of candidates to return

        Returns:
        -------
            List of candidate entity profiles

        """
        ...

    def save(self, entity: EntityProfile) -> None:
        """Save entity to repository.

        Args:
        ----
            entity: Entity profile to save

        """
        ...

    def get_all_entity_names(self) -> list[EntityName]:
        """Get all entity names in the repository.

        Returns
        -------
            List of all entity names

        """
        ...
