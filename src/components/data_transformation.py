import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import read_yaml_file, save_numpy_array, save_object


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig) -> None:
        try:
            logging.info(f"{'>>'*5} Data Transformation {'<<'*5}")
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise MyException(e, sys)
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)
        
    def get_data_transformer_object(self) -> Pipeline:
        try:
            numeric_transformer = StandardScaler()
            min_max_scaler = MinMaxScaler()
            num_features = self._schema_config["num_features"]
            mm_columns = self._schema_config["mm_columns"]

            preprocessor = ColumnTransformer(
                transformers=[
                    ("StandardScaler", numeric_transformer, num_features),
                    ("MinMaxScaler", min_max_scaler, mm_columns)
                ], remainder="passthrough")

            final_pipeline = Pipeline(steps=[("preprocessor", preprocessor)])
            return final_pipeline
        except Exception as e:
            raise MyException(e, sys)
        
    def _map_gender_column(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0}).astype(int)
            return df
        except Exception as e:
            raise MyException(e, sys)
    
    def _create_dummy_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = pd.get_dummies(df, drop_first=True)
            return df
        except Exception as e:
            raise MyException(e, sys)
        
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.rename(columns={
                "Vehicle_Age_< 1 Year": "Vehicle_Age_lt_1_Year",
                "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years"
            })
            for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
                if col in df.columns:
                    df[col] = df[col].astype(int)
            return df
        except Exception as e:
            raise MyException(e, sys)
        
    def _drop_id_column(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            drop_col = self._schema_config["drop_columns"]
            if drop_col in df.columns:
                df = df.drop(columns=[drop_col])
            return df
        except Exception as e:
            raise MyException(e, sys)
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Reading training and testing data")
            train_df = DataTransformation.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = DataTransformation.read_data(self.data_ingestion_artifact.test_file_path)

            logging.info("Mapping gender column")
            train_df = self._map_gender_column(train_df)
            test_df = self._map_gender_column(test_df)  
            
            logging.info("Creating dummy columns")
            train_df = self._create_dummy_columns(train_df)
            test_df = self._create_dummy_columns(test_df)

            logging.info("Renaming columns")
            train_df = self._rename_columns(train_df)
            test_df = self._rename_columns(test_df)

            logging.info("Dropping id column")
            train_df = self._drop_id_column(train_df)
            test_df = self._drop_id_column(test_df)

            logging.info("Getting data transformer object")
            data_transformer_object = self.get_data_transformer_object()

            logging.info("Transforming training data")
            train_features = data_transformer_object.fit_transform(train_df.drop(columns=[TARGET_COLUMN]))
            train_target = train_df[TARGET_COLUMN]

            logging.info("Transforming testing data")
            test_features = data_transformer_object.transform(test_df.drop(columns=[TARGET_COLUMN]))
            test_target = test_df[TARGET_COLUMN]

            logging.info("Applying SMOTEENN to training data only (no resampling of test set)")
            # Apply SMOTEENN to handle class imbalance ONLY on training data to avoid test leakage
            try:
                smt = SMOTEENN(sampling_strategy="minority")
                train_features_resampled, train_target_resampled = smt.fit_resample(train_features, train_target)
                # Do NOT resample the test set; keep it unchanged for valid evaluation
                test_features_resampled, test_target_resampled = test_features, test_target
            except Exception:
                # if resampling fails, fall back to original training arrays
                train_features_resampled, train_target_resampled = train_features, train_target
                test_features_resampled, test_target_resampled = test_features, test_target

            # concatenate features and target for saving
            train_arr = np.c_[train_features_resampled, np.array(train_target_resampled)]
            test_arr = np.c_[test_features_resampled, np.array(test_target_resampled)]

            # save preprocessing object and transformed arrays
            save_object(file_path=self.data_transformation_config.transformed_object_file_path, obj=data_transformer_object)
            save_numpy_array(file_path=self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array(file_path=self.data_transformation_config.transformed_test_file_path, array=test_arr)

            # build and return artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact

        except Exception as e:
            raise MyException(e, sys)