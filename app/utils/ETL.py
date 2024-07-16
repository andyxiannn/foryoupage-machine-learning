#https://www.kaggle.com/code/gspmoreira/recommender-systems-in-python-101/notebook
import numpy as np
import scipy
import pandas as pd
import math
import random
import sklearn
import nltk
# nltk.download_shell()
# nltk.download('stopwords')
from nltk.corpus import stopwords
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
from sklearn.preprocessing import MinMaxScaler, normalize
import matplotlib.pyplot as plt

def transformData(postData, userInteractionData):
    contents_df = pd.DataFrame(postData)
    interactions_df = pd.DataFrame(userInteractionData)

    event_type_strength = {
        'VIEW': 1.0,
        'LIKE': 2.0, 
        'BOOKMARK': 2.5, 
        'FOLLOW': 3.0,
        'COMMENT CREATED': 4.0,  
        'SHARE': 5.0,  
    }

    interactions_df['eventStrength'] = interactions_df['eventType'].apply(lambda x: event_type_strength[x])

    users_interactions_count_df = interactions_df.groupby(['userId', 'contentId']).size().groupby('userId').size()
    print('# users: %d' % len(users_interactions_count_df))
    users_with_enough_interactions_df = users_interactions_count_df[users_interactions_count_df >= 5].reset_index()[['userId']]
    print('# users with at least 5 interactions: %d' % len(users_with_enough_interactions_df))

    print('# of interactions: %d' % len(interactions_df))
    interactions_from_selected_users_df = interactions_df.merge(users_with_enough_interactions_df, 
                how = 'right',
                left_on = 'userId',
                right_on = 'userId')
    print('# of interactions from users with at least 5 interactions: %d' % len(interactions_from_selected_users_df))

    def smooth_user_preference(x):
        return math.log(1+x, 2)
        
    interactions_full_df = interactions_from_selected_users_df \
                        .groupby(['userId', 'contentId'])['eventStrength'].sum() \
                        .apply(smooth_user_preference).reset_index()
    print('# of unique user/item interactions: %d' % len(interactions_full_df))

    interactions_train_df, interactions_test_df = train_test_split(interactions_full_df,
                                    stratify=interactions_full_df['userId'], 
                                    test_size=0.20,
                                    random_state=42)

    print('# interactions on Full set: %d' % len(interactions_full_df))
    print('# interactions on Train set: %d' % len(interactions_train_df))
    print('# interactions on Test set: %d' % len(interactions_test_df))

    #Indexing by userId to speed up the searches during evaluation
    interactions_full_indexed_df = interactions_full_df.set_index('userId')
    interactions_train_indexed_df = interactions_train_df.set_index('userId')
    interactions_test_indexed_df = interactions_test_df.set_index('userId')
    
    return [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df]


def transformDataCollaborative(postData, userInteractionData):
    [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(postData, userInteractionData)

    #Creating a sparse pivot table with users in rows and items in columns
    users_items_pivot_matrix_df = interactions_train_df.pivot(index='userId', 
                                                            columns='contentId', 
                                                            values='eventStrength').fillna(0)

    users_items_pivot_matrix = csr_matrix(users_items_pivot_matrix_df.values)
    users_items_pivot_matrix[:10]

    users_ids = list(users_items_pivot_matrix_df.index)
    users_ids[:10]

    users_items_pivot_sparse_matrix = csr_matrix(users_items_pivot_matrix)
    users_items_pivot_sparse_matrix

    #The number of factors to factor the user-item matrix.
    NUMBER_OF_FACTORS_MF = 15
    #Performs matrix factorization of the original user item matrix
    #U, sigma, Vt = svds(users_items_pivot_matrix, k = NUMBER_OF_FACTORS_MF)
    U, sigma, Vt = svds(users_items_pivot_sparse_matrix, k = NUMBER_OF_FACTORS_MF)

    sigma = np.diag(sigma)

    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) 

    all_user_predicted_ratings_norm = (all_user_predicted_ratings - all_user_predicted_ratings.min()) / (all_user_predicted_ratings.max() - all_user_predicted_ratings.min())

    #Converting the reconstructed matrix back to a Pandas dataframe
    cf_preds_df = pd.DataFrame(all_user_predicted_ratings_norm, columns = users_items_pivot_matrix_df.columns, index=users_ids).transpose()

    return [cf_preds_df, contents_df]


def transformDataContent(postData, userInteractionData):
    [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(postData, userInteractionData)

    stopwords_list = stopwords.words('english')

    #Trains a model whose vectors size is 5000, composed by the main unigrams and bigrams found in the corpus, ignoring stopwords
    vectorizer = TfidfVectorizer(analyzer='word',
                        ngram_range=(1, 2),
                        min_df=0.003,
                        max_df=0.5,
                        max_features=5000,
                        stop_words=stopwords_list)

    item_ids = contents_df['contentId'].tolist()
    tfidf_matrix = vectorizer.fit_transform(contents_df['content'])
    tfidf_feature_names = vectorizer.get_feature_names_out()
    tfidf_matrix
    
    return [item_ids, interactions_train_df, tfidf_matrix, contents_df]

def transformDataPopularity(postData, userInteractionData):
    [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(postData, userInteractionData)

    #Computes the most popular items
    item_popularity_df = interactions_full_df.groupby('contentId')['eventStrength'].sum().sort_values(ascending=False).reset_index()
    
    return [item_popularity_df, contents_df]