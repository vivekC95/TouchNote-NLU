# -*- coding: utf-8 -*-
"""
Created on Mon July 4 22:07:43 2022

@author: vivek chatterjee
"""

#from mysql import connector
import pymysql 
from sqlalchemy import create_engine
import numpy as np
import pandas as pd

class DBOps():
    
    def __init__(self,data_frame = None,host = '',username = '',password = '',port = '',database = ''):
        """
        The DBOps object takes a dataframe and inserts data into the db. 
        While Initiating the object, always use a dataframe instead of a None Object.
        
        """
        self.host = host
        self.user = username
        self.password = password
        self.port = port
        self.db = database
        self.data = data_frame
        
        # creating an engine for sql_alchemy:
        try:
            self.engine = create_engine("mysql+pymysql://{un}:{p}@{h}:{pt}/{db}".format(
                un = self.user, 
                p = self.password,
                h = self.host,
                pt = self.port,
                db = self.db
                ))
            print("...")
            print("engine setup to: ",self.db )
            
        except:
            print("...")
            print("cannot setup an engine for db: ",self.db)
            
        finally:
            print('connecting to engine: ...')
        
        raise
            
        # connect to engine:
        self.conn_flag = 0
        try:
            self.conn = self.engine.connect()
            self.conn_flag = 1 
        except:
            print('connection error.')
            
        
    
    def read_data(self,query = ''):
        """ Takes SQL query as an argument and returns a Data Frame."""
        
        if self.conn_flag == 1:
            data = pd.read_sql( sql = query , con = self.conn)
            return data 
        else:
            print('error in connecting to db.')
            return None
    
    
    def write_data_from_frame(self,tableName = '',chunks = 100,method_ = 'append'):
        """ writes data to database"""
        if self.conn_flag == 1:
            try:
                self.data.to_sql(name=tableName, con=self.conn, if_exists=method_,chunksize=chunks,index=False,method='multi');
            except ValueError as vx:
                print(vx)
            except Exception as ex:   
                print(ex)
            except NameError as nx:
                print(nx)
            else:
                print("Table {t} created successfully.".format( t = tableName))
        else:
            print('error in connecting to db.')
            
    def execute_CRUD(self,query=''):
        """ Executes Create, Update and Delete Statements."""
        
        config = {"host": self.host,
                  "database": self.db,
                  "user":self.user,    
                  "port":self.port,
                  "password":self.password}
        
        try:
            connection = self.engine.connect(**config)
            cursor = connection.cursor()
            cursor.execute(query)
            print('Executed the following statement: ')
            print(' ')
            print(query)
        except:
            print('Failed to execute the following statement: ')
            print(' ')
            print(query)            
    
    @staticmethod       # Ignore.
    def _validate():    # --------------
        pass            # Not Required.
    