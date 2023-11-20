import os
import json
from pymongo import MongoClient, ASCENDING
from py2neo import Graph, Node, Relationship
import nltk
from nltk.corpus import stopwords
from flask_login import login_required, current_user
import json

client = MongoClient('localhost', 27017)
# db = client['test_database']
# collection = db['test_collection']
db = client['testdb']
collection = db['videos']
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
        video_id = video_data["videoId"]
        likes = video_data["likeCount"]
        dislikes = video_data["dislikeCount"]
        views = video_data["viewCount"]
        channel = video_data["channelId"]
        title = video_data["title"]
        description = video_data["description"]
        try:
            tags = video_data["tags"]
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
        if(self.is_already_subscribed(user_id, channel_id)):
            self.remove_subscribed_relationship(user_id, channel_id)
            return
        user_subsribed_channel_relationship = Relationship(user_node, "SUBSCRIBED", channel_node)
        self.graph.create(user_subsribed_channel_relationship)
        
    def create_user_liked_video_relationship(self, user_id, video_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        if(self.is_already_liked(user_id, video_id)):
            self.remove_like_relationship(user_id, video_id)
            return
        if(self.is_already_disliked(user_id, video_id)):
            self.remove_dislike_relationship(user_id, video_id)
            query = (
                f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
                "SET video.dislikes = video.dislikes - 1"
            )
            self.graph.run(query)

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
        if(self.is_already_disliked(user_id, video_id)):
            self.remove_dislike_relationship(user_id, video_id)
            return
        if(self.is_already_liked(user_id, video_id)):
            self.remove_like_relationship(user_id, video_id)
            query = (
                f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
                "SET video.likes = video.likes - 1"
            )
            self.graph.run(query)

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
        video_id_list = [video_data["videoId"] for video_data in videos_data]
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
    
    def remove_like_relationship(self, user_id, video_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:LIKED]-(:VIDEO {{video_id: '{video_id}'}}) "
            f"DELETE r"
        )

        self.graph.run(query)

    def remove_dislike_relationship(self, user_id, video_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:DISLIKED]-(:VIDEO {{video_id: '{video_id}'}}) "
            f"DELETE r"
        )

        self.graph.run(query)

    def remove_subscribed_relationship(self, user_id, channel_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:SUBSCRIBED]-(:CHANNEL {{channel_id: '{channel_id}'}}) "
            f"DELETE r"
        )

        self.graph.run(query)

    def is_already_liked(self, user_id, video_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:LIKED]-(:VIDEO {{video_id: '{video_id}'}}) "
            f"RETURN COUNT(r) > 0"
        )

        return self.graph.evaluate(query)
    
    def is_already_disliked(self, user_id, video_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:DISLIKED]-(:VIDEO {{video_id: '{video_id}'}}) "
            f"RETURN COUNT(r) > 0"
        )

        return self.graph.evaluate(query)

    def is_already_subscribed(self, user_id, channel_id):
        query = (
            f"MATCH (:USER {{user_id: '{user_id}'}})-[r:SUBSCRIBED]-(:CHANNEL {{channel_id: '{channel_id}'}}) "
            f"RETURN COUNT(r) > 0"
        )

        return self.graph.evaluate(query)

    def get_relation_with_other_videos(self, video_id_current):
        other_videos_meta_data = {}
        for video_data in videos_data:
            video_id_other = video_data["videoId"]
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
        individual_meta_data = {}
        num_videos = 1
        import time
        start_time = time.time()
        for video_data in videos_data:
            video_id_current = video_data["videoId"]
            relationships_meta_data[video_id_current] = self.get_relation_with_other_videos(video_id_current)
            individual_meta_data[video_id_current] = {
                "likes": self.__get_video_property(video_id_current, "likes"),
                "dislikes": self.__get_video_property(video_id_current, "dislikes"),
                "views": self.__get_video_property(video_id_current, "views"),
            }
            print(f"Completed video {num_videos}")
            num_videos += 1

        with open('relations.json', 'w') as file:
            json.dump(relationships_meta_data, file, indent=4)

        with open('individual.json', 'w') as file:
            json.dump(individual_meta_data, file, indent=4)

        end_time = time.time()
        print(f"Time taken : {end_time - start_time}")
    
    def get_score(self, user_id, current_video_id, video_id, individual_cache, relations_cache):
        try:
            user_data = user_cache[user_id]
        except KeyError:
            user_data = {"liked": [], "disliked": [], "subscribed": []}
        
        video_data = individual_cache[video_id]
        video_is_liked = 0
        video_is_disliked = 0
        videos_channel_is_subsribed = 0
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

        relation_data = relations_cache[current_video_id][video_id]
        
        score = weightage_likes * video_data["likes"] + weightage_dislikes * video_data["dislikes"] + \
            weightage_views * video_data["views"] + weightage_same_channel * relation_data["same_channel"] + \
            weightage_num_common_words_description * relation_data["num_common_words_description"] + \
            weightage_num_common_words_title * relation_data["num_common_words_title"] + \
            weightage_num_common_tags * relation_data["num_common_tags"] + \
            weightage_liked_video * video_is_liked + weightage_disliked_video * video_is_disliked + \
            weightage_subsribed_channel_of_video * videos_channel_is_subsribed
        return score

    def get_score_wrt_current_video(self, current_video_id):
        with open('relations.json', 'r') as file:
            relations_cache = json.load(file)
        with open('individual.json', 'r') as file:
            individual_cache= json.load(file)
        relevant_videos = relations_cache[current_video_id]
        user_id = current_user.id
        scores = []
        weighage_most_related_user = 0.75
        most_related_user_id = self.get_most_related_user(user_id)
        for video_id in relevant_videos:
            if video_id != current_video_id:
                score = self.get_score(user_id, current_video_id, video_id, individual_cache, relations_cache) + \
                        weighage_most_related_user * self.get_score(most_related_user_id, current_video_id, video_id, individual_cache, relations_cache)
                scores.append([score, video_id])
        top_5_scores = sorted(scores)[::-1][:5]
        top_5_videos = [video[1] for video in top_5_scores]
        return top_5_videos
    
    def get_count_of_common_liked_videos(self, user_id1, user_id2):
        query = (
            f"MATCH (:USER {{user_id: {user_id1}}})-[:LIKED]-> (video:VIDEO) "
            f"MATCH (:USER {{user_id: {user_id2}}})-[:LIKED]-> (video) "
            f"RETURN COUNT(video)"
        )

        return self.graph.evaluate(query)
    
    def get_count_of_common_disliked_videos(self, user_id1, user_id2):
        query = (
            f"MATCH (:USER {{user_id: {user_id1}}})-[:DISLIKED]-> (video:VIDEO) "
            f"MATCH (:USER {{user_id: {user_id2}}})-[:DISLIKED]-> (video) "
            f"RETURN COUNT(video)"
        )

        return self.graph.evaluate(query)
    
    def get_count_of_common_subscribed_channels(self, user_id1, user_id2):
        query = (
            f"MATCH (:USER {{user_id: {user_id1}}})-[:SUBSCRIBED]-> (channel:CHANNEL) "
            f"MATCH (:USER {{user_id: {user_id2}}})-[:SUBSCRIBED]-> (channel) "
            f"RETURN COUNT(channel)"
        )

        return self.graph.evaluate(query)
    
    def set_relationship_between_users(self):
        with open("users.json", "r") as file:
            users = json.load(file)
        all_user_id = list(users.keys())
        users_relation = {}
        num_users = len(all_user_id)
        for i in range(num_users):
            ith_user_relation = {}
            for j in range(num_users):
                if(i == j):
                    continue
                jth_user_relation = {}
                user_id1, user_id2 = all_user_id[i], all_user_id[j]
                jth_user_relation["num_common_liked_videos"] = self.get_count_of_common_liked_videos(user_id1, user_id2)
                jth_user_relation["num_common_disliked_videos"] = self.get_count_of_common_disliked_videos(user_id1, user_id2)
                jth_user_relation["num_common_subsribed_channels"] = self.get_count_of_common_subscribed_channels(user_id1, user_id2)
                ith_user_relation[user_id2] = jth_user_relation
            users_relation[user_id1] = ith_user_relation
        with open("users_relation.json", "w") as file:
            json.dump(users_relation, file, indent=4)

    def get_relation_score(self, user_relation_data):
        weightage_liked = 1/3
        weightage_disliked = 1/3
        weightage_subscribed = 1/3
        score =  weightage_liked * user_relation_data["num_common_liked_videos"] + \
                weightage_disliked * user_relation_data["num_common_disliked_videos"] + \
                weightage_subscribed * user_relation_data["num_common_subsribed_channels"]
        return score

    def get_most_related_user(self, current_user_id):
        with open("users_relation.json", "r") as file:
            users_relation = json.load(file)
        other_users_relation_data = users_relation[str(current_user_id)]
        most_related_user_id, max_relation_score = None
        for user_id, user_relation_data in other_users_relation_data.items():
            relation_score = self.get_relation_score(user_relation_data)
            if relation_score > max_relation_score:
                max_relation_score = relation_score
                most_related_user_id = user_id
        return most_related_user_id

