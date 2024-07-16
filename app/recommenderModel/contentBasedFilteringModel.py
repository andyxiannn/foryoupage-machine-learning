#https://www.kaggle.com/code/gspmoreira/recommender-systems-in-python-101/notebook
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    
    MODEL_NAME = 'Content-Based'
    
    def __init__(self, item_ids, tfidf_matrix, interactions_train_df, articles_df, items_df=None):
        self.item_ids = item_ids
        self.tfidf_matrix = tfidf_matrix
        self.interactions_train_df = interactions_train_df
        self.articles_df = articles_df
        self.items_df = items_df
        
    def get_model_name(self):
        return self.MODEL_NAME
    
    def get_item_profile(self, item_id):
        idx = self.item_ids.index(item_id)
        item_profile = self.tfidf_matrix[idx:idx+1]
        return item_profile

    def get_item_profiles(self, ids):
        item_profiles_list = [self.get_item_profile(x) for x in ids]
        item_profiles = scipy.sparse.vstack(item_profiles_list)
        return item_profiles

    def build_users_profile(self, person_id, interactions_indexed_df):
        interactions_person_df = interactions_indexed_df.loc[person_id]
        user_item_profiles = self.get_item_profiles(interactions_person_df['contentId'])
        
        user_item_strengths = np.array(interactions_person_df['eventStrength']).reshape(-1,1)
        #Weighted average of item profiles by the interactions strength
        user_item_strengths_weighted_avg = np.sum(user_item_profiles.multiply(user_item_strengths), axis=0) / np.sum(user_item_strengths)
        user_item_strengths_weighted_avg_array = np.asarray(user_item_strengths_weighted_avg)

        user_profile_norm = sklearn.preprocessing.normalize(user_item_strengths_weighted_avg_array)
        return user_profile_norm

    def build_users_profiles(self): 
        interactions_indexed_df = self.interactions_train_df[self.interactions_train_df['contentId'] \
                                                    .isin(self.articles_df['contentId'])].set_index('userId')
        user_profiles = {}
        for person_id in interactions_indexed_df.index.unique():
            user_profiles[person_id] = self.build_users_profile(person_id, interactions_indexed_df)
        return user_profiles
        
    def _get_similar_items_to_user_profile(self, person_id, topn=1000):
        #Computes the cosine similarity between the user profile and all item profiles
        user_profiles = self.build_users_profiles()
        cosine_similarities = cosine_similarity(user_profiles[person_id], self.tfidf_matrix)
        #Gets the top similar items
        similar_indices = cosine_similarities.argsort().flatten()[-topn:]
        #Sort the similar items by similarity
        similar_items = sorted([(self.item_ids[i], cosine_similarities[0,i]) for i in similar_indices], key=lambda x: -x[1])
        return similar_items
        
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        similar_items = self._get_similar_items_to_user_profile(user_id)
        #Ignores items the user has already interacted
        similar_items_filtered = list(filter(lambda x: x[0] not in items_to_ignore, similar_items))
        
        recommendations_df = pd.DataFrame(similar_items_filtered, columns=['contentId', 'recStrength']) \
                                    .head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['recStrength', 'contentId', 'content']]


        return recommendations_df
    
# content_based_recommender_model = ContentBasedRecommender(articles_df)

# print('Evaluating Content-Based Filtering model...')
# cb_global_metrics, cb_detailed_results_df = model_evaluator.evaluate_model(content_based_recommender_model)
# print('\nGlobal metrics:\n%s' % cb_global_metrics)
# print(cb_detailed_results_df.head(10))


# print(content_based_recommender_model.recommend_items(-1479311724257856983))