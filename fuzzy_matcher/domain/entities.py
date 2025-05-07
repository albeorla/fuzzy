"""Domain entities for the fuzzy matching system.

This module defines the core domain entities used throughout the fuzzy matching system,
implementing the protocols defined in fuzzy_matcher.protocols.interfaces.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass(eq=True, frozen=True)
class DomainEntityName:
    """Value object representing an entity name.

    This class implements the EntityName protocol.

    Attributes
    ----------
        raw_value: The original, unprocessed entity name

    """

    raw_value: str

    def __str__(self) -> str:
        """Return the string representation of the entity name.

        Returns
        -------
            The raw value of the entity name

        """
        return self.raw_value


@dataclass(eq=True, frozen=True)
class DomainProcessedName:
    """Value object representing a processed entity name.

    This class implements the ProcessedName protocol.

    Attributes
    ----------
        original: The original, unprocessed entity name
        processed_value: The processed, standardized entity name

    """

    original: DomainEntityName
    processed_value: str

    def __str__(self) -> str:
        """Return the string representation of the processed name.

        Returns
        -------
            The processed value of the entity name

        """
        return self.processed_value


@dataclass(eq=True, frozen=True)
class DomainMatchScore:
    """Value object representing a match score between two entities.

    This class implements the MatchScore protocol.

    Attributes
    ----------
        original_s1: The original first entity name
        original_s2: The original second entity name
        processed_s1: The processed first entity name
        processed_s2: The processed second entity name
        scores: Dictionary mapping algorithm names to scores or phonetic codes

    """

    original_s1: DomainEntityName
    original_s2: DomainEntityName
    processed_s1: DomainProcessedName
    processed_s2: DomainProcessedName
    scores: Dict[str, Union[float, str]]  # Algorithm name -> score or phonetic code

    def get_score(self, algorithm_name: str) -> Union[float, str]:
        """Get score by algorithm name.

        Args:
        ----
            algorithm_name: Name of the scoring algorithm

        Returns:
        -------
            Score as float (0.0 if not found) or string ("" if not found)
            depending on algorithm type

        """
        value = self.scores.get(algorithm_name)
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            return value

        # Heuristic: if it's a phonetic code (string), return empty string as default
        # For similarity scores (float), return 0.0 as default
        if algorithm_name.startswith(("soundex_", "metaphone_")):  # phonetic codes
            return ""
        return 0.0


@dataclass
class MatchResult:
    """Value object representing match result with decision.

    Attributes
    ----------
        score_details: Detailed match score information
        is_match: Whether the compared entities are considered a match
        match_reasons: List of reasons for the match decision

    """

    score_details: DomainMatchScore  # Changed from 'score' to 'score_details' for clarity
    is_match: bool
    match_reasons: List[str] = field(default_factory=list)

    def add_reason(self, reason: str) -> None:
        """Add a reason for the match decision.

        Args:
        ----
            reason: Reason text to add

        """
        self.match_reasons.append(reason)


@dataclass
class DomainEntityProfile:
    """Entity containing all information about a single entity.

    This class implements the EntityProfile protocol.

    Attributes
    ----------
        entity_id: Unique identifier for the entity
        primary_name: The main name of the entity
        alternate_names: List of alternative names for the entity
        attributes: Dictionary of entity attributes
        relationships: Dictionary mapping relationship types to lists of related entity IDs

    """

    entity_id: str
    primary_name: DomainEntityName
    alternate_names: List[DomainEntityName] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    def add_alternate_name(self, name: DomainEntityName) -> None:
        """Add an alternate name to the entity if it's not already present.

        Args:
        ----
            name: The alternate name to add

        """
        if name.raw_value != self.primary_name.raw_value and name not in self.alternate_names:
            self.alternate_names.append(name)

    def add_attribute(self, key: str, value: Any) -> None:
        """Add or update an attribute for the entity.

        Args:
        ----
            key: Attribute name
            value: Attribute value

        """
        self.attributes[key] = value

    def add_relationship(self, relation_type: str, related_entity_id: str) -> None:
        """Add a relationship to another entity if it doesn't already exist.

        Args:
        ----
            relation_type: Type of the relationship
            related_entity_id: ID of the related entity

        """
        if related_entity_id not in self.relationships[relation_type]:
            self.relationships[relation_type].append(related_entity_id)


@dataclass(eq=True, frozen=True)
class MatchCandidate:
    """Value object representing a potential match with score.

    Attributes
    ----------
        entity_name: The original name of the candidate
        processed_entity_name: The processed name of the candidate
        score: Overall similarity score in range [0.0, 1.0]

    """

    entity_name: DomainEntityName
    processed_entity_name: DomainProcessedName
    score: float

    def __lt__(self, other: "MatchCandidate") -> bool:
        """Compare match candidates by score (higher score is better).

        This allows sorting match candidates in descending order by score
        using the built-in sorted() function.

        Args:
        ----
            other: The match candidate to compare with

        Returns:
        -------
            True if this candidate has a higher score, False otherwise

        """
        # Higher score is better
        return self.score > other.score
