import os
import sys
from typing import Any, Optional

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import load_object, save_object
from src.cloud_storage.aws_storage import SimpleStorageService
from botocore.exceptions import ClientError


class Proj1Estimator:
    """Estimator loader with local and S3 fallback support.
    
    Loads a serialized model from local path or S3 bucket.
    On first initialization, model is optional (lazy loading).
    """

    def __init__(self, bucket_name: str, model_path: str) -> None:
        try:
            self.bucket_name = bucket_name
            self.model_path = model_path
            self.model = None  # Lazy load on demand
        except Exception as e:
            raise MyException(e, sys) from e

    def is_model_present(self, model_path: str = None) -> bool:
        """Check if model exists locally or in S3 without loading it."""
        path = model_path or self.model_path
        try:
            # Check local path first
            if os.path.exists(path):
                logging.info(f"Model found at local path: {path}")
                return True
            
            # Check S3
            s3_service = SimpleStorageService()
            is_available = s3_service.s3_key_path_available(
                bucket_name=self.bucket_name,
                s3_key=path
            )
            if is_available:
                logging.info(f"Model found in S3 bucket {self.bucket_name} at key {path}")
                return True
            
            logging.info(f"Model not found: local path {path} or S3 {self.bucket_name}/{path}")
            return False
        except Exception as e:
            logging.warning(f"Error checking model presence: {e}")
            return False

    def _load_model(self) -> Any:
        """Load model from local path or S3 with fallback."""
        try:
            # Try local path first
            if os.path.exists(self.model_path):
                logging.info(f"Loading model from local path: {self.model_path}")
                return load_object(file_path=self.model_path)
            
            # Fallback to S3
            logging.info(f"Local model not found. Attempting S3 download from {self.bucket_name}/{self.model_path}")
            s3_service = SimpleStorageService()
            model = s3_service.load_model(
                model_name=os.path.basename(self.model_path),
                bucket_name=self.bucket_name,
                model_dir=os.path.dirname(self.model_path) or None
            )
            logging.info(f"Successfully loaded model from S3")
            return model
            
        except ClientError as e:
            raise MyException(
                f"Failed to load model from S3: {e}. Model file not found at {self.model_path}.",
                sys,
            ) from e
        except Exception as e:
            raise MyException(
                f"Error loading model from {self.model_path}: {e}",
                sys,
            ) from e

    def predict(self, dataframe):
        """Make prediction using the model (lazy load on first call)."""
        try:
            if self.model is None:
                logging.info("Model not yet loaded, loading now...")
                self.model = self._load_model()
            
            logging.info("Performing prediction using loaded model")
            return self.model.predict(dataframe)
        except Exception as e:
            raise MyException(e, sys) from e
    
    def save_model(self, from_file: str) -> None:
        """Upload model from local path to S3."""
        try:
            logging.info(f"Uploading model from {from_file} to S3")
            s3_service = SimpleStorageService()
            s3_service.upload_file(
                from_filename=from_file,
                to_filename=self.model_path,
                bucket_name=self.bucket_name,
                remove=False  # Keep local copy
            )
            logging.info(f"Successfully uploaded model to S3: {self.bucket_name}/{self.model_path}")
        except Exception as e:
            raise MyException(f"Failed to upload model to S3: {e}", sys) from e
