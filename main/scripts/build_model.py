
import os
from libs.ml.custom_nlu import nlu_driver
from joblib import dump
import pyarrow.parquet as pq


data = pq.read_table('./data/featurized_data.parquet').to_pandas()
nlu = nlu_driver(data)
nlu.trainModel()
dump(nlu,'./data/model.pkl')


