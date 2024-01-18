import numpy as np
import pytest
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from autoemulate.emulators import MODEL_REGISTRY
from autoemulate.model_processing import check_model_names
from autoemulate.model_processing import get_models
from autoemulate.model_processing import turn_models_into_multioutput
from autoemulate.model_processing import wrap_models_in_pipeline


# -----------------------test getting models-------------------#
def test_get_models():
    models = get_models(MODEL_REGISTRY)
    assert isinstance(models, list)
    model_names = [type(model).__name__ for model in models]
    assert all([model_name in MODEL_REGISTRY for model_name in model_names])


def test_check_model_names():
    models = get_models(MODEL_REGISTRY)
    model_names = [type(model).__name__ for model in models]
    with pytest.raises(ValueError):
        check_model_names(["NotInRegistry"], MODEL_REGISTRY)
    check_model_names(model_names, MODEL_REGISTRY)


def test_get_models_subset():
    models = get_models(
        MODEL_REGISTRY, model_subset=["GaussianProcessSk", "RandomForest"]
    )
    assert len(models) == 2
    model_names = [type(model).__name__ for model in models]
    assert all([model_name in MODEL_REGISTRY for model_name in model_names])


# -----------------------test turning models into multioutput-------------------#
def test_turn_models_into_multioutput():
    models = get_models(MODEL_REGISTRY)
    y = np.array([[1, 2], [3, 4]])
    models = turn_models_into_multioutput(models, y)
    assert isinstance(models, list)
    # check that non-native multioutput models are wrapped in MultiOutputRegressor
    assert all(
        [
            isinstance(model, MultiOutputRegressor)
            for model in models
            if not model._more_tags().get("multioutput")
        ]
    )


# -----------------------test wrapping models in pipeline-------------------#
def test_wrap_models_in_pipeline_no_scaler():
    models = get_models(MODEL_REGISTRY)
    models = wrap_models_in_pipeline(models, scale=False, scaler=StandardScaler())
    assert isinstance(models, list)
    assert all([isinstance(model, Pipeline) for model in models])
    # assert that pipeline does have a scaler as first step
    assert all([model.steps[0][0] != "scaler" for model in models])


def test_wrap_models_in_pipeline_scaler():
    models = get_models(MODEL_REGISTRY)
    models = wrap_models_in_pipeline(models, scale=True, scaler=StandardScaler())
    assert isinstance(models, list)
    assert all([isinstance(model, Pipeline) for model in models])
    # assert that pipeline does have a scaler as first step
    assert all([model.steps[0][0] == "scaler" for model in models])
