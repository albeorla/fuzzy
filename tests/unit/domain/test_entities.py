"""Unit tests for the domain entities in fuzzy_matcher.domain.entities."""

import pytest

from fuzzy_matcher.domain.entities import (
    DomainEntityName,
    DomainEntityProfile,
    DomainMatchScore,
    DomainProcessedName,
    MatchCandidate,
    MatchResult,
)


class TestDomainEntityName:
    """Tests for the DomainEntityName class."""

    def test_creation(self):
        """Test creating a DomainEntityName instance."""
        name = DomainEntityName("Apple Inc.")
        assert name.raw_value == "Apple Inc."

    def test_string_representation(self):
        """Test string representation of DomainEntityName."""
        name = DomainEntityName("Apple Inc.")
        assert str(name) == "Apple Inc."

    def test_equality(self):
        """Test equality of DomainEntityName instances."""
        name1 = DomainEntityName("Apple Inc.")
        name2 = DomainEntityName("Apple Inc.")
        name3 = DomainEntityName("Microsoft Corp")

        assert name1 == name2
        assert name1 != name3

    def test_immutability(self):
        """Test that DomainEntityName is immutable."""
        name = DomainEntityName("Apple Inc.")
        with pytest.raises(AttributeError):
            name.raw_value = "New Value"


class TestDomainProcessedName:
    """Tests for the DomainProcessedName class."""

    def test_creation(self):
        """Test creating a DomainProcessedName instance."""
        original = DomainEntityName("Apple Inc.")
        processed = DomainProcessedName(original, "apple inc")

        assert processed.original == original
        assert processed.processed_value == "apple inc"

    def test_string_representation(self):
        """Test string representation of DomainProcessedName."""
        original = DomainEntityName("Apple Inc.")
        processed = DomainProcessedName(original, "apple inc")

        assert str(processed) == "apple inc"

    def test_immutability(self):
        """Test that DomainProcessedName is immutable."""
        original = DomainEntityName("Apple Inc.")
        processed = DomainProcessedName(original, "apple inc")

        with pytest.raises(AttributeError):
            processed.processed_value = "new value"

        with pytest.raises(AttributeError):
            processed.original = DomainEntityName("New")


class TestDomainMatchScore:
    """Tests for the DomainMatchScore class."""

    @pytest.fixture()
    def match_score(self):
        """Return a sample match score."""
        original_s1 = DomainEntityName("Apple Inc.")
        original_s2 = DomainEntityName("Apple Incorporated")
        processed_s1 = DomainProcessedName(original_s1, "apple inc")
        processed_s2 = DomainProcessedName(original_s2, "apple incorporated")

        scores = {
            "levenshtein": 0.8,
            "jaro_winkler": 0.9,
            "token_set_ratio": 0.95,
            "soundex_s1": "A140",
            "soundex_s2": "A140",
            "metaphone_s1": "APL",
            "metaphone_s2": "APL",
        }

        return DomainMatchScore(
            original_s1=original_s1,
            original_s2=original_s2,
            processed_s1=processed_s1,
            processed_s2=processed_s2,
            scores=scores,
        )

    def test_creation(self, match_score):
        """Test creating a DomainMatchScore instance."""
        assert match_score.original_s1.raw_value == "Apple Inc."
        assert match_score.original_s2.raw_value == "Apple Incorporated"
        assert match_score.processed_s1.processed_value == "apple inc"
        assert match_score.processed_s2.processed_value == "apple incorporated"
        assert len(match_score.scores) == 7

    def test_get_score_float(self, match_score):
        """Test getting a float score from DomainMatchScore."""
        assert match_score.get_score("levenshtein") == 0.8
        assert match_score.get_score("jaro_winkler") == 0.9
        assert match_score.get_score("token_set_ratio") == 0.95

    def test_get_score_string(self, match_score):
        """Test getting a string score from DomainMatchScore."""
        assert match_score.get_score("soundex_s1") == "A140"
        assert match_score.get_score("soundex_s2") == "A140"
        assert match_score.get_score("metaphone_s1") == "APL"
        assert match_score.get_score("metaphone_s2") == "APL"

    def test_get_nonexistent_score(self, match_score):
        """Test getting a nonexistent score from DomainMatchScore."""
        assert match_score.get_score("nonexistent_algorithm") == 0.0
        assert match_score.get_score("soundex_nonexistent") == ""
        assert match_score.get_score("metaphone_nonexistent") == ""

    def test_immutability(self, match_score):
        """Test that DomainMatchScore is immutable."""
        with pytest.raises(AttributeError):
            match_score.scores = {}

        with pytest.raises(AttributeError):
            match_score.original_s1 = DomainEntityName("New")


