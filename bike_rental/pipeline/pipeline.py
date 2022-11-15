from bike_rental.config.configuration import Configuration
from bike_rental.entity.artifact_entity import*
from bike_rental.component.data_ingestion import DataIngestion
from bike_rental.exception import BikeRentExcep
import sys



class Pipeline():

    def __init__(self, config: Configuration) -> None:

        self.config = config
        
    
    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise BikeRentExcep(e, sys) from e


    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
        except Exception as e:
            raise BikeRentExcep(e,sys) from e