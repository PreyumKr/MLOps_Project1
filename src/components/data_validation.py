import json
import sys 
import os

import pandas as pd
from pandas import DataFrame

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import read_yaml_file
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.entity.config_entity import DataValidationConfig
from src.constants import SCHEMA_FILE_PATH


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig) -> None:
        try:
            logging.info(f"{'>>'*5} Data Validation {'<<'*5}")
            self.data_ingestion_artifact = data_ingestion_artifact  
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise MyException(e, sys)

    def validate_data(self, dataframe: DataFrame) -> bool:
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])
            return status
        except Exception as e:
            raise MyException(e, sys)

    def is_column_exist(self, df: DataFrame) -> bool:
        try:
            # Extract column names from schema (list of dicts)
            schema_columns = [list(col.keys())[0] for col in self._schema_config["columns"]]
            dataframe_columns = df.columns.to_list()
            for column in schema_columns:
                if column not in dataframe_columns:
                    logging.info(f"Column: [{column}] is not present in dataframe")
                    return False
            return True
        except Exception as e:
            raise MyException(e, sys)
        
    @staticmethod
    def read_data(file_path: str) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logging.info("Reading training and testing file")
            train_df = DataValidation.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = DataValidation.read_data(self.data_ingestion_artifact.test_file_path)

            logging.info("Validating training and testing data")
            train_status = self.validate_data(train_df)
            test_status = self.validate_data(test_df)

            if not train_status:
                raise Exception("Training data does not have all the columns")
            
            if not test_status:
                raise Exception("Testing data does not have all the columns")

            column_status_train = self.is_column_exist(train_df)
            column_status_test = self.is_column_exist(test_df)

            if not column_status_train:
                raise Exception("Training data does not have all the columns")
            
            if not column_status_test:
                raise Exception("Testing data does not have all the columns")

            data_validation_artifact = DataValidationArtifact(
                validation_status=True,
                message="Data Validation completed successfully",
                validation_report_file_path=self.data_validation_config.report_file_path
            )

            # Ensure report directory exists and write validation report
            try:
                report_dir = os.path.dirname(self.data_validation_config.report_file_path)
                os.makedirs(report_dir, exist_ok=True)
                report_content = {
                    "validation_status": data_validation_artifact.validation_status,
                    "message": data_validation_artifact.message
                }
                with open(self.data_validation_config.report_file_path, "w") as f:
                    json.dump(report_content, f, indent=4)
                logging.info(f"Validation report saved at: {self.data_validation_config.report_file_path}")
            except Exception as e:
                logging.info(f"Failed to write validation report: {e}")

            logging.info(f"Data Validation Artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise MyException(e, sys)