class TestMatchResult:
    """Tests for the MatchResult class."""

    @pytest.fixture()
    def match_score(self):
        """Return a sample match score for testing."""
        original_s1 = DomainEntityName("Apple Inc.")
        original_s2 = DomainEntityName("Apple Incorporated")
        processed_s1 = DomainProcessedName(original_s1, "apple inc")
        processed_s2 = DomainProcessedName(original_s2, "apple incorporated")

        scores = {
            "levenshtein": 0.8,
            "jaro_winkler": 0.9,
            "token_set_ratio": 0.95,
        }

        return DomainMatchScore(
            original_s1=original_s1,
            original_s2=original_s2,
            processed_s1=processed_s1,
            processed_s2=processed_s2,
            scores=scores,
        )

    def test_creation(self, match_score):
        """Test creating a MatchResult instance."""
        result = MatchResult(match_score, True)
        assert result.score_details == match_score
        assert result.is_match is True
        assert result.match_reasons == []

    def test_add_reason(self, match_score):
        """Test adding a reason to MatchResult."""
        result = MatchResult(match_score, True)
        result.add_reason("High token set ratio similarity")
        result.add_reason("Phonetic match")

        assert len(result.match_reasons) == 2
        assert "High token set ratio similarity" in result.match_reasons
        assert "Phonetic match" in result.match_reasons


class TestDomainEntityProfile:
    """Tests for the DomainEntityProfile class."""

    def test_creation(self):
        """Test creating a DomainEntityProfile instance."""
        entity = DomainEntityProfile(
            entity_id="E001",
            primary_name=DomainEntityName("Apple Inc."),
            alternate_names=[
                DomainEntityName("Apple Incorporated"),
                DomainEntityName("Apple Computer"),
            ],
            attributes={"industry": "Technology", "founded": 1976},
        )

        assert entity.entity_id == "E001"
        assert entity.primary_name.raw_value == "Apple Inc."
        assert len(entity.alternate_names) == 2
        assert entity.alternate_names[0].raw_value == "Apple Incorporated"
        assert entity.alternate_names[1].raw_value == "Apple Computer"
        assert entity.attributes["industry"] == "Technology"
        assert entity.attributes["founded"] == 1976
        assert len(entity.relationships) == 0

    def test_add_alternate_name(self):
        """Test adding an alternate name to an entity."""
        entity = DomainEntityProfile(
            entity_id="E001", primary_name=DomainEntityName("Apple Inc."), alternate_names=[]
        )

        # Add alternate name
        entity.add_alternate_name(DomainEntityName("Apple Incorporated"))

        # Verify
        assert len(entity.alternate_names) == 1
        assert entity.alternate_names[0].raw_value == "Apple Incorporated"

    def test_add_duplicate_alternate_name(self):
        """Test that adding a duplicate alternate name is ignored."""
        entity = DomainEntityProfile(
            entity_id="E001",
            primary_name=DomainEntityName("Apple Inc."),
            alternate_names=[DomainEntityName("Apple Incorporated")],
        )

        # Add duplicate alternate name
        entity.add_alternate_name(DomainEntityName("Apple Incorporated"))

        # Verify
        assert len(entity.alternate_names) == 1

    def test_add_primary_as_alternate_name(self):
        """Test that adding the primary name as an alternate name is ignored."""
        entity = DomainEntityProfile(
            entity_id="E001", primary_name=DomainEntityName("Apple Inc."), alternate_names=[]
        )

        # Add primary name as alternate
        entity.add_alternate_name(DomainEntityName("Apple Inc."))

        # Verify
        assert len(entity.alternate_names) == 0

    def test_add_attribute(self):
        """Test adding an attribute to an entity."""
        entity = DomainEntityProfile(
            entity_id="E001", primary_name=DomainEntityName("Apple Inc."), attributes={}
        )

        # Add attribute
        entity.add_attribute("industry", "Technology")

        # Verify
        assert "industry" in entity.attributes
        assert entity.attributes["industry"] == "Technology"

    def test_update_attribute(self):
        """Test updating an existing attribute."""
        entity = DomainEntityProfile(
            entity_id="E001",
            primary_name=DomainEntityName("Apple Inc."),
            attributes={"industry": "Consumer Electronics"},
        )

        # Update attribute
        entity.add_attribute("industry", "Technology")

        # Verify
        assert entity.attributes["industry"] == "Technology"

    def test_add_relationship(self):
        """Test adding a relationship to an entity."""
        entity = DomainEntityProfile(entity_id="E001", primary_name=DomainEntityName("Apple Inc."))

        # Add relationship
        entity.add_relationship("subsidiary", "E002")

        # Verify
        assert "subsidiary" in entity.relationships
        assert "E002" in entity.relationships["subsidiary"]

    def test_add_duplicate_relationship(self):
        """Test that adding a duplicate relationship is ignored."""
        entity = DomainEntityProfile(entity_id="E001", primary_name=DomainEntityName("Apple Inc."))

        # Add relationship
        entity.add_relationship("subsidiary", "E002")

        # Add duplicate relationship
        entity.add_relationship("subsidiary", "E002")

        # Verify
        assert "subsidiary" in entity.relationships
        assert len(entity.relationships["subsidiary"]) == 1

    def test_multiple_relationships_same_type(self):
        """Test adding multiple relationships of the same type."""
        entity = DomainEntityProfile(entity_id="E001", primary_name=DomainEntityName("Apple Inc."))

        # Add relationships
        entity.add_relationship("subsidiary", "E002")
        entity.add_relationship("subsidiary", "E003")

        # Verify
        assert "subsidiary" in entity.relationships
        assert len(entity.relationships["subsidiary"]) == 2
        assert "E002" in entity.relationships["subsidiary"]
        assert "E003" in entity.relationships["subsidiary"]


