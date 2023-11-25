import re
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from nltk.corpus import stopwords
import joblib

data = pd.read_csv("Twitter_Data.csv", names=["text", "sentiment"], header=None)
data = data.iloc[1:, :]
data.dropna(inplace=True)

def remove_tags(raw_text):
    cleaned_text = re.sub(re.compile('<.*?>'), '', raw_text)
    return cleaned_text


data['text'] = data['text'].astype('str')
data['text'] = data['text'].apply(remove_tags)


data['text'] = data['text'].apply(lambda text: text.lower())


english_stopwords = set(stopwords.words('english'))
data['text'] = data['text'].apply(lambda x: ' '.join([item for item in x.split() if item not in english_stopwords]))


X = data['text']
y = data['sentiment']
y[y == -1] = 0
y[y == 0] = 1
y[y == 1] = 2
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)


text_clf = Pipeline([
    ('vect', CountVectorizer(ngram_range=(1, 2), max_features=5000)),
    ('clf', RandomForestClassifier())
])


start_time = time.time()
text_clf.fit(X_train, y_train)
print("Training time: %s seconds" % (time.time() - start_time))


y_pred = text_clf.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
joblib.dump(text_clf, 'sentiment_analysis_pipeline.joblib')