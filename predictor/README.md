# SmartShelf Predictor

ML prediction models for SmartShelf inventory optimization.

## Features
- Risk classification using XGBoost
- Time series prediction with Prophet
- Recommendation engine for inventory actions

## Installation
```
uv pip install --editable .
```

## Usage
```python
from predictor.src.models.risk_classifier import treinar_modelo_risco
from predictor.src.models.time_series import treinar_modelo_tempo_vencimento
from predictor.src.models.recommender import avaliar_risco_estoque
``` 