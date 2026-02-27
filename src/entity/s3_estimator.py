import os
import sys
from typing import Any

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import load_object


class Proj1Estimator:
    """Minimal estimator loader used by the prediction pipeline.

    It attempts to load a serialized model from a local path (`model_path`).
    If the file is not present, it raises a clear error (S3 download support
    is not implemented here).
    """

    def __init__(self, bucket_name: str, model_path: str) -> None:
        try:
            self.bucket_name = bucket_name
            self.model_path = model_path
            self.model = self._load_model()
        except Exception as e:
            raise MyException(e, sys) from e

    def _load_model(self) -> Any:
        try:
            if os.path.exists(self.model_path):
                logging.info(f"Loading model from local path: {self.model_path}")
                return load_object(file_path=self.model_path)
            else:
                raise MyException(
                    f"Model file not found at path: {self.model_path}.\nProvide a valid local path or implement S3 download.",
                    sys,
                )
        except Exception as e:
            raise MyException(e, sys) from e

    def predict(self, dataframe):
        try:
            logging.info("Performing prediction using loaded model")
            return self.model.predict(dataframe)
        except Exception as e:
            raise MyException(e, sys) from e
