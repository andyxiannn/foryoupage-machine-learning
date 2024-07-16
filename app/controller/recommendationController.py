from datetime import datetime
import json
import pandas as pd
from fastapi import Depends, HTTPException, status, APIRouter, Response
from starlette.responses import JSONResponse
from pymongo.collection import ReturnDocument
import app.schemas as schemas
from app.database.database import posts, likes, db
from app.oauth2 import require_user
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from bson import json_util
from app.utils.utilities import parse_json
from app.utils.ETL import transformData, transformDataCollaborative, transformDataContent, transformDataPopularity
from app.database.crud.recommendationCrud import getContentList, getInteractionsList, getUsersList
from app.recommenderModel.popularityModel import PopularityRecommender
from app.recommenderModel.collaborativeFilteringModel import CFRecommender
from app.recommenderModel.contentBasedFilteringModel import ContentBasedRecommender
from app.recommenderModel.hybridFilteringModel import HybridRecommender
from app.utils.modelEvaluator import ModelEvaluator
from app.database.database import fyp, popularPost
from app.database.schema.recommenderSchema import PopularityContent
from app.response_model.common_model import errorHandler, successHandler
import random

def updatePostRandomPlanet():
    planet_ids = [planet['_id'] for planet in db.planets.find({}, {'_id': 1})]
    print(planet_ids)
    if not planet_ids:
        print('No planetIds found in the planet collection.')
    else:
        # Iterate through each document in the posts collection
        for post in db.posts.find():
            # Select a random planetId
            random_planet_id = random.choice(planet_ids)

            # Update the post with the random planetId
            db.posts.update_one(
                {'_id': post['_id']},
                {'$set': {'planetId': random_planet_id}}
            )

    print('PlanetId updated randomly for all posts.')
    
def getUsers():
    resultList = getUsersList()
    
    users_df = pd.DataFrame(resultList)
    print(users_df.head(5))

    return successHandler(resultList)

def getContents(planetId, tribeId):
    try:
        result = {}
        print(planetId, tribeId)
        resultList = getContentList(planetId, tribeId)
        
        result["data"] = resultList
        result["total"] = len(resultList)
        
        content_df = pd.DataFrame(resultList)
        print(content_df.head(5))
        return successHandler(result)
    except Exception as e: 
        print(e)
        return errorHandler(e)

def getInteractions(contentList):
    try:
        result = {}
        print(contentList)
        resultList = getInteractionsList(contentList)
        
        result["data"] = resultList
        result["total"] = len(resultList)
        
        interaction_df = pd.DataFrame(resultList)
        print(interaction_df.head(5))
        print(len(interaction_df))
        # interaction_df.to_csv("interaction.csv", index = None, header=True)
        return successHandler(result)
    except Exception as e: 
        print(e)
        return errorHandler(e)


def getRecommendationResults(userId, modelName, amount = 10, filterType = None , filterId = None):
    try:
        planetId = None
        tribeId = None
        if filterType == "Planet":
            planetId = filterId
        elif filterType == "Tribe":
            tribeId = filterId
        print(filterId)
        contentList     = getContentList(planetId, tribeId)
        # print(contentList)
        content_ids = [item["contentId"] for item in contentList]
            # content_ids = content.contentId 
        
        print(content_ids)
        interactionList = getInteractionsList(content_ids)
        
        if modelName == 'Popularity':
            [item_popularity_df, contents_df] = transformDataPopularity(contentList, interactionList)
            popularity_model = PopularityRecommender(item_popularity_df, contents_df)
            
            result = popularity_model.recommend_items([], amount)
            result = result.to_json(orient='records', indent=4)
            result = json.loads(result)
            
            content = PopularityContent(popularContentList=result)
            # Convert to MongoDB document format
            finalContent = content.dict()
            popularPost.insert_one(finalContent)
            
        elif modelName == 'Collaborative':
            [cf_preds_df, contents_df] = transformDataCollaborative(contentList, interactionList)
            cf_recommender_model = CFRecommender(cf_preds_df, contents_df)
            result = cf_recommender_model.recommend_items(userId, [], amount)
            result = result.to_json(orient='records', indent=4)
            result = json.loads(result)
            finalResult = {}
            finalResult['userId'] = userId
            finalResult['createdAt'] = datetime.now()
            finalResult['recommendedContentList'] = result
            
            # [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(contentList, interactionList)
            # model_evaluator = ModelEvaluator(interactions_full_indexed_df, interactions_test_indexed_df, interactions_train_indexed_df, contents_df)   
            # cf_global_metrics, cf_detailed_results_df = model_evaluator.evaluate_model(cf_recommender_model)
            # print('\nGlobal metrics:\n%s' % cf_global_metrics)
            # print(cf_detailed_results_df.head(10))
                        
        elif modelName == 'Content':
            [item_ids, interactions_train_df, tfidf_matrix, contents_df] = transformDataContent(contentList, interactionList)
            content_based_recommender_model = ContentBasedRecommender(item_ids, tfidf_matrix, interactions_train_df, contents_df)
            result = content_based_recommender_model.recommend_items(userId, [], amount)
            result = result.to_json(orient='records', indent=4)
            result = json.loads(result)
            finalResult = {}
            finalResult['userId'] = userId
            finalResult['createdAt'] = datetime.now()
            finalResult['recommendedContentList'] = result
            
            # [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(contentList, interactionList)
            # model_evaluator = ModelEvaluator(interactions_full_indexed_df, interactions_test_indexed_df, interactions_train_indexed_df, contents_df)   
            # print('Evaluating Content-Based Filtering model...')
            # cb_global_metrics, cb_detailed_results_df = model_evaluator.evaluate_model(content_based_recommender_model)
            # print('\nGlobal metrics:\n%s' % cb_global_metrics)
            # print(cb_detailed_results_df.head(10))
            
        elif modelName == 'Hybrid':
            [cf_preds_df, contents_df] = transformDataCollaborative(contentList, interactionList)
            [item_ids, interactions_train_df, tfidf_matrix, contents_df] = transformDataContent(contentList, interactionList)
            
            cf_recommender_model = CFRecommender(cf_preds_df, contents_df)
            content_based_recommender_model = ContentBasedRecommender(item_ids, tfidf_matrix, interactions_train_df, contents_df)
            
            hybrid_recommender_model = HybridRecommender(content_based_recommender_model, cf_recommender_model, contents_df, cb_ensemble_weight=50.0, cf_ensemble_weight=50.0)
            result = hybrid_recommender_model.recommend_items(userId, [], amount)
            result = result.to_json(orient='records', indent=4)
            result = json.loads(result)
            finalResult = {}
            finalResult['userId'] = userId
            finalResult['createdAt'] = datetime.now()
            finalResult['recommendedContentList'] = result
            
            fyp.insert_one(finalResult)
            
            # [contents_df, interactions_full_df, interactions_train_df, interactions_test_df, interactions_full_indexed_df, interactions_train_indexed_df, interactions_test_indexed_df] = transformData(contentList, interactionList)
            # model_evaluator = ModelEvaluator(interactions_full_indexed_df, interactions_test_indexed_df, interactions_train_indexed_df, contents_df)   
            # hybrid_global_metrics, hybrid_detailed_results_df = model_evaluator.evaluate_model(hybrid_recommender_model)
            # print('\nGlobal metrics:\n%s' % hybrid_global_metrics)
            # print(hybrid_detailed_results_df.head(10))
        else :
            raise HTTPException(status_code=404, detail="modelName not found")
        
        return successHandler(parse_json(finalResult))
    except ZeroDivisionError as e:
        print(e)
        return errorHandler(e)