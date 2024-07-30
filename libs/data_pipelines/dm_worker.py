import requests as req 
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
from libs.connectors import mysql
import json
import os

class ScrapeDataCard():

    def __init__(self,url):
        '''This module takes in the URL: https://www.123greetings.com/.
        Once the object is initiated, the classmethod RUN() can be used to
        start the web-scraping.
        Result: Creates CSV Delta Files in the Data Folder.'''
        # Class Variables
        self.url_ = url
        self.site_response = req.get(self.url_)
        self.site_html = BeautifulSoup(self.site_response.text)



    @staticmethod
    def convertToUrl(sequence):
        '''This method converts strings to url format strings.'''
        for i in range(0,len(sequence)):
            sequence[i] = sequence[i].lower()
            sequence[i] = sequence[i].replace(' ','_')
        return sequence


    def getCategoryAttributes(self):
        menu_features = self.site_html.find('ul',attrs={'class':'menu-pri'})
        category = [x.text for x in menu_features.find_all('li')]
        category = category[:-1] + [x for x in category[-1].split('\n') if x != '']
        category = self.convertToUrl(category)

        # Qualifying Categories Selection.
        dict_200 = {}
        for cat in category:
            cat_url  = self.url_ + '/' + cat + '/'
            test_req = req.get(cat_url)
            print(cat_url,test_req.status_code)
            dict_200.update({cat:test_req.status_code})
        qualified_cats = [x for x in category if dict_200[x] == 200]
        
        # Qualifying Sub-Categories.
        sub_cats = {} # Sub-Category initation data structures.
        for cat in category:
            cat_url  = self.url_ + '/' + cat + '/'
            sub_level_ = req.get(cat_url)
            sub_level_html = BeautifulSoup(sub_level_.text)
            print(type(sub_level_html))
            sub_cat_html = sub_level_html.find_all('h2',{'class':re.compile("^gdr")})
            sub_cats.update({cat:[x.text.split('(')[0].strip().lower().replace(' ','_') for x in sub_cat_html]})
        
        sb_dict_200 = {} # Sub-Categories Qualification starts from here.
        for k,v in sub_cats.items(): 
            for j in v:
                cats_url = self.url_ + '/' + k + '/' + j + '/'
                response = req.get(cats_url)
                print(cats_url,response.status_code)
                if response.status_code == 200:
                    sb_dict_200.update({j:response.status_code})
                else:
                    pass
        keys = sub_cats.keys()
        values = sub_cats.values()
        t = sub_cats.values()
        qualified_sub_cats = {k:v for (k,v) in zip(keys,values) if k in [x for x in [item for sublist in t for item in sublist]]}
        with open('E://TouchNote//settings//DM_Cats.json','w') as file:
            json.dump(qualified_sub_cats,file)
        return qualified_sub_cats


    def RUN(self):
        # Check if JSON File Exists:
        try:
            sub_cats = json.loads(open('.\settings\DM_Cats.json','r').read())
        except:
            sub_cats = self.getCategoryAttributes()
        # Start Web-Scraping from Here:
        i = 1
        for k,v in sub_cats.items():
            for j in v:
                cats_url = self.url_ + '/' + k + '/' + j + '/'
                response = req.get(cats_url,cookies={"IDE":"AHWqTUmZhLX_zduEJhNst2t-QFkt5-xJUnvng0-pQf8VRA5yEHWO0p9McqkNluwWGK8"},
                            headers={'User-Agent':'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320'})
                print('-'*100)
                try:
                    response_html = BeautifulSoup(response.text)
                    card_text = [x.text for x in [x.find_all('p',{'class':'std'}) for x in response_html.find_all('ul',id = 'div_thumbs')][0]]
                    card_img = ['https:' + x['src'] for x in [x.find_all('img') for x in response_html.find_all('ul',id = 'div_thumbs')][0]]
                    df = pd.DataFrame({'card_text':card_text,'card_img':card_img,'category':k,'sub_category':j})
                    print(df)
                    path = './data/dm_dump_part_' + str(i) +'.csv'
                    df.to_csv(path)
                    i += 1
                    del df
                except:
                    print(cats_url + ' Response: ',response.status_code)
                print('-'*100)
                time.sleep(2)

if __name__ == '__main__':
    scd = ScrapeDataCard('https://www.123greetings.com')
    scd.RUN()