def update_users_data(user_id, property_name, property_value):
    with open("users.json", "r") as file:
        users = json.load(file)
    flag = False
    if(property_name == "liked"):
        if property_value in users[user_id]["disliked"]:
            users[user_id]["disliked"].remove(property_value)
        if property_value in users[user_id]["liked"]:
            users[user_id]["liked"].remove(property_value)
            flag = True
    elif(property_name == "disliked"):
        if property_value in users[user_id]["liked"]:
            users[user_id]["liked"].remove(property_value)
        if property_value in users[user_id]["disliked"]:
            users[user_id]["disliked"].remove(property_value)
            flag = True
    elif(property_name == "subscribed"):
        if property_value in users[user_id]["subscribed"]:
            users[user_id]["subscribed"].remove(property_value)
            flag = True
    
    if flag == False:
        users[user_id][property_name].append(property_value)
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)
    return flag


def update_like_in_cache(video_id):
    with open("individual.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["likes"] += 1
    with open("individual.json", "w") as file:
        json.dump(cache, file, indent=4)


def update_dislike_in_cache(video_id):
    with open("individual.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["dislikes"] += 1
    with open("individual.json", "w") as file:
        json.dump(cache, file, indent=4)


def update_views_in_cache(video_id):
    with open("individual.json", "r") as file:
        cache = json.load(file)
    cache[video_id]["views"] += 1
    with open("individual.json", "w") as file:
        json.dump(cache, file,indent=4)


class User(Neo4jHandler):
    
    def __init__(self, user_id, uri="bolt://localhost:7687", username="neo4j", password="password"):
        super().__init__(uri, username, password)  # Connect to the database where we already have our data
        self.user_id = str(user_id)

    # All the methods for User-Channel relationship
    def subscribe(self, channel_id):
        update_users_data(self.user_id, "subscribed", channel_id)
        self.create_user_subscribed_channel_relationship(self.user_id, channel_id)
        
    # All the methods for User-Video relationship
    def like(self, video_id):
        is_already_liked = update_users_data(self.user_id, "liked", video_id)
        if not is_already_liked:
            update_like_in_cache(video_id)
        self.create_user_liked_video_relationship(self.user_id, video_id)
    
    def dislike(self, video_id):
        is_already_disliked = update_users_data(self.user_id, "disliked", video_id)
        if not is_already_disliked:
            update_dislike_in_cache(video_id)
        self.create_user_disliked_video_relationship(self.user_id, video_id)


def main():
    neo4j = Neo4jHandler(uri="bolt://localhost:7687", username="neo4j", password="password")
    # neo4j.create_initial_graph()
    # neo4j.get_relationships_meta_data()
    neo4j.set_relationship_between_users()


if __name__ == "__main__":
    main()