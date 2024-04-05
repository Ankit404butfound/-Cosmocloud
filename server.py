import os
import motor.motor_asyncio

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import ReturnDocument
from fastapi.responses import Response
from fastapi import FastAPI, Body, HTTPException, status, Query

from models import StudentModel, UpdateStudentModel, StudentList, Optional

load_dotenv()  # Load environment variables from .env file

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["DSN"])
collection = client.college.get_collection("students")

app = FastAPI(title="Backend Intern Hiring Task",
    summary="A sample application for task to build a Library Management System.",
)


@app.post(
    "/students",
    response_description="A JSON response sending back the ID of the newly created student record.",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: StudentModel = Body(...)):
    """
    API to create a student in the system. All fields are mandatory and required while creating the student in the system.
    """
    new_student = await collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    
    return {
        "id": str(new_student.inserted_id)
    }


@app.get(
    "/students",
    response_model=StudentList,
    response_model_by_alias=False,
)
async def list_students(country: Optional[str] = Query(None, description="Filter students by country if given"),
                        age: Optional[int] = Query(None, description="Filter students by age if given"),):
    """
    An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.
    """
    query_json = {}
    if country:
        query_json["address.country"] = country
    if age:
        # Age greater than or equal to the given age
        query_json["age"] = {"$gte": age}

    students = await collection.find(query_json).to_list(length=100)
    return StudentList(data=students)


@app.get(
    "/students/{id}",
    response_description="JSON response with the student record.",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    """
    Fetch student
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=404, detail=f"Student {id} not found")
    if (
        student := await collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return StudentModel(name=student["name"], age=student["age"], address=student["address"])
    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.patch(
    "/students/{id}",
    status_code=status.HTTP_204_NO_CONTENT,

)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    """
    API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=404, detail=f"Student {id} not found")
    student = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    if len(student) >= 1:
        update_result = await collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return Response(status_code=204)
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.delete("/students/{id}", response_description="Delete a student")
async def delete_student(id: str):
    """
    Remove a single student record from the database.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=404, detail=f"Student {id} not found")
    delete_result = await collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return {}

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
