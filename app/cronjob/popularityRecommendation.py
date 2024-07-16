from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import os, json
from fastapi_utils.tasks import repeat_every
from fastapi import APIRouter
import logging
from uuid import uuid4
from log.log_config import RequestFilter
from database.crud.recommendationCrud import getContentList, getInteractionsList
from app.utils.ETL import  transformDataPopularity
from app.recommenderModel.popularityModel import PopularityRecommender
from app.config import settings
from datetime import datetime
import time
import concurrent.futures
from app.database.database import fyp, popularPost

app_popularityRecommendation = APIRouter()

path = "./log/cron"
if not os.path.exists(path) :
    os.makedirs(path)

logger = logging.getLogger("logger_popular")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler('log/cron/popularityRecommendation', when='midnight', backupCount=1000)
handler.suffix = "%Y-%m-%d.log"
handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)-8s | %(correlation_id)s | %(funcName)s | line %(lineno)s | %(message)s', '%H:%M:%S'))
handler.addFilter(RequestFilter())
logger.addHandler(handler)

@app_popularityRecommendation.on_event("startup")
@repeat_every(seconds = int(settings.POPULARITY_CRONJOB_INTERVAL), raise_exceptions = True)
async def popularityRecommendation():
    RequestFilter.correlation_id.set(uuid4().hex)
    logger.info("Popularity cronjob started")
    try:
        start_time      = datetime.now()
        contentList     = getContentList()
        interactionList = getInteractionsList()

        [item_popularity_df, articles_df] = transformDataPopularity(contentList, interactionList)
        popularity_model = PopularityRecommender(item_popularity_df, articles_df)
        result = popularity_model.recommend_items([], settings.POPULARITY_AMOUNT)
        
        #convert dataframe to json
        result = result.to_json(orient='records', indent=4)
        result = json.loads(result)
        
        finalResult = {}
        finalResult['createdAt'] = datetime.now()
        finalResult['popularContentList'] = result
        popularPost.insert_one(finalResult)
        
    except Exception as e:
        logger.error(f"Popularity cronjob error: {e.args[0]}")
    finally:
        logger.info("Popularity cronjob ended")
        end_time = datetime.now()
        logger.info('Duration: {}'.format(end_time - start_time))

