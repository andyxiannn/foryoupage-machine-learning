from datetime import datetime
from pymongo.collection import ReturnDocument
from app.database.database import posts, likes, users
from app.oauth2 import require_user
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from app.utils.utilities import parse_json

def getUsersList():
    pipeline = [
        {'$match': { 'isAdmin': False, 'isDeleted': False , 'isActive': True, 'isCompleted': True}},
        {
            '$project': {
                "_id": 0,
                'followerCount': 1,
                'authorityScore': 1,
                'level': 1,
                'userId': {'$toString': '$_id'},  # Convert userId ObjectId to string
                'lastLogin': {'$toLong': '$lastLogin'},
            }
        }
    ]
    result = users.aggregate(pipeline)
    resultList = parse_json(list(result))
    return resultList

def getContentList(planetId = None, tribeId = None):
    search = {}
    if planetId:
        search["planetId"]= planetId 
        
    if tribeId:
        search["tribeId"]= tribeId

    pipeline = [
        { '$match': {"isActive": True}},
        { '$project': { "_id": 0, 'contentId': {'$toString': '$_id'}, 'planetId': {'$toString': '$planetId'}, 'tribeId': {'$toString': '$tribeId'},'content': 1, 'userId': {'$toString': '$userId'}, 'timestamp': {'$toLong': '$createdAt'}, 'contentType': 'POST',} },
        {
            '$unionWith': {
                'coll': 'polls',
                'pipeline': [ { '$project': { "_id": 0, 'contentId': {'$toString': '$_id'}, 'planetId': {'$toString': '$planetId'}, 'tribeId': {'$toString': '$tribeId'}, 'content': 1, 'userId': {'$toString': '$userId'}, 'timestamp': {'$toLong': '$createdAt'}, 'contentType': 'POLL', } }, ]
            }
        },
        {
            '$unionWith': {
                'coll': 'articles',
                'pipeline': [ { '$project': { "_id": 0, 'contentId': {'$toString': '$_id'}, 'planetId': {'$toString': '$planetId'},'tribeId': {'$toString': '$tribeId'},'content': 1, 'userId': {'$toString': '$userId'}, 'timestamp': {'$toLong': '$createdAt'}, 'contentType': 'ARTICLES',} }, ]
            }
        },
        { '$match': search }
    ]
    print(pipeline)
    result = posts.aggregate(pipeline)
    resultList = parse_json(list(result))
    return resultList

def getInteractionsList(contentList = None):
    search = {}
    if contentList:
        search = { "contentId" : {"$in": contentList} }
        
    pipeline = [
        {'$match': {'isUpvote': True}},
        {'$project': { '_id': 0, 'contentId': {'$toString': '$postId'}, 'userId': {'$toString': '$userId'}, 'eventType': 'LIKE', 'timestamp': {'$toLong': '$createdAt'}, } },
        {
            '$unionWith': {
                'coll': 'bookmarks',
                'pipeline': [ {'$project': { '_id': 0, 'contentId': {'$toString': '$postId'}, 'userId': {'$toString': '$userId'}, 'eventType': 'BOOKMARK', 'timestamp': {'$toLong': '$createdAt'}, } }, ]
            }
        },
        {
            '$unionWith': {
                'coll': 'comments',
                'pipeline': [ {'$project': { '_id': 0, 'contentId': {'$toString': '$postId'}, 'userId': {'$toString': '$userId'}, 'eventType': 'COMMENT CREATED', 'timestamp': {'$toLong': '$createdAt'}, } }, ]
            }
        },
        {
            '$unionWith': {
                'coll': 'shares',
                'pipeline': [ {'$project': { '_id': 0, 'contentId': {'$toString': '$postId'}, 'userId': {'$toString': '$userId'}, 'eventType': 'SHARE', 'timestamp': {'$toLong': '$createdAt'}, } }, ]
            }
        },
        { '$match': search }
    ]
    print(pipeline)
    result = likes.aggregate(pipeline)
    resultList = parse_json(list(result))

    return resultList
