from msilib.schema import Error
import pandas as pd
import pyarrow
import fastparquet
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
import json
import yaml
import pyarrow.parquet as pq
import decimal

class Featurize():

    def __init__(self,force = False):
        '''This class checks if there is data dumps avaialable from dm_worker.py
        and collates data to a parquet file for faster access.
        If a parquet file is found, this worker will fail gracefully and exit it's operation.'''
        self.test = None
        self.force_ = force
        try:
            self.test = pq.read_table('./data/featurized_data.parquet')
            if self.force_ == False:
                print('Parquet File Found! Use force = True to overwrite.')
            else:
                pass
        except:
            print('Parquet File not found, proceeding to conversion...')
            pass
        
        # Edge-Case: if parquet file is corrupted--
        if self.test is not None:
            self.test = self.test.to_pandas()
            if self.test.shape[0] == 0:
                print('Parquet File is blank')
                try:
                    self.test = self.test[['intent','word_tokens']]
                except:
                    raise
        else:
            pass

    def readDataDumps(self):
        if self.force_:
            i = 1
            final_data = pd.DataFrame()
            while True:
                try:
                    data = pd.read_csv('./data/dm_dump_part_'+str(i)+'.csv', index_col=0)
                    final_data = pd.concat([final_data,data])
                except FileNotFoundError:
                    if i == 1:
                        print('Although force = True is given, there is no data dump available.')
                        raise
                    else:
                        break
                i += 1
        print('Data Dumps read Successfully!')
        return final_data
        
    def processIntentFeatures(self,final_data):
        final_data['card_name'] = ''
        final_data['intent'] = final_data['category'] + '_' + final_data['sub_category']
        final_data.reset_index(drop=True,inplace=True)
        cats = []
        sub_cats = []
        index = 1
        for row in range(0,final_data.shape[0]):
            if final_data['category'][row] in cats:
                if final_data['sub_category'][row] in sub_cats:
                    index += 1
                    final_data['card_name'][row] = final_data['intent'][row] + '_' + str(index)
                else:
                    index = 1
                    final_data['card_name'][row] = final_data['intent'][row] + '_' + str(index)
                    sub_cats.append(final_data['sub_category'][row])
            elif final_data['sub_category'][row] in sub_cats:  # Handling Edge-Cases for similar sub-category in different category
                index = 1
                final_data['card_name'][row] = final_data['intent'][row] + '_' + str(index)
            else:
                cats.append(final_data['category'][row])
                final_data['card_name'][row] = final_data['intent'][row] + '_' + str(index)
            return final_data
        
    def exportToParquet(self,final_data):
        if self.force_:
            # Export Data to Parquet:
            final_data.to_parquet('./data/featurized_data.parquet',engine='fastparquet')
            i = 1
            while True:
                try:
                    os.remove('./data/dm_dump_part_'+str(i)+'.csv')
                except:
                    break
                i += 1


if __name__ == '__main__':
    ff = Featurize(force=True)
    data = ff.readDataDumps()
    data_intent = ff.processIntentFeatures(data)
    ff.exportToParquet(data_intent)
    del data
    del data_intent
    del ff


        

