import os
import sys

import numpy as np
import pandas as pd
from six.moves import urllib
from sklearn.model_selection import StratifiedShuffleSplit

from bike_rental.entity.artifact_entity import DataIngestionArtifact
from bike_rental.entity.config_entity import DataIngestionConfig
from bike_rental.exception import BikeRentExcep
from bike_rental.logger import logging


class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'='*20}Data Ingestion log started.{'='*20} ")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise BikeRentExcep(e,sys)


    def download_bikerental_data(self) -> str:
        try:
            
             #extracting remote url to download dataset
            download_url = self.data_ingestion_config.dataset_download_url

            #folder loacation to download file
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)

            os.makedirs(raw_data_dir,exist_ok=True)

            
            #Getting file name from url
            bikerental_file_name = os.path.basename(download_url)

            #complete file path
            raw_file_path = os.path.join(raw_data_dir,bikerental_file_name)
            
            logging.info(f"Downloading file from : [{download_url}] into : [{raw_file_path}]")
            #downloading file
            urllib.request.urlretrieve(download_url, raw_file_path)
            logging.info(f"File :[{raw_file_path}] has been downloaded successfully")
            return raw_file_path
        except Exception as e:
            raise BikeRentExcep(sys,e) from e


    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            file_name = os.listdir(raw_data_dir)[0]

            bikerental_file_path = os.path.join(raw_data_dir, file_name)

            logging.info(f"Reading csv file: [{bikerental_file_path}]")
            bikerental_data_frame = pd.read_csv(bikerental_file_path)

            bikerental_data_frame["mnth_cat"] = pd.cut(
                bikerental_data_frame["mnth"],
                bins = [0,3,6,9,12],
                labels=[1,2,3,4]   
)
            
            logging.info(f"Spliting data into train and test")
            strat_train_set = None
            strat_test_set = None

            #StratifiedShuffleSplit splits data in to train and test having same statistal distribution 
            strat_split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

            for train_index,test_index in strat_split.split(bikerental_data_frame, bikerental_data_frame["mnth_cat"]):
                strat_train_set = bikerental_data_frame.loc[train_index].drop(["mnth_cat"],axis = 1)
                strat_test_set = bikerental_data_frame.loc[test_index].drop(["mnth_cat"],axis = 1)


            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir, file_name)
            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir, file_name)


            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir, exist_ok=True)
                logging.info(f"Exporting training dataset to file : [{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)

            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok=True)
                logging.info(f"Exporting test dataset to file : [{test_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)

            
            data_ingestion_artifact = DataIngestionArtifact(
                                        train_file_path=train_file_path,
                                        test_file_path=test_file_path,
                                        is_ingested=True,
                                        message= f"Data ingestion completed successfully"
                                        )
            logging.info(f"Data ingestion artifacat: [{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise BikeRentExcep(e,sys) from e


    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            raw_file_path =  self.download_bikerental_data()
            return self.split_data_as_train_test()
        except Exception as e:
            raise BikeRentExcep(e,sys) from e
    

    def __del__(self):
        logging.info(f"{'='*20}Data Ingestion log completed.{'='*20} \n \n")