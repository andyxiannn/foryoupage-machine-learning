from pymongo import mongo_client
import pymongo
from app.config import settings

client = mongo_client.MongoClient(settings.DATABASE_URL)
print('Connected to MongoDB...')

db = client["wolf-db"]
users       = db["users"]
posts       = db["posts"]
likes       = db["likes"]
shares      = db["shares"]
comments    = db["comments"]
bookmarks   = db["bookmarks"]

fyp = db['fyp']
popularPost = db['popularPosts']