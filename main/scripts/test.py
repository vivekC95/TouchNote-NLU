from joblib import load

model = load('./data/model.pkl')

x = model.predProb('I want to gift a card to my dog')
print(x)