# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 09:08:56 2022

@author: vivekc
"""

from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import pandas_gbq as gq

class big_query():
    
    def __init__(self,service_account_ = None,PROJECT_ID='',DATA_SET_ID='',REGION='',TABLE_ID=''):
        ''' This is a Big Query Connector Module which will be used for CRUD and DB Operations.
            Following Settings are to be provided:
                1. Service Account File
                2. Project ID
                3. Data Set ID
                4. Region
                5. Table ID
            Class Methods used in this module:
                1.export_csv_to_table - For exporting csv file to table in Big Query
                2.read_data - Read data from BigQuery into a dataframe.
                3.execute_query - To be used for DDL and DML Statements.'''
                
        # Class Global Variables -
        self._service_account_ = service_account_
        self.pid = PROJECT_ID
        self.dsid = DATA_SET_ID
        self.region_ = REGION
        self.tid = TABLE_ID
        self.cred = None
        self.client = None
        try:
            self.cred = Credentials.from_service_account_file(self._service_account_) # Loads valid JSON service account else throws error.
            self.client = bigquery.Client(project=self.pid,credentials=self.cred)  # Creates BQ Client object. Only works with valid settings else throws error.
            print('Big Query Connection Successful.')
        except:
            raise
            print('Failed to initialize. Check above error to know more.')
        
    def export_csv_to_table(self,file=None,source_format = 'csv',header = 1, method = 'kill_fill'):
        ''' Exports CSV file to table. As of now, kill fill and csv file input is the only option.
            Only input the file path to use this method.'''
        
        if file == None:
            print('Failed. No CSV file were given as input.')
        else:
            # Create Job Config-
            try:
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows = 1,
                    autodetect = True,
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE #This is the method to define kill-fill.
                    )
            except:
                raise
                
            print('Attempting Ingestion...')
            
            try:
                with open(file,"rb") as csv_file:
                    job = self.client.load_table_from_file(file_obj = csv_file, destination = self.tid, job_config=job_config)
                    job.result()
            except:
                raise
                
            print('Export Stats: ')
            
            try:
                table = self.client.get_table(self.tid)
                print( "Row Ingested: ",table.num_rows )
                print( "Column Ingested: ",len(table.schema) )
                print('Export Successful!')
                del csv_file
            except:
                raise
            
                
    def read_data_to_df(self,query = ''):
        ''' This uses Pandas-GBQ to load data quickly from BigQuery.'''
        df = gq.read_gbq(query_or_table=query,project_id=self.pid,credentials=self.cred)
        return df
       
    def execute_query(self,query = ''):
        ''' Use only for DDL and DML'''
        self.client.execute_query(query)
            
            
                
                
                
                
            
        