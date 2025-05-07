# Architecture

This document describes the architecture of the Fuzzy Matcher library.

## Overview

Fuzzy Matcher follows a clean architecture approach with clear separation of concerns. The main architectural principles are:

1. **Dependency Inversion**: High-level modules do not depend on low-level modules. Both depend on abstractions.
2. **Interface Segregation**: Clients depend only on the interfaces they use.
3. **Single Responsibility**: Each component has a single responsibility.
4. **Open/Closed**: Components are open for extension but closed for modification.

## Architectural Layers

The codebase is organized into the following layers:

### 1. Protocols Layer (`fuzzy_matcher/protocols/`)

This layer defines the contracts (interfaces) that components in other layers must implement. It contains:

- Protocol definitions using Python's `Protocol` type
- Type hints and documentation for the expected behavior
- Abstract methods that must be implemented by concrete classes

Key protocols include:
- `StringPreprocessor`: Interface for string preprocessing components
- `MatchingAlgorithm`: Interface for string similarity algorithms
- `PhoneticEncoder`: Interface for phonetic encoding algorithms
- `EntityName`: Interface for entity name representations
- `EntityProfile`: Interface for entity profile representations
- `EntityRepository`: Interface for entity storage and retrieval

### 2. Domain Layer (`fuzzy_matcher/domain/`)

This layer contains the core business logic and domain entities. It includes:

- Domain models representing the core concepts
- Business rules and logic
- Value objects and entities

Key components include:
- `DomainEntityName`: Implementation of the `EntityName` protocol
- `DomainProcessedName`: Representation of a processed name
- `DomainEntityProfile`: Implementation of the `EntityProfile` protocol
- `MatchResult`: Representation of a match result
- `MatchCandidate`: Representation of a potential match

### 3. Infrastructure Layer (`fuzzy_matcher/infrastructure/`)

This layer provides concrete implementations of the interfaces defined in the protocols layer. It includes:

- Algorithm implementations
- Preprocessing implementations
- Repository implementations

Key components include:
- `StandardStringPreprocessor`: String preprocessing with a chain of responsibility
- Various algorithm implementations (Levenshtein, Jaro-Winkler, etc.)
- Phonetic encoders (Soundex, Metaphone)
- `InMemoryEntityRepository`: In-memory implementation of the entity repository

### 4. Application Layer (`fuzzy_matcher/application/`)

This layer provides higher-level services and facades that compose the components from other layers. It includes:

- Services that coordinate multiple components
- Facades that provide a simplified interface to clients

Key components include:
- `ComprehensiveMatchScorer`: Service for calculating match scores across algorithms
- `ConfigurableMatchDecisionStrategy`: Strategy for deciding if strings match
- `EntityResolverService`: Service for resolving entities from candidates
- `EntityResolutionFacade`: Facade providing a simplified API for client code

## Component Interactions

The main interactions between components are:

1. **String Preprocessing**:
   - Chain of responsibility pattern with multiple preprocessing steps
   - Each step normalizes the string in a specific way
   - Steps include lowercase conversion, accent removal, whitespace normalization, etc.

2. **String Matching**:
   - Multiple algorithms calculate similarity scores
   - Comprehensive scorer aggregates scores from different algorithms
   - Match decision strategy determines if strings match based on scores

3. **Entity Resolution**:
   - Entity resolver finds potential matches for a query
   - Repository provides candidate entities using phonetic indexing
   - Resolution selects the best match based on similarity scores

## Design Patterns

The codebase uses several design patterns:

1. **Chain of Responsibility**: Used in the string preprocessor to apply multiple steps sequentially.
2. **Strategy**: Used for match decision and algorithm selection.
3. **Repository**: Used for entity storage and retrieval.
4. **Facade**: Used to provide a simplified interface to clients.
5. **Factory**: Used to create instances of components.
6. **Value Object**: Used for immutable domain entities.

## Dependency Injection

The architecture uses dependency injection to maintain loose coupling:

- Components receive their dependencies through constructors
- Default implementations are provided for convenience
- Clients can provide custom implementations to change behavior

For example, the `EntityResolutionFacade` allows clients to inject custom preprocessors, algorithms, and repositories.

## Extension Points

The library provides several extension points:

1. **Custom Preprocessing Steps**: New preprocessing steps can be added by implementing the `PreprocessingStep` protocol.
2. **Custom Matching Algorithms**: New algorithms can be added by implementing the `MatchingAlgorithm` protocol.
3. **Custom Phonetic Encoders**: New encoders can be added by implementing the `PhoneticEncoder` protocol.
4. **Custom Repository Implementations**: Alternative storage mechanisms can be implemented via the `EntityRepository` protocol.
5. **Custom Match Decision Strategies**: New strategies can be implemented via the `MatchDecisionStrategy` protocol.
