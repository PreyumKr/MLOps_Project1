import sys
from src.exception import MyException
from src.logger import logging

from src.components.data_ingestion import DataIngestion
# from src.components.data_validation import DataValidation
# from src.components.data_transformation import DataTransformation
# from src.components.model_trainer import ModelTrainer
# from src.components.model_evaluation import ModelEvaluation
# from src.components.model_pusher import ModelPusher

from src.entity.config_entity import DataIngestionConfig
# from src.entity.config_entity import DataValidationConfig
# from src.entity.config_entity import DataTransformationConfig
# from src.entity.config_entity import ModelTrainerConfig
# from src.entity.config_entity import ModelEvaluationConfig
# from src.entity.config_entity import ModelPusherConfig

from src.entity.artifact_entity import DataIngestionArtifact
# from src.entity.artifact_entity import DataValidationArtifact
# from src.entity.artifact_entity import DataTransformationArtifact
# from src.entity.artifact_entity import ModelTrainerArtifact
# from src.entity.artifact_entity import ModelEvaluationArtifact
# from src.entity.artifact_entity import ModelPusherArtifact

class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info(f"{'>>'*5} Starting data ingestion {'<<'*5}")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"{'>>'*5} Completed data ingestion {'<<'*5}")
            return data_ingestion_artifact
        except Exception as e:
            raise MyException(e, sys) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            # data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            # data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            # model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            # model_evaluation_artifact = self.start_model_evaluation(model_trainer_artifact=model_trainer_artifact)
            # if not model_evaluation_artifact.is_model_accepted:
            #     logging.info("Trained model rejected.")
            #     return
            # model_pusher_artifact = self.start_model_pusher(model_evaluation_artifact=model_evaluation_artifact)
        except Exception as e:
            raise MyException(e, sys) from e