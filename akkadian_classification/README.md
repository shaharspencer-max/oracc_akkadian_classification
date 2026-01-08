# Akkadian Classification - Clean Architecture

This directory contains a refactored, production-ready implementation with proper separation of concerns.

## Architecture

```
akkadian_classification/
├── services/       # Business logic and orchestration
├── repositories/   # Data access layer (ORACC, CDLI, CSV)
├── models/         # Domain models and dataclasses
└── utils/          # Shared utilities
```

## Design Principles

- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Inversion**: Services depend on repository interfaces, not implementations
- **Testability**: Clean architecture makes unit testing straightforward
- **Type Safety**: Uses Python type hints and dataclasses throughout

## Usage Example

```python
from akkadian_classification.repositories import ORACCRepository
from akkadian_classification.services import TextClassificationService
from akkadian_classification.models import AkkadianText

# Initialize repository
oracc_repo = ORACCRepository(base_path="path/to/parsed_results")

# Load text
text = oracc_repo.get_text(project="rinap-rinap1", text_id="Q003414")

# Classify
classifier = TextClassificationService()
result = classifier.classify(text)

print(f"Predicted city: {result.predicted_city}")
```

## Migration from `src/`

The experimental code in `src/` is preserved as-is for reference.
This clean implementation extracts patterns and conventions from that research code.
