#https://www.kaggle.com/code/gspmoreira/recommender-systems-in-python-101/notebook
import numpy as np
import pandas as pd

class PopularityRecommender:
    
    MODEL_NAME = 'Popularity'
    
    def __init__(self, popularity_df, items_df=None):
        self.popularity_df = popularity_df
        self.items_df = items_df
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, items_to_ignore=[], topn=10, verbose=False):
        # Recommend the more popular items that the user hasn't seen yet.
        recommendations_df = self.popularity_df[~self.popularity_df['contentId'].isin(items_to_ignore)] \
                               .sort_values('eventStrength', ascending = False) \
                               .head(topn)
        # if verbose:
        #     if self.items_df is None:
        #         raise Exception('"items_df" is required in verbose mode')

        recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['eventStrength', 'contentId', 'content', 'contentType']]

        return recommendations_df
    
# popularity_model = PopularityRecommender(item_popularity_df, articles_df)

# # print('Evaluating Popularity recommendation model...')
# # pop_global_metrics, pop_detailed_results_df = model_evaluator.evaluate_model(popularity_model)
# # # print('\nGlobal metrics:\n%s' % pop_global_metrics)
# # print(pop_detailed_results_df.head(10))

# print(popularity_model.recommend_items(-1479311724257856983))