from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deta import Deta
from datetime import date
from typing import Optional
import re


deta = Deta()

db = deta.Base("test_details")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TestDetails(BaseModel):
    question_id: int
    question: str
    op1: str
    op2: str
    op3: str
    op4: str
    ans: int

class UpdatedTestDetails(BaseModel):
    question: str=None
    op1: str=None
    op2: str=None
    op3: str=None
    op4: str=None
    ans: int=None

@app.get("/")
async def read_root():
    return {"greetings": "Welcome to the Testing API!"}

@app.get("/testdetails")
async def get_test_details():
    '''
    Fetch all the tests details
    '''
    return next(db.fetch())

@app.get("/testdetails/question_id/{question_id}") #alternative you don't need an endpoint to be speicified at all!
async def get_test_detail_by_no(question_id: int):
    '''
    Fetch test details by question id
    '''    
 
    json_item = next(db.fetch({"question_id":question_id}))

    return json_item

@app.post("/testdetails/")
async def add_test_details(test_details: TestDetails):
    '''
    Add test details by post request
    '''
    current_object_question_id = test_details.dict()["question_id"]
    json_item = next(db.fetch({"question_id":current_object_question_id}))
    if json_item:
        raise HTTPException(status_code=409, detail="Test with same question_id and date field exist")
    else:
        db.put(test_details.dict())
        return {"Success":"Successfully posted the question."}

@app.delete("/testdetails/question_id/{question_id}")
async def delete_test_details(question_id: int):
    '''
    Delete test details by question id
    '''    

    json_item = next(db.fetch({"question_id":question_id}))

    if json_item:
        for dictionary in json_item:
            db.delete(dictionary["key"])
        return {"task":"Deleted Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID/Date Field not found")

@app.put("/testdetails/question_id/{question_id}")
async def update_test_details(question_id: int, updated_test_details: UpdatedTestDetails):
    '''
    Update test details by question id and date
    '''
    json_item = next(db.fetch({"question_id":question_id}))
    if json_item == []:
        raise HTTPException(status_code=404, detail="Vehicle ID/Date Field not found")
    item_key = json_item[0]["key"]
    updated_dictionary_of_test_details = {k:v for k,v in updated_test_details.dict().items() if (v is not None)}
    db.update(updated_dictionary_of_test_details,item_key)
    return db.get(item_key)