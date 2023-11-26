# importing modules
import os
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from youtube_transcript_api import YouTubeTranscriptApi 

stop_words = set(stopwords.words('english'))


# fetching captions for the video with the given video id
def get_captions(video_id):
    try:
        srt = YouTubeTranscriptApi.get_transcript(f"{video_id}")
        caption = " ".join([content['text'] for content in srt])
        caption = re.sub(r'\[.*?\]', '', caption)
        caption = caption.lower().strip()
        caption = " ".join([word for word in caption.split() if word not in stop_words])
    except:
        caption = ""
    finally:
        return get_relevant_words(caption)
    

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
        caption_keywords = get_captions(data['videoInfo']['id'])
        
        try:
            required_data['tags'] = data['videoInfo']['snippet']['tags']
        except:
            required_data['tags'] = []
        required_data['tags'] = required_data['tags'] + caption_keywords
        
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
        # print(tagstring)

        relevantKeywordsList = get_relevant_words(data['videoInfo']['snippet']['title']) \
            + get_relevant_words(data['videoInfo']['snippet']['channelTitle']) \
            + get_relevant_words(data['videoInfo']['snippet']['description']) \
            + get_relevant_words(tagstring)
        required_data['relevantKeywords'] = list(dict.fromkeys(relevantKeywordsList))

        with open(os.path.join(output_directory_path, os.path.basename(filepath)), 'w') as outfile:
            json.dump(required_data, outfile, indent=4)

        file.close()

def get_relevant_keywords_from_videodata(title, channel_name, description, tags):
        all_tags = []
        for tag in tags:
            taglist = tag.split()
            for t in taglist:
                all_tags.append(t)
        tagstring = ' '.join(all_tags)

        relevantKeywordsList = get_relevant_words(title) \
            + get_relevant_words(channel_name) \
            + get_relevant_words(description) \
            + get_relevant_words(' '.join(tagstring))
        
        return list(dict.fromkeys(relevantKeywordsList))


# main function
if __name__ == '__main__':
    preprocess()
    # print()
    pass