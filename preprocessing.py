# importing modules
import os
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))


# extracting only relevant keywords from a given text
def get_relevant_words(text):
    # removing hyperlinks, unicode characters and next line character
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    text = text.replace('\n', ' ')
    text = text.replace('\\"', '')
    words = re.findall(r'\b\w+\b', text)
    relevant_words = [word.lower() for word in words]
    
    # removing stop words
    processed_text = ' '.join(relevant_words)
    word_tokens = word_tokenize(processed_text)
    res = [w for w in word_tokens if not w.lower() in stop_words]
    res = [w for w in res if len(w) > 1]
    
    return list(dict.fromkeys(res))


# preprocessing the given video data to remove redundant entities
def preprocess():
    input_directory_path = 'video_data'
    output_directory_path = 'preprocessed_data'

    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)

    for filepath in os.listdir(input_directory_path):
        if os.path.exists(os.path.join(output_directory_path, filepath)):
            continue
        file = open(os.path.join(input_directory_path, filepath))
        print(f'preprocessing file: {filepath}')
        data = json.load(file)
        
        required_data = {}
        required_data['videoId'] = data['videoInfo']['id']
        required_data['channelId'] = data['videoInfo']['snippet']['channelId']
        required_data['title'] = data['videoInfo']['snippet']['title']
        required_data['channelTitle'] = data['videoInfo']['snippet']['channelTitle']
        required_data['description'] = data['videoInfo']['snippet']['description']
        required_data['thumbnails'] = data['videoInfo']['snippet']['thumbnails']
        
        try:
            required_data['tags'] = data['videoInfo']['snippet']['tags']
        except:
            required_data['tags'] = []
        
        required_data['categoryId'] = int(data['videoInfo']['snippet']['categoryId'])

        required_data['viewCount'] = int(data['videoInfo']['statistics']['viewCount'])
        required_data['likeCount'] = int(data['videoInfo']['statistics']['likeCount'])
        required_data['dislikeCount'] = int(data['videoInfo']['statistics']['dislikeCount'])

        tags = []
        for tag in required_data['tags']:
            taglist = tag.split()
            for t in taglist:
                tags.append(t)
        tagstring = ' '.join(tags)

        relevantKeywordsList = get_relevant_words(data['videoInfo']['snippet']['title']) \
            + get_relevant_words(data['videoInfo']['snippet']['channelTitle']) \
            + get_relevant_words(data['videoInfo']['snippet']['description']) \
            + get_relevant_words(' '.join(tagstring))
        required_data['relevantKeywords'] = list(dict.fromkeys(relevantKeywordsList))

        with open(os.path.join(output_directory_path, os.path.basename(filepath)), 'w') as outfile:
            json.dump(required_data, outfile, indent=4)

        file.close()


# main function
if __name__ == '__main__':
    preprocess()