class TestMatchCandidate:
    """Tests for the MatchCandidate class."""

    def test_creation(self):
        """Test creating a MatchCandidate instance."""
        entity_name = DomainEntityName("Apple Inc.")
        processed_name = DomainProcessedName(entity_name, "apple inc")

        candidate = MatchCandidate(
            entity_name=entity_name, processed_entity_name=processed_name, score=0.95
        )

        assert candidate.entity_name == entity_name
        assert candidate.processed_entity_name == processed_name
        assert candidate.score == 0.95

    def test_comparison(self):
        """Test comparison of MatchCandidate instances based on score."""
        candidate1 = MatchCandidate(
            entity_name=DomainEntityName("Apple Inc."),
            processed_entity_name=DomainProcessedName(DomainEntityName("Apple Inc."), "apple inc"),
            score=0.95,
        )

        candidate2 = MatchCandidate(
            entity_name=DomainEntityName("Microsoft Corp"),
            processed_entity_name=DomainProcessedName(
                DomainEntityName("Microsoft Corp"), "microsoft corp"
            ),
            score=0.85,
        )

        candidate3 = MatchCandidate(
            entity_name=DomainEntityName("Google LLC"),
            processed_entity_name=DomainProcessedName(DomainEntityName("Google LLC"), "google llc"),
            score=0.75,
        )

        # Higher score should come first when sorted
        candidates = [candidate1, candidate2, candidate3]
        sorted_candidates = sorted(candidates)

        assert sorted_candidates[0] == candidate1
        assert sorted_candidates[1] == candidate2
        assert sorted_candidates[2] == candidate3

        # Test direct comparison
        assert candidate1 < candidate2
        assert candidate2 < candidate3
        assert not (candidate1 > candidate2)

    def test_immutability(self):
        """Test that MatchCandidate is immutable."""
        candidate = MatchCandidate(
            entity_name=DomainEntityName("Apple Inc."),
            processed_entity_name=DomainProcessedName(DomainEntityName("Apple Inc."), "apple inc"),
            score=0.95,
        )

        with pytest.raises(AttributeError):
            candidate.score = 0.8

        with pytest.raises(AttributeError):
            candidate.entity_name = DomainEntityName("New")
