"""Infrastructure implementations for the fuzzy matching system."""

from fuzzy_matcher.infrastructure.algorithms import (
    DamerauLevenshteinAlgorithm,
    JaroWinklerAlgorithm,
    LevenshteinAlgorithm,
    MetaphoneEncoder,
    PartialRatioAlgorithm,
    SoundexEncoder,
    TokenSetRatioAlgorithm,
    TokenSortRatioAlgorithm,
    WeightedRatioAlgorithm,
    get_default_phonetic_encoders,
    get_default_similarity_algorithms,
)
from fuzzy_matcher.infrastructure.preprocessors import (
    AccentRemovalStep,
    CompanySuffixStandardizationStep,
    LowercaseStep,
    PreprocessingStep,
    PunctuationRemovalStep,
    StandardStringPreprocessor,
    TypeConversionStep,
    WhitespaceNormalizationStep,
)
from fuzzy_matcher.infrastructure.repositories import InMemoryEntityRepository

__all__ = [
    # Algorithms
    "DamerauLevenshteinAlgorithm",
    "JaroWinklerAlgorithm",
    "LevenshteinAlgorithm",
    "MetaphoneEncoder",
    "PartialRatioAlgorithm",
    "SoundexEncoder",
    "TokenSetRatioAlgorithm",
    "TokenSortRatioAlgorithm",
    "WeightedRatioAlgorithm",
    "get_default_phonetic_encoders",
    "get_default_similarity_algorithms",
    # Preprocessors
    "AccentRemovalStep",
    "CompanySuffixStandardizationStep",
    "LowercaseStep",
    "PreprocessingStep",
    "PunctuationRemovalStep",
    "StandardStringPreprocessor",
    "TypeConversionStep",
    "WhitespaceNormalizationStep",
    # Repositories
    "InMemoryEntityRepository",
]
