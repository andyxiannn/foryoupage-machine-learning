#https://www.kaggle.com/code/gspmoreira/recommender-systems-in-python-101/notebook
import numpy as np
import pandas as pd

class HybridRecommender:
    
    MODEL_NAME = 'Hybrid'
    
    def __init__(self, cb_rec_model, cf_rec_model, items_df, cb_ensemble_weight=1.0, cf_ensemble_weight=1.0):
        self.cb_rec_model = cb_rec_model
        self.cf_rec_model = cf_rec_model
        self.cb_ensemble_weight = cb_ensemble_weight
        self.cf_ensemble_weight = cf_ensemble_weight
        self.items_df = items_df
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        #Getting the top-1000 Content-based filtering recommendations
        cb_recs_df = self.cb_rec_model.recommend_items(user_id, items_to_ignore=items_to_ignore, verbose=verbose,
                                                           topn=1000).rename(columns={'recStrength': 'recStrengthCB'})
        
        #Getting the top-1000 Collaborative filtering recommendations
        cf_recs_df = self.cf_rec_model.recommend_items(user_id, items_to_ignore=items_to_ignore, verbose=verbose, 
                                                           topn=1000).rename(columns={'recStrength': 'recStrengthCF'})
        
        #Combining the results by contentId
        recs_df = cb_recs_df.merge(cf_recs_df,
                                   how = 'outer', 
                                   left_on = 'contentId', 
                                   right_on = 'contentId').fillna(0.0)
        
        #Computing a hybrid recommendation score based on CF and CB scores
        #recs_df['recStrengthHybrid'] = recs_df['recStrengthCB'] * recs_df['recStrengthCF'] 
        recs_df['recStrengthHybrid'] = (recs_df['recStrengthCB'] * self.cb_ensemble_weight) \
                                     + (recs_df['recStrengthCF'] * self.cf_ensemble_weight)
        
        #Sorting recommendations by hybrid score
        recommendations_df = recs_df.sort_values('recStrengthHybrid', ascending=False).head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['recStrengthHybrid', 'contentId', 'content']]


        return recommendations_df
    
# hybrid_recommender_model = HybridRecommender(content_based_recommender_model, cf_recommender_model, articles_df,
#                                              cb_ensemble_weight=1.0, cf_ensemble_weight=100.0)

# print('Evaluating Hybrid model...')
# hybrid_global_metrics, hybrid_detailed_results_df = model_evaluator.evaluate_model(hybrid_recommender_model)
# print('\nGlobal metrics:\n%s' % hybrid_global_metrics)
# print(hybrid_detailed_results_df.head(10))

# global_metrics_df = pd.DataFrame([cb_global_metrics, pop_global_metrics, cf_global_metrics, hybrid_global_metrics]) \
#                         .set_index('modelName')
# print(global_metrics_df)

# def inspect_interactions(person_id, test_set=True):
#     if test_set:
#         interactions_df = interactions_test_indexed_df
#     else:
#         interactions_df = interactions_train_indexed_df
#     return interactions_df.loc[person_id].merge(articles_df, how = 'left', 
#                                                       left_on = 'contentId', 
#                                                       right_on = 'contentId') \
#                           .sort_values('eventStrength', ascending = False)[['eventStrength', 
#                                                                           'contentId',
#                                                                           'title', 'url', 'lang']]

# print(inspect_interactions(-1479311724257856983, test_set=False).head(20))

# print(hybrid_recommender_model.recommend_items(-1479311724257856983, topn=20, verbose=True))