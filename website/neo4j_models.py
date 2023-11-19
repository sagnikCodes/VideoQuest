import os
import json
from pymongo import MongoClient, ASCENDING
from py2neo import Graph, Node, Relationship
import nltk
from nltk.corpus import stopwords
from flask_login import login_required, current_user
import json

client = MongoClient('localhost', 27017)
db = client['test_database']
collection = db['test_collection']
videos_data = list(collection.find())
# nltk.download('stopwords')
english_stopwords = set(stopwords.words('english'))

with open('users.json', 'r') as file:
    user_cache = json.load(file)

class Neo4jHandler(object):
    
    def __init__(self, uri="bolt://localhost:7687", username="neo4j", password="password"):
        self.graph = Graph(uri, auth=(username, password))
    
    def __get_video_property(self, video_id, property_name):
        query = f"MATCH (v:VIDEO {{video_id: '{video_id}'}}) RETURN v.{property_name} AS result"
        result = self.graph.run(query).evaluate()
        return result
    
    def __get_num_common_property(self, video_node1, video_node2, property_name):
        video_id1, video_id2 = video_node1['video_id'], video_node2['video_id']
        property_video1 = self.__get_video_property(video_id1, property_name)
        property_video2 = self.__get_video_property(video_id2, property_name)
        if(property_name != 'tags'):
            property_video1 = property_video1.split()
            property_video2 = property_video2.split()
        try:
            property_lower_capped_1 = [each.lower() for each in property_video1 if each not in english_stopwords]
        except TypeError:
            property_lower_capped_1 = []
        try:
            property_lower_capped_2 = [each.lower() for each in property_video2 if each not in english_stopwords]
        except TypeError:
            property_lower_capped_2 = []
            
        return len(set(property_lower_capped_1) & set(property_lower_capped_2))
        
        
    def create_video_node(self, video_data):
        # We are storing each important information in video node so that accessing the relevant information is faster
        video_id = video_data["videoInfo"]["id"]
        likes = video_data["videoInfo"]["statistics"]["likeCount"]
        dislikes = video_data["videoInfo"]["statistics"]["dislikeCount"]
        views = video_data["videoInfo"]["statistics"]["viewCount"]
        channel = video_data["videoInfo"]["snippet"]["channelId"]
        title = video_data["videoInfo"]["snippet"]["title"]
        description = video_data["videoInfo"]["snippet"]["description"]
        try:
            tags = video_data["videoInfo"]["snippet"]["tags"]
        except:
            tags = []
        video_node = Node("VIDEO", video_id=video_id, likes=likes, dislikes=dislikes, views=views, channel=channel, tags=tags, title=title, description=description)
        self.graph.create(video_node)

    def create_user_node(self, user_id):
        user_node = Node("USER", user_id=user_id)
        self.graph.create(user_node)
    
    def create_same_channel_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        channel_id1 = self.__get_video_property(video_id1, "channel")
        channel_id2 = self.__get_video_property(video_id2, "channel")
        if(channel_id1 == channel_id2):
            same_channel_relation = Relationship(video_node1, "SAME_CHANNEL", video_node2)
            self.graph.create(same_channel_relation)
        
    def create_similar_tags_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_tags = self.__get_num_common_property(video_node1, video_node2, "tags")
        if(num_common_tags > 0):
            common_tag_relationship = Relationship(video_node1, "HAS_COMMON_TAG", video_node2, num_common_tags=num_common_tags)
            self.graph.create(common_tag_relationship)
    
    def create_similar_description_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_description_words = self.__get_num_common_property(video_node1, video_node2, "description")
        if(num_common_description_words > 5):
            similar_description_relationship = Relationship(video_node1, "HAS_SIMILAR_DESCRIPTION", video_node2, num_common_description_words=num_common_description_words)
            self.graph.create(similar_description_relationship)
            
    def create_similar_title_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_title_words = self.__get_num_common_property(video_node1, video_node2, "title")
        if(num_common_title_words > 2):
            similar_title_relationship = Relationship(video_node1, "HAS_SIMILAR_TITLE", video_node2, num_common_title_words=num_common_title_words)
            self.graph.create(similar_title_relationship)
            
    def create_video_channel_relationship(self, video_id):
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        channel_id = self.__get_video_property(video_id, "channel")
        # Create channel node
        channel_node = Node("CHANNEL", channel_id=channel_id)
        self.graph.create(channel_node)
        video_channel_relationship = Relationship(video_node, "CHANNEL_NAME", channel_node)
        self.graph.create(video_channel_relationship)
        
    def create_user_subscribed_channel_relationship(self, user_id, channel_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first() or Node("USER", user_id=user_id)
        channel_node = self.graph.nodes.match("CHANNEL", channel_id=channel_id).first()
        user_subsribed_channel_relationship = Relationship(user_node, "SUBSCRIBED", channel_node)
        self.graph.create(user_subsribed_channel_relationship)
            
    def create_user_hit_bell_icon_relationship(self, user_id, channel_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        channel_node = self.graph.nodes.match("CHANNEL", channel_id=channel_id).first()
        user_hit_bell_icon_relationship = Relationship(user_node, "HIT_BELL_ICON", channel_node)
        self.graph.create(user_hit_bell_icon_relationship)
        
    def create_user_liked_video_relationship(self, user_id, video_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        user_liked_video_relationship = Relationship(user_node, "LIKED", video_node)
        self.graph.create(user_liked_video_relationship)
        query = (
            f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
            "SET video.likes = video.likes + 1"
        )
        self.graph.run(query)
    
    def create_user_disliked_video_relationship(self, user_id, video_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        user_disliked_video_relationship = Relationship(user_node, "DISLIKED", video_node)
        self.graph.create(user_disliked_video_relationship)
        query = (
            f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
            "SET video.dislikes = video.dislikes + 1"
        )
        self.graph.run(query)
        
    def create_initial_graph(self):
        for video_data in videos_data:
            self.create_video_node(video_data)
        video_id_list = [video_data["videoInfo"]["id"] for video_data in videos_data]
        num_videos = len(video_id_list)
        for i in range(num_videos):
            for j in range(num_videos):
                if(i == j):
                    continue
                video_id1 = video_id_list[i]
                video_id2 = video_id_list[j]
                self.create_same_channel_relationship(video_id1, video_id2)
                self.create_similar_tags_relationship(video_id1, video_id2)
                self.create_similar_description_relationship(video_id1, video_id2)
                self.create_similar_title_relationship(video_id1, video_id2)
        for video_id in video_id_list:
            self.create_video_channel_relationship(video_id)
    
    def get_relationship_property(self, video_id1, video_id2, relationship, property_name=None):
        query = (
            f"MATCH (video1:VIDEO {{video_id: '{video_id1}'}})-[r:{relationship}]-(video2:VIDEO {{video_id: '{video_id2}'}}) "
            f"RETURN r.{property_name}"
        )
        if(property_name == None):
            # Means relationship is SAME_CHANNEL
            query = (
                f"MATCH (video1:VIDEO {{video_id: '{video_id1}'}})-[r:{relationship}]-(video2:VIDEO {{video_id: '{video_id2}'}}) "
                f"RETURN COUNT(r)"
            )
        
        return self.graph.evaluate(query)
    
    def get_user_video_relationship(self, user_id, video_id, relationship):
        query = (
            f"MATCH (user:USER {{user_id: '{user_id}'}})-[r:{relationship}]-(video:VIDEO {{video_id: '{video_id}'}}) "
            f"RETURN COUNT(r) > 0"
        )
        
        return self.graph.evaluate(query)
    
    def get_user_channel_relationship(self, user_id, video_id, relationship):
        channel_id = self.__get_video_property(video_id, "channel")
        query = (
            f"MATCH (user:USER {{user_id: '{user_id}'}})-[r:{relationship}]-(channel:CHANNEL {{channel_id: '{channel_id}'}}) "
            f"RETURN COUNT(r) > 0"
        )

        return self.graph.evaluate(query)

    def get_relation_with_other_videos(self, video_id_current):
        other_videos_meta_data = {}
        for video_data in videos_data:
            video_id_other = video_data["videoInfo"]["id"]
            if(video_id_other == video_id_current):
                continue
            
            video_meta_data = {}
            likes = self.__get_video_property(video_id_other, "likes")
            dislikes = self.__get_video_property(video_id_other, "dislikes")
            views = self.__get_video_property(video_id_other, "views")
            same_channel = self.get_relationship_property(video_id_current, video_id_other, "SAME_CHANNEL")
            num_common_words_description = self.get_relationship_property(video_id_current, video_id_other, "HAS_SIMILAR_DESCRIPTION", "num_common_description_words")
            num_common_words_title = self.get_relationship_property(video_id_current, video_id_other, "HAS_SIMILAR_TITLE", "num_common_title_words")
            num_common_tags = self.get_relationship_property(video_id_current, video_id_other, "HAS_COMMON_TAG", "num_common_tags")
            
            video_meta_data["likes"] = likes
            video_meta_data["dislikes"] = dislikes
            video_meta_data["views"] = views
            video_meta_data["same_channel"] = same_channel
            video_meta_data["num_common_words_description"] = num_common_words_description if(num_common_words_description != None) else 0
            video_meta_data["num_common_words_title"] = num_common_words_title if(num_common_words_title != None) else 0
            video_meta_data["num_common_tags"] = num_common_tags if(num_common_tags  != None) else 0
            
            other_videos_meta_data[video_id_other] = video_meta_data
        return other_videos_meta_data
    
    def get_relationships_meta_data(self):
        relationships_meta_data = {}
        num_videos = 1
        import time
        start_time = time.time()
        for video_data in videos_data:
            video_id_current = video_data["videoInfo"]["id"]
            relationships_meta_data[video_id_current] = self.get_relation_with_other_videos(video_id_current)
            print(f"Completed video {num_videos}")
            num_videos += 1
        with open('cache.json', 'w') as file:
            json.dump(relationships_meta_data, file)
        end_time = time.time()
        print(f"Time taken : {end_time - start_time}")
    
    def get_score(self, user_id, video_id, cache):
        try:
            user_data = user_cache[user_id]
        except KeyError:
            user_data = {"liked": [], "disliked": [], "subscribed": [], "hit_bell_icon": []}
        video_data = cache[video_id]
        video_is_liked = 0
        video_is_disliked = 0
        videos_channel_is_subsribed = 0
        videos_channel_bell_icon_hit = 0
        channel_id = self.__get_video_property(video_id, "channel")

        for liked_video_id in user_data["liked"]:
            if liked_video_id == video_id:
                video_is_liked = 1
                break
        
        for disliked_video_id in user_data["disliked"]:
            if disliked_video_id == video_id:
                video_is_disliked = 1
                break

        for subsribed_channel_id in user_data["subscribed"]:
            if subsribed_channel_id == channel_id:
                videos_channel_is_subsribed = 1
                break

        for hit_bell_icon_channel_id in user_data["hit_bell_icon"]:
            if hit_bell_icon_channel_id == channel_id:
                videos_channel_bell_icon_hit = 1
                break

        weightage_likes = 1
        weightage_dislikes = -2
        weightage_views = 3
        weightage_same_channel = 4
        weightage_num_common_words_description = 5
        weightage_num_common_words_title = 5
        weightage_num_common_tags = 5
        weightage_liked_video = 2
        weightage_disliked_video = -2
        weightage_subsribed_channel_of_video = 2
        weightage_hit_bell_icon_of_video = 3
        score = weightage_likes * video_data["likes"] + weightage_dislikes * video_data["dislikes"] + weightage_views * video_data["views"] + weightage_same_channel * video_data["same_channel"] + weightage_num_common_words_description * video_data["num_common_words_description"] + weightage_num_common_words_title * video_data["num_common_words_title"] + weightage_num_common_tags * video_data["num_common_tags"] + weightage_liked_video * video_is_liked + weightage_disliked_video * video_is_disliked + weightage_subsribed_channel_of_video * videos_channel_is_subsribed + weightage_hit_bell_icon_of_video * videos_channel_bell_icon_hit
        return score

    def get_score_wrt_current_video(self, current_video_id):
        with open('cache.json', 'r') as file:
            cache = json.load(file)
        relevant_videos = cache[current_video_id]
        user_id = current_user.id
        scores = []
        for video_id in relevant_videos:
            score = self.get_score(user_id, video_id, cache)
            scores.append([score, video_id])
        top_5_scores = sorted(scores)[::-1][:5]
        top_5_videos = [video[1] for video in top_5_scores]
        return top_5_videos


def push_data_to_users(user_id, property_name, property_value):
    with open("users.json", "r") as file:
        users = json.load(file)
    users[user_id][property_name].append(property_value)
    with open("users.json", "w") as file:
        json.dump(users, file)


def update_like_in_cache(video_id):
    with open("cache.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["likes"] += 1
    with open("cache.json", "w") as file:
        json.dump(cache, file)


def update_dislike_in_cache(video_id):
    with open("cache.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["dislikes"] += 1
    with open("cache.json", "w") as file:
        json.dump(cache, file)


def update_views_in_cache(video_id):
    with open("cache.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["views"] += 1
    with open("cache.json", "w") as file:
        json.dump(cache, file)


class User(Neo4jHandler):
    
    def __init__(self, user_id, uri="bolt://localhost:7687", username="neo4j", password="password"):
        super().__init__(uri, username, password)  # Connect to the database where we already have our data
        self.user_id = user_id

    # All the methods for User-Channel relationship
    def subscribe(self, channel_id):
        push_data_to_users(self.user_id, "subscribed", channel_id)
        self.create_user_subscribed_channel_relationship(self.user_id, channel_id)
        
    def hit_bell_icon(self, channel_id):
        push_data_to_users(self.user_id, "hit_bell_icon", channel_id)
        self.create_user_hit_bell_icon_relationship(self.user_id, channel_id)
        
    # All the methods for User-Video relationship
    def like(self, video_id):
        push_data_to_users(self.user_id, "liked", video_id)
        update_like_in_cache(video_id)
        self.create_user_liked_video_relationship(self.user_id, video_id)
    
    def dislike(self, video_id):
        push_data_to_users(self.user_id, "disliked", video_id)
        update_dislike_in_cache(video_id)
        self.create_user_disliked_video_relationship(self.user_id, video_id)


def main():
    neo4j = Neo4jHandler(uri="bolt://localhost:7687", username="neo4j", password="password")
    neo4j.get_relationships_meta_data()


if __name__ == "__main__":
    main()