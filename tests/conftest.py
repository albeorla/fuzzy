"""Common fixtures for pytest across the test suite."""

import pytest

from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.domain.entities import (
    DomainEntityName,
    DomainEntityProfile,
    DomainProcessedName,
)
from fuzzy_matcher.infrastructure.algorithms import (
    JaroWinklerAlgorithm,
    LevenshteinAlgorithm,
    MetaphoneEncoder,
    SoundexEncoder,
    TokenSetRatioAlgorithm,
)
from fuzzy_matcher.infrastructure.preprocessors import StandardStringPreprocessor
from fuzzy_matcher.infrastructure.repositories import InMemoryEntityRepository


@pytest.fixture()
def preprocessor():
    """Return a standard string preprocessor."""
    return StandardStringPreprocessor()


@pytest.fixture()
def entity_name():
    """Return a sample entity name."""
    return DomainEntityName("Apple Inc.")


@pytest.fixture()
def processed_name(entity_name, preprocessor):
    """Return a sample processed name."""
    processed = preprocessor.preprocess(entity_name.raw_value)
    return DomainProcessedName(entity_name, processed)


@pytest.fixture()
def entity_names():
    """Return a list of sample entity names."""
    return [
        DomainEntityName("Apple Inc."),
        DomainEntityName("Apple Incorporated"),
        DomainEntityName("Microsoft Corporation"),
        DomainEntityName("IBM"),
        DomainEntityName("International Business Machines"),
        DomainEntityName("Google LLC"),
    ]


@pytest.fixture()
def entity_profile():
    """Return a sample entity profile."""
    return DomainEntityProfile(
        entity_id="E001",
        primary_name=DomainEntityName("Apple Inc."),
        alternate_names=[
            DomainEntityName("Apple Incorporated"),
            DomainEntityName("Apple Computer"),
        ],
        attributes={"industry": "Technology", "founded": 1976},
    )


@pytest.fixture()
def entity_repository(preprocessor):
    """Return an in-memory entity repository with test data."""
    repo = InMemoryEntityRepository(preprocessor)

    # Add some test entities
    apple = DomainEntityProfile(
        entity_id="E001",
        primary_name=DomainEntityName("Apple Inc."),
        alternate_names=[
            DomainEntityName("Apple Incorporated"),
            DomainEntityName("Apple Computer"),
        ],
        attributes={"industry": "Technology", "founded": 1976},
    )

    microsoft = DomainEntityProfile(
        entity_id="E002",
        primary_name=DomainEntityName("Microsoft Corporation"),
        alternate_names=[DomainEntityName("Microsoft Corp"), DomainEntityName("MSFT")],
        attributes={"industry": "Technology", "founded": 1975},
    )

    ibm = DomainEntityProfile(
        entity_id="E003",
        primary_name=DomainEntityName("International Business Machines"),
        alternate_names=[DomainEntityName("IBM"), DomainEntityName("IBM Corporation")],
        attributes={"industry": "Technology", "founded": 1911},
    )

    # Save entities to the repository
    repo.save(apple)
    repo.save(microsoft)
    repo.save(ibm)

    return repo


@pytest.fixture()
def levenshtein_algorithm():
    """Return a Levenshtein algorithm instance."""
    return LevenshteinAlgorithm()


@pytest.fixture()
def jaro_winkler_algorithm():
    """Return a Jaro-Winkler algorithm instance."""
    return JaroWinklerAlgorithm()


@pytest.fixture()
def token_set_algorithm():
    """Return a Token Set Ratio algorithm instance."""
    return TokenSetRatioAlgorithm()


@pytest.fixture()
def soundex_encoder():
    """Return a Soundex encoder instance."""
    return SoundexEncoder()


@pytest.fixture()
def metaphone_encoder():
    """Return a Metaphone encoder instance."""
    return MetaphoneEncoder()


@pytest.fixture()
def facade():
    """Return an EntityResolutionFacade instance."""
    return EntityResolutionFacade()


@pytest.fixture()
def populated_facade(entity_repository):
    """Return an EntityResolutionFacade instance with pre-populated data."""
    facade = EntityResolutionFacade(repository=entity_repository)
    return facade
