from bike_rental.pipeline.pipeline import Pipeline
from bike_rental.config.configuration import Configuration
from bike_rental.exception import BikeRentExcep
import sys

def main():
    try:
        #Testing data ingestion
        pipeline = Pipeline(Configuration())
        pipeline.run_pipeline()

    except Exception as e:
        raise BikeRentExcep(e,sys) from e

      
if __name__ == "__main__":
    main()