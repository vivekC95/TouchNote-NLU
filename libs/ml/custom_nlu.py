import pandas as pd
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import ast
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score, classification_report
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import pyarrow.parquet as pq

class nlu_driver():

    def __init__(self,data,re_train = False):
        '''
        nlu_driver is a custom NLU-Based, Intent Classification ML model, which uses greetings/post/appreciation/invite card data to train and classify intent extracted from text given by the user.

        Usage:

        # Instantiate the class object
        nlu = nlu_driver(data = <dataframe_object>)
        x = nlu.trainModel()
        x.predProb(<text_object>) # outputs multiple intents defined in taxonomy and their probabilities.

        More Functionalities-
        Custom sklearn functionalities can be explicitly added to the instance in the manner given below:
        
        from sklearn.xxxx import xxxx

        <custom_label_encoder> = LabelEncoder(<args>)
        ....
        <custom_sklearn_model_with_hyper_parameters> = sklearn.Ensemble/SVC/... #any sklearn model...


        nlu = nlu_driver(data = <dataframe_object>)
        nlu.labelencoder = <custom_label_encoder>
        nlu.lemmatizer = <custom_lemmatizer>
        nlu.tfidf = <custom_tfidf_vectorizer>
        nlu.count_vect = <custom_count_vectorizer>
        nlu.tfidf_transformer = <custom_tfidf_transformer>
        nlu.model = <custom_sklearn_model_with_hyper_parameters>


        nlu_driver also allows to re-train the model when newer intent data is avaialable for training, which in result, over-writes the pickle file.
        While re-training the model, instantiate this class with re_train = True.'''
        self.train_data_ = None
        self.categories_ = None
        self.clf_ = None
        self.cr_ = None
        self.data_ = data
        self.labelencoder = LabelEncoder()
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = stopwords.words('english')
        self.tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1,3), stop_words=self.stopwords)
        self.count_vect = CountVectorizer()
        self.tfidf_transformer = TfidfTransformer()
        self.model = SVC(kernel='linear',probability=True,degree=3,decision_function_shape='ovr',break_ties=False,C=1.0,gamma='auto')

    def sort_dict(self,dict_ = {}):
        sorted_keys = sorted(dict_, key=dict_.get, reverse=True)
        final_dict = {}
        for r in sorted_keys:
            final_dict.update({r: dict_[r]})
        return final_dict

    def tokenizeText(self):
        self.data_['word_tokens'] = None
        for row in range(0,self.data_.shape[0]):
            self.data_['word_tokens'][row] = [y for y in [x for x in word_tokenize(self.data_['card_text'][row])] if y not in self.stopwords]
    
    
    def categorySchema(self):
        self.categories_ = pd.DataFrame(self.train_data_.intent.unique(),
        self.train_data_.intent_code.unique()).reset_index(drop=False).rename(columns = {'index':'intent_code',0:'intent'}).sort_values('intent_code',ascending=True).reset_index(drop=True)


    def trainModel(self):
        print('Started Training...')
        try:
            self.tokenizeText()
            self.train_data_ = self.data_[['intent','word_tokens']]
            self.train_data_['intent_code'] = self.labelencoder.fit_transform(self.train_data_['intent'])
            self.train_data_['word_tokens'] = self.train_data_['word_tokens'].apply(lambda y:' '.join([self.lemmatizer.lemmatize(x) for x in y if x.isalpha() == True]))
            # features = self.tfidf.fit_transform(self.train_data_.word_tokens).toarray()
            # labels = self.train_data_.intent_code
            self.categorySchema()
            X_train, X_test, y_train, y_test = train_test_split(self.train_data_['word_tokens'], self.train_data_['intent_code'], random_state = 0)
            X_train_counts = self.count_vect.fit_transform(X_train)
            X_train_tfidf = self.tfidf_transformer.fit_transform(X_train_counts)
            self.clf_ = OneVsRestClassifier(self.model).fit(X_train_tfidf, y_train)
            y_pred = self.clf_.predict(self.count_vect.transform(X_test))
            test_data = pd.DataFrame({'predictions':y_pred,'true':y_test.values})
            test_data = test_data.reset_index().rename(columns={'index':'intent_code'})
            test_data = pd.merge(self.train_data_[['intent','intent_code']],test_data,how='inner',on='intent_code').set_index('intent').drop('intent_code',axis=1)
            self.cr_ = classification_report(test_data['true'],test_data['predictions'])
            print('Completed Training of the model...')
            print('-'*100)
            print('Model Performance: ')
            print(self.cr_)
        except:
            print('An error occured while training the model...')
            raise

    def predProb(self,input_ = ''):
        in_ = input_
        results = self.clf_.predict_proba(self.count_vect.transform([in_]))
        result = pd.DataFrame(self.sort_dict([dict(zip(self.clf_.classes_, cs)) for cs in results][0]),index=[0]).T.rename(columns={0:'confidence'}).reset_index(drop=False).rename(columns={'index':'intent_code'})
        json = pd.merge(result,self.categories_,how='inner',on='intent_code')[['intent','confidence']].to_json(orient='values')
        return {k:v for (k,v) in ast.literal_eval(json)}
    
if __name__ == '__main__':
    data = pq.read_table('./data/featurized_data.parquet').to_pandas()
    nlu = nlu_driver(data)
    nlu.trainModel()
    print(nlu.predProb('I want to gift a card to my granddaughter.'))
    print(nlu.predProb('I want to gift a card to my wife at her wedding.'))





