"""String preprocessing implementations for the fuzzy matching system.

This module implements the StringPreprocessor protocol from fuzzy_matcher.protocols.interfaces
using a chain of responsibility pattern to process strings in multiple steps.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional

from unidecode import unidecode

from fuzzy_matcher.protocols.interfaces import StringOrNumeric, StringPreprocessor


class PreprocessingStep(ABC):
    """Abstract base class for preprocessing steps (Chain of Responsibility pattern).

    This class defines the interface for preprocessing steps and implements
    the chain of responsibility pattern to process strings through multiple steps.

    Attributes
    ----------
        _next_step: The next preprocessing step in the chain

    """

    def __init__(self, next_step: Optional["PreprocessingStep"] = None):
        """Initialize a preprocessing step.

        Args:
        ----
            next_step: The next preprocessing step in the chain

        """
        self._next_step = next_step

    def process(self, text: str) -> str:
        """Process text through this step and the rest of the chain.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Processed text after passing through this step and subsequent steps

        """
        result = self._execute(text)
        if self._next_step:
            return self._next_step.process(result)
        return result

    @abstractmethod
    def _execute(self, text: str) -> str:
        """Execute the specific preprocessing logic for this step.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Processed text after this step

        """
        pass


class TypeConversionStep(PreprocessingStep):
    """Converts input to string. This should be the first step in a chain.

    This step handles conversion from any input type to string to ensure
    subsequent steps receive string input.
    """

    def _execute(self, text: str) -> str:
        """Convert input to string.

        Args:
        ----
            text: The text to convert (already string in this implementation)

        Returns:
        -------
            String representation of the input

        """
        return str(text)


class AccentRemovalStep(PreprocessingStep):
    """Removes accents from text using unidecode."""

    def _execute(self, text: str) -> str:
        """Remove accents from text.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Text with accents removed

        """
        return unidecode(text)


class LowercaseStep(PreprocessingStep):
    """Converts text to lowercase."""

    def _execute(self, text: str) -> str:
        """Convert text to lowercase.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Lowercase text

        """
        return text.lower()


class CompanySuffixStandardizationStep(PreprocessingStep):
    """Standardizes company suffixes in text.

    This step standardizes various company suffixes (e.g., Corporation, Inc., Ltd.)
    to a consistent format to improve matching between entities with different
    suffix representations.
    """

    def __init__(self, next_step: Optional[PreprocessingStep] = None):
        """Initialize the company suffix standardization step.

        Args:
        ----
            next_step: The next preprocessing step in the chain

        """
        super().__init__(next_step)
        # Order matters: e.g., "p.l.c." before "plc" if "plc" is a substring of the replacement
        self.suffix_mapping = {
            # Common corporation variations
            r"\bcorporation\b": "corp",
            r"\bcorp\b": "corp",
            r"\bcorp\.\b": "corp",
            # Incorporated variations
            r"\bincorporated\b": "inc",
            r"\binc\b": "inc",
            r"\binc\.\b": "inc",
            # Limited variations
            r"\blimited\b": "ltd",
            r"\bltd\b": "ltd",
            r"\bltd\.\b": "ltd",
            # Company variations
            r"\bcompany\b": "co",
            r"\bco\b": "co",
            r"\bco\.\b": "co",
            # PLC variations
            r"\bpublic limited company\b": "plc",
            r"\bp\.l\.c\.\b": "plc",
            r"\bplc\b": "plc",
            # LLC variations
            r"\blimited liability company\b": "llc",
            r"\bl\.l\.c\.\b": "llc",
            r"\bllc\b": "llc",
            # Other common variations
            r"\bsociete anonyme\b": "sa",
            r"\bs\.a\.\b": "sa",
            r"\bsa\b": "sa",
            r"\bsociété anonyme\b": "sa",  # Added with accent
            r"\baktiengesellschaft\b": "ag",
            r"\ba\.g\.\b": "ag",
            r"\bag\b": "ag",
            r"\bgmbh\b": "gmbh",
            r"\bgmbh & co\. kg\b": "gmbh",
            r"\bholdings?\b": "hldg",
            r"\bhldg\b": "hldg",
            r"\bhldg\.\b": "hldg",
            r"\bgroup\b": "grp",
            r"\bgrp\b": "grp",
            r"\bgrp\.\b": "grp",
        }

    def _execute(self, text: str) -> str:
        """Standardize company suffixes in text.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Text with standardized company suffixes

        """
        processed_text = text
        for pattern, replacement in self.suffix_mapping.items():
            processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)
        return processed_text


class PunctuationRemovalStep(PreprocessingStep):
    """Removes punctuation from text."""

    def _execute(self, text: str) -> str:
        """Remove punctuation from text.

        First removes specific punctuation (periods and commas), then
        removes all remaining non-alphanumeric/whitespace characters.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Text with punctuation removed

        """
        # Remove periods and commas specifically, then general non-alphanumeric/whitespace
        # This order can matter if some punctuation is part of suffixes handled earlier
        text_no_specific_punct = text.replace(".", "").replace(",", "")
        # Removes all remaining punctuation, keeps letters, numbers, and whitespace
        return re.sub(r"[^\w\s]", "", text_no_specific_punct)


class WhitespaceNormalizationStep(PreprocessingStep):
    """Normalizes whitespace in text."""

    def _execute(self, text: str) -> str:
        """Normalize whitespace in text.

        Replaces multiple consecutive whitespace characters with a single space
        and trims leading/trailing whitespace.

        Args:
        ----
            text: The text to process

        Returns:
        -------
            Text with normalized whitespace

        """
        return re.sub(r"\s+", " ", text).strip()


class StandardStringPreprocessor(StringPreprocessor):
    """Standard implementation of string preprocessor using chain of responsibility.

    This class implements the StringPreprocessor protocol, creating a chain of
    preprocessing steps that text passes through.
    """

    def __init__(self) -> None:
        """Initialize the standard string preprocessor.

        Creates a chain of preprocessing steps in the desired order.
        """
        # Define the chain of preprocessing steps in desired order
        # Last step in definition is first in execution path if thinking backwards
        step1 = WhitespaceNormalizationStep()
        step2 = PunctuationRemovalStep(step1)
        step3 = CompanySuffixStandardizationStep(step2)
        step4 = LowercaseStep(step3)
        self._chain_head = AccentRemovalStep(step4)  # First step to execute after type conversion

    def preprocess(self, text: StringOrNumeric) -> str:
        """Preprocess input string to standardized form.

        Args:
        ----
            text: Input text to preprocess

        Returns:
        -------
            Preprocessed string in standardized form

        """
        if text is None:  # Handle None input explicitly
            return ""

        # Initial type conversion
        str_text: str = str(text) if not isinstance(text, str) else text

        if not str_text.strip():  # Handle empty or whitespace-only strings
            return ""

        return self._chain_head.process(str_text)
