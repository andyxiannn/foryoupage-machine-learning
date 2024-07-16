from datetime import datetime
from fastapi import Depends, HTTPException, status, APIRouter, Response, Request
from app.oauth2 import require_user
import app.controller.recommendationController as recommendationController
from fastapi.responses import JSONResponse
from app.database.schema.recommenderSchema import recommendationTraining, content, interaction

router = APIRouter()

@router.get('/users')
def getUsers():
    resultList = recommendationController.getUsers()
    return resultList

@router.get('/content')
def getContents(payload: content):
    resultList = recommendationController.getContents(payload.planetId, payload.tribeId)
    return resultList


@router.get('/interaction')
def getInteractions(payload: interaction):
    resultList = recommendationController.getInteractions(payload.contentList)
    return resultList

@router.post('/train')
def recommendationTraining(payload: recommendationTraining):
    resultList = recommendationController.getRecommendationResults(payload.userId, payload.modelName, payload.amount, payload.filterType, payload.filterId)
    return resultList