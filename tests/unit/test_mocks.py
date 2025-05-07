"""Tests using mock objects for external dependencies."""

from unittest.mock import MagicMock, Mock, patch

from fuzzy_matcher.application.facades import EntityResolutionFacade
from fuzzy_matcher.application.services import (
    ComprehensiveMatchScorer,
)
from fuzzy_matcher.domain.entities import (
    DomainEntityName,
    DomainEntityProfile,
)
from fuzzy_matcher.protocols.interfaces import (
    EntityRepository,
    MatchingAlgorithm,
    PhoneticEncoder,
    StringPreprocessor,
)


class TestMockedDependencies:
    """Tests using mock objects for external dependencies."""

    def test_preprocessor_mocking(self):
        """Test using a mocked preprocessor."""
        # Create a mock preprocessor
        mock_preprocessor = Mock(spec=StringPreprocessor)
        mock_preprocessor.preprocess.return_value = "mock_processed"

        # Create a service using the mock
        scorer = ComprehensiveMatchScorer(mock_preprocessor, {}, {})

        # Use the service
        scorer.calculate_scores("Test1", "Test2")

        # Verify the mock was called correctly
        assert mock_preprocessor.preprocess.call_count == 2
        mock_preprocessor.preprocess.assert_any_call("Test1")
        mock_preprocessor.preprocess.assert_any_call("Test2")

    def test_algorithm_mocking(self):
        """Test using a mocked similarity algorithm."""
        # Create a mock algorithm
        mock_algorithm = Mock(spec=MatchingAlgorithm)
        mock_algorithm.name = "mock_algorithm"
        mock_algorithm.calculate_similarity.return_value = 0.75

        # Create a real preprocessor
        preprocessor = Mock(spec=StringPreprocessor)
        preprocessor.preprocess.side_effect = lambda x: x.lower()

        # Create a scorer with the mock algorithm
        scorer = ComprehensiveMatchScorer(preprocessor, {"mock_algorithm": mock_algorithm}, {})

        # Use the service
        scores = scorer.calculate_scores("Test1", "Test2")

        # Verify the mock was called correctly
        mock_algorithm.calculate_similarity.assert_called_once_with("test1", "test2")
        assert scores.get_score("mock_algorithm") == 0.75

    def test_encoder_mocking(self):
        """Test using a mocked phonetic encoder."""
        # Create a mock encoder
        mock_encoder = Mock(spec=PhoneticEncoder)
        mock_encoder.name = "mock_encoder"
        mock_encoder.encode.return_value = "M000"

        # Create a real preprocessor
        preprocessor = Mock(spec=StringPreprocessor)
        preprocessor.preprocess.side_effect = lambda x: x.lower()

        # Create a scorer with the mock encoder
        scorer = ComprehensiveMatchScorer(preprocessor, {}, {"mock_encoder": mock_encoder})

        # Use the service
        scores = scorer.calculate_scores("Test1", "Test2")

        # Verify the mock was called correctly
        assert mock_encoder.encode.call_count == 2
        mock_encoder.encode.assert_any_call("test1")
        mock_encoder.encode.assert_any_call("test2")
        assert scores.get_score("mock_encoder_s1") == "M000"
        assert scores.get_score("mock_encoder_s2") == "M000"

    def test_repository_mocking(self):
        """Test using a mocked entity repository."""
        # Create a mock repository
        mock_repository = Mock(spec=EntityRepository)

        # Mock return value for find_by_primary_name
        test_entity = DomainEntityProfile(
            entity_id="E001", primary_name=DomainEntityName("Test Entity"), alternate_names=[]
        )
        mock_repository.find_by_primary_name.return_value = test_entity

        # Create a facade with the mock repository
        facade = EntityResolutionFacade(repository=mock_repository)

        # Use the facade
        entity = facade.find_by_name("Test Entity")

        # Verify the mock was called and the entity was returned
        mock_repository.find_by_primary_name.assert_called_once()
        assert entity is test_entity

    @patch("fuzzy_matcher.application.services.ComprehensiveMatchScorer")
    def test_patching_services(self, mock_scorer_class):
        """Test patching a class with unittest.mock.patch."""
        # Configure the mock scorer
        mock_scorer = MagicMock()
        mock_scorer_class.return_value = mock_scorer

        # Mock the evaluate_match method to return a specific result
        mock_match_result = MagicMock()
        mock_match_result.is_match = True
        mock_match_result.match_reasons = ["Mocked reason"]
        mock_match_result.score_details.get_score.return_value = 0.99
        mock_match_result.score_details.processed_s1.processed_value = "processed_s1"
        mock_match_result.score_details.processed_s2.processed_value = "processed_s2"

        # Configure the strategy to return our mock result
        with patch(
            "fuzzy_matcher.application.services.ConfigurableMatchDecisionStrategy.evaluate_match"
        ) as mock_evaluate:
            mock_evaluate.return_value = mock_match_result

            # Create a facade (which will use our patched classes)
            facade = EntityResolutionFacade()

            # Use the facade
            result = facade.compare_strings("s1", "s2")

            # Verify the patched method was called
            mock_evaluate.assert_called_once_with("s1", "s2")

            # Verify the result contains our mocked data
            assert result["is_match"] is True
            assert "Mocked reason" in result["match_reasons"]
