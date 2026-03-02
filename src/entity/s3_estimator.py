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
            logging.info(f"[DEBUG] Proj1Estimator.__init__() called with bucket_name='{bucket_name}', model_path='{model_path}'")
            self.bucket_name = bucket_name
            self.model_path = model_path
            self.model = None  # Lazy load on demand
            logging.info(f"[DEBUG] Proj1Estimator initialized (lazy loading enabled)")
        except Exception as e:
            logging.error(f"[DEBUG] Error in __init__: {e}")
            raise MyException(e, sys) from e

    def is_model_present(self, model_path: str = None) -> bool:
        """Check if model exists locally or in S3 without loading it."""
        path = model_path or self.model_path
        try:
            logging.info(f"[DEBUG] is_model_present() checking for: {path}")
            
            # Check local path first
            if os.path.exists(path):
                logging.info(f"[DEBUG] Model found at local path: {path}")
                return True
            
            logging.info(f"[DEBUG] No local file. Checking S3...")
            # Check S3
            s3_service = SimpleStorageService()
            is_available = s3_service.s3_key_path_available(
                bucket_name=self.bucket_name,
                s3_key=path
            )
            if is_available:
                logging.info(f"[DEBUG] Model found in S3 bucket {self.bucket_name} at key {path}")
                return True
            
            logging.info(f"[DEBUG] Model not found: local path {path} or S3 {self.bucket_name}/{path}")
            return False
        except Exception as e:
            logging.warning(f"[DEBUG] Error checking model presence: {type(e).__name__}: {e}")
            return False

    def _load_model(self) -> Any:
        """Load model from local path or S3 with fallback."""
        try:
            logging.info(f"[DEBUG] _load_model() called with bucket_name={self.bucket_name}, model_path={self.model_path}")
            
            # Try local path first
            logging.info(f"[DEBUG] Checking local path: {self.model_path}")
            if os.path.exists(self.model_path):
                logging.info(f"[DEBUG] Local file found! Loading from: {self.model_path}")
                return load_object(file_path=self.model_path)
            else:
                logging.info(f"[DEBUG] Local file NOT found at: {self.model_path}")
            
            # Fallback to S3
            logging.info(f"[DEBUG] Local model not found. Attempting S3 download...")
            logging.info(f"[DEBUG] S3 Details: bucket='{self.bucket_name}', key='{self.model_path}'")
            
            try:
                s3_service = SimpleStorageService()
                logging.info(f"[DEBUG] SimpleStorageService initialized successfully")
            except Exception as e:
                logging.error(f"[DEBUG] Failed to initialize SimpleStorageService: {e}")
                raise
            
            # Use model_path directly as the S3 key
            logging.info(f"[DEBUG] Attempting to get_file_object from S3...")
            try:
                model_file = s3_service.get_file_object(
                    filename=self.model_path,
                    bucket_name=self.bucket_name
                )
                logging.info(f"[DEBUG] Successfully retrieved file object from S3")
            except Exception as e:
                logging.error(f"[DEBUG] Failed to get_file_object from S3: {type(e).__name__}: {e}")
                raise
            
            logging.info(f"[DEBUG] Reading model object from S3...")
            try:
                model_obj = s3_service.read_object(model_file, decode=False)
                logging.info(f"[DEBUG] Successfully read model object")
            except Exception as e:
                logging.error(f"[DEBUG] Failed to read_object: {type(e).__name__}: {e}")
                raise
            
            logging.info(f"[DEBUG] Unpickling model...")
            import pickle
            try:
                model = pickle.loads(model_obj)
                logging.info(f"[DEBUG] Successfully unpickled model from S3: s3://{self.bucket_name}/{self.model_path}")
            except Exception as e:
                logging.error(f"[DEBUG] Failed to unpickle: {type(e).__name__}: {e}")
                raise
            
            return model
            
        except ClientError as e:
            logging.error(f"[DEBUG] ClientError (AWS S3 error): {e.response['Error']['Code']}")
            if e.response['Error']['Code'] == '404':
                raise MyException(
                    f"Model not found in S3 bucket '{self.bucket_name}' at key '{self.model_path}'. "
                    f"Ensure the model has been trained and pushed to S3. "
                    f"Check AWS credentials are set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION",
                    sys,
                ) from e
            raise MyException(
                f"AWS S3 error: {e}. Bucket: {self.bucket_name}, Key: {self.model_path}",
                sys,
            ) from e
        except Exception as e:
            logging.error(f"[DEBUG] Unexpected error type {type(e).__name__}: {e}")
            raise MyException(
                f"Error loading model from local path '{self.model_path}' or S3 's3://{self.bucket_name}/{self.model_path}': {e}. "
                f"Check: (1) Local artifact exists, (2) AWS credentials set, (3) Model uploaded to S3",
                sys,
            ) from e

    def predict(self, dataframe):
        """Make prediction using the model (lazy load on first call)."""
        try:
            logging.info(f"[DEBUG] predict() called")
            if self.model is None:
                logging.info(f"[DEBUG] Model not yet loaded, loading now...")
                self.model = self._load_model()
                logging.info(f"[DEBUG] Model loaded successfully, performing prediction")
            else:
                logging.info(f"[DEBUG] Model already loaded, performing prediction")
            
            logging.info("Performing prediction using loaded model")
            return self.model.predict(dataframe)
        except Exception as e:
            logging.error(f"[DEBUG] Error in predict(): {type(e).__name__}: {e}")
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
