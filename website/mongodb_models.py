import pymongo
from pymongo import MongoClient
import os, json
from jellyfish import jaro_similarity


class MongoDBHandler(object):
    
    def __init__(self, url="localhost", port=27017, db_name="testdb", collection_name="videos"):
        self.client = MongoClient(url, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # indexing
        self.collection.create_index([("videoId", pymongo.ASCENDING)])

    def __upload_data(self, data):
        self.collection.insert_one(data)

    def upload_single_video_data(self, data):
        self.__upload_data(data)

    def upload_data(self, directory_path):
        for video in os.listdir(directory_path):
            file = open(os.path.join(directory_path, video))
            data = json.load(file)
            self.__upload_data(data)
            file.close()

    def get_data(self, video_id):
        result = self.collection.find_one({"videoId": video_id})
        result['_id'] = str(result['_id'])
        return result
    
    def get_tags(self, video_id):
        result = self.collection.find_one({"videoId": video_id})
        tags = result['tags']
        
        taglist = set()

        for tag in tags:
            tag = tag.lower().split()
            for each in tag:
                taglist.add(each)

        return list(taglist)        


    def search(self, search_query, search_threshold=0.85):
        '''
        we can make further changes for prioritizing the search results
        by adding weights to the title, channel title and then relevant keywords
        '''
        search_query = search_query.lower()
        search_query = search_query.split()
        search_query = list(dict.fromkeys(search_query))

        result = self.collection.find({})
        
        filtered_results = []
        for document in result:
            title = document['title']
            channel_title = document['channelTitle']

            title_similarity_score = 0
            channel_title_similarity_score = 0


            relevant_keywords = document['relevantKeywords']
            # similar_word_count = 0
            # similar_words = []
            similarity_score = 0

            for word in search_query:
                for keyword in relevant_keywords:
                    if jaro_similarity(word, keyword) >= search_threshold:
                        # similar_word_count += 1
                        # similar_words.append((word, keyword))
                        similarity_score += jaro_similarity(word, keyword)
                for word_ in title.split():
                    if jaro_similarity(word, word_) >= search_threshold:
                        # similar_word_count += 1
                        # similar_words.append((word, word_))
                        title_similarity_score += jaro_similarity(word, word_)
                for word_ in channel_title.split():
                    if jaro_similarity(word, word_) >= search_threshold:
                        # similar_word_count += 1
                        # similar_words.append((word, word_))
                        channel_title_similarity_score += jaro_similarity(word, word_)

            total_similarity_score = 10*title_similarity_score + \
                    10*channel_title_similarity_score + \
                    similarity_score
                
            # document['similarity'] = similar_word_count
            # document['similarWords'] = similar_words
            document['similarityScore'] = total_similarity_score
            filtered_results.append(document)

        for result in filtered_results:
            result['_id'] = str(result['_id'])

        filtered_results = sorted(filtered_results, key=lambda k: k['similarityScore'], reverse=True)
        return filtered_results[:10]


if __name__ == '__main__':
    mongo_handler = MongoDBHandler(url="localhost", port=27017, db_name="testdb", collection_name="videos")
    
    # upload video data to MongoDB
    # '''
    mongo_handler.upload_data("../preprocessed_data")
    # '''

