from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import os, json
from fastapi_utils.tasks import repeat_every
from fastapi import APIRouter
import logging
from uuid import uuid4
from log.log_config import RequestFilter
from database.crud.recommendationCrud import getContentList, getInteractionsList, getUsersList
from utils.ETL import transformDataCollaborative, transformDataContent
from recommenderModel.collaborativeFilteringModel import CFRecommender
from recommenderModel.contentBasedFilteringModel import ContentBasedRecommender
from recommenderModel.hybridFilteringModel import HybridRecommender
from app.config import settings
from datetime import datetime
import time
import concurrent.futures
from app.database.database import fyp

app_forYouRecommendation = APIRouter()

path = "./log/cron"
if not os.path.exists(path) :
    os.makedirs(path)

logger = logging.getLogger("logger_fyp")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler('log/cron/forYouRecommendation', when='midnight', backupCount=1000)
handler.suffix = "%Y-%m-%d.log"
handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)-8s | %(correlation_id)s | %(funcName)s | line %(lineno)s | %(message)s', '%H:%M:%S'))
handler.addFilter(RequestFilter())
logger.addHandler(handler)

@app_forYouRecommendation.on_event("startup")
@repeat_every(seconds = int(settings.FYP_CRONJOB_INTERVAL), raise_exceptions = True)
async def forYouRecommendation():
    RequestFilter.correlation_id.set(uuid4().hex)
    logger.info("FYP cronjob started")
    try:
        start_time = datetime.now()
        userList        = getUsersList()
        contentList        = getContentList()
        interactionList = getInteractionsList()
   
        for user in userList:
            logger.info(f"FYP cronjob running: {user['userId']}")
            userId = user['userId']
            [cf_preds_df, articles_df] = transformDataCollaborative(contentList, interactionList)
            [item_ids, interactions_train_df, tfidf_matrix, articles_df] = transformDataContent(contentList, interactionList)
                
            cf_recommender_model = CFRecommender(cf_preds_df, articles_df)
            content_based_recommender_model = ContentBasedRecommender(item_ids, tfidf_matrix, interactions_train_df, articles_df)
            
            hybrid_recommender_model = HybridRecommender(content_based_recommender_model, cf_recommender_model, articles_df, cb_ensemble_weight=1.0, cf_ensemble_weight=100.0)
            result = hybrid_recommender_model.recommend_items(userId, [], settings.FYP_AMOUNT)
            
            #convert dataframe to json
            result = result.to_json(orient='records', indent=4)
            result = json.loads(result)
            
            finalResult = {}
            finalResult['userId'] = userId
            finalResult['createdAt'] = datetime.now()
            finalResult['recommendedContentList'] = result
            
            fyp.insert_one(finalResult)
            
        
    except Exception as e:
        logger.error(f"FYP cronjob error: {e.args[0]}")
    finally:
        logger.info("FYP cronjob ended")
        end_time = datetime.now()
        logger.info('Duration: {}'.format(end_time - start_time))

