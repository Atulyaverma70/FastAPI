from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal


app=FastAPI()


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of Patient",example='P001')]
    name: Annotated[str,Field(...,description="Name of the patient")]
    city: Annotated[str,Field(..., description="Name of the city")]
    age: Annotated[int,Field(...,gt=0, lt=120,description="Age of the patient")]
    gender: Annotated[Literal['male','female','other'],Field(..., description="gender of the patient")]
    height: Annotated[float, Field(...,gt=0,description="Height of the patient in mtrs")]
    weight: Annotated[float, Field(...,gt=0,description="Weight of the patient in kgs")]


    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight/(self.height**2),2)

        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return 'Underweight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Overweight'
        else:
            return 'Obese'
        



def load_data():
    with open('patients.json','r') as f:   # with is used for resource management, it ensures files are properly opened and automatically closed using context managers.”
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get("/") # making a route
def hello():
    return {'message': 'Patient management system API'}

@app.get('/about')
def about():
   return {'message':"A fully functional API to manage patients records"}

@app.get('/view')
def view():
    data=load_data()

    return data

# for path
@app.get('/patient/{patient_id}')
def view_patient(patient_id: str):
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='patient not found')

# for querry
@app.get('/sort')
def sort_patients(sort_by:str=Query(...,description='sort on the basis of height, weight, bmi'), order:str=Query('asc', description='sort in asc or desc order')):
    valid_fields=['height','weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid filed, select from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail='Invalid order selct from asc and desc')
    
    data=load_data()

    sort_order= True if order=='desc' else False

    sorted_data=sorted(data.values(), key=lambda x:x.get(sort_by,0), reverse=sort_order)

    return sorted_data
     

@app.post('/create')
def create_patient(patient:Patient):
    # loading existing data
    data=load_data()
    # check if patient already exist
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient already exist")
    
    # new patient add to database
    data[patient.id]=patient.model_dump(exclude=['id']) # by using "model_dump" converting pydantic object in dictionary

    # save data into json file

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patient created successfully'})