# Using Natural Language Understanding to Solve for Product, ML and Content Optimization Problem.

# Objective:
1. To solve the cold-start problem for any user by reinforcing affinity upon extracting intent from the user.
2. To solve for content discoverability problem, where a particular content or item, gets less engagement/sales as it’s age increases.
3. To solve for Customer Onboarding Journey and reduce drop-off from the same journey. Also, to reduce the time to first purchase by a significant amount.

# Methodology:
First, in order to extract intent, there has to be an ML model that can recognize intent. Due to which, a taxonomy on a domain specific definition is required. Once the taxonomy is created, the same is used for setting rules for data mining and related data are scraped from different sources to a DB or High-Throughput I/O filesystem. 

Featurization is divided into 2 parts:
1. Create Dumps of CSV from scraped data.
2. Ingestion of the chunk csv to a parquet file.

Once, Featurization is complete and data is stored in parquet, it is then moved towards another module where machine learning is used to train on the named-entities to create a intent-classification model. Further, the model is saved as a pickle file using  JobLib which is also another High-Throughput I/O File Handler.

Post training and pickling of model, it is served as a REST API using Flask and can be integrated into frontend as shown in the code.

The entire structure is summarized in the workflow shown below:

![image](https://github.com/user-attachments/assets/fde4f853-546d-4c5a-aad1-79238ed737a6)


# Future Implementations:
Using RASA NLU to create bots that can serve as assistance to the customer with the power of NLU especially with strong stories and actions. Thus Driving Retention and also help users to identify product features and usability if they are lost in a page, causing to solve for gratification and better building up of user-segmentation like power-users,network users etc. 
