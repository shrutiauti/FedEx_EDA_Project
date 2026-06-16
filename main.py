from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
import os
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

# pydatic model 

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique ID of the patient", examples=["P001"])]

    name: Annotated[str,Field(..., description="Name of the patient")]

    city: Annotated[str, Field(..., description="City where patient lives")]

    age: Annotated[int,Field(..., gt=0, lt=120, description="Age of the patient")]

    gender: Annotated[Literal['male', 'female', 'others'],Field(..., description="Gender of the patient")]

    height: Annotated[float,Field(..., gt=0, description="Height in meters")]

    weight: Annotated[float,Field(..., gt=0, description="Weight in kilograms") ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'under weight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'   # <-- you missed return earlier
        else:
            return 'Obese'

# pydantic model 2

class PatientUpdate(BaseModel):

    name: Annotated[Optional[str],Field(default=None)]

    city: Annotated[Optional[str], Field(default=None)]

    age: Annotated[Optional[int],Field(default=None, gt=0)]

    gender: Annotated[Optional[Literal['male', 'female', 'others']],Field(default=None)]

    height: Annotated[Optional[float],Field(default=None, gt=0)]

    weight: Annotated[Optional[float],Field(default=None, gt=0) ]


def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def home():
    return {"message": "Patient Management System API"}

@app.get("/view")
def view():
    data = load_data()
    return data

# path parameter : allow get specific record


@app.get('/patient/{patient_id}')
def view_patient(
    patient_id: str = Path(..., description='Id of the patient in DB', example='P001')
):
    data = load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code=404, detail='patient not found')

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='Sort by height, weight, bmi'),
    order: str = Query('asc', description='Sort in asc or desc order')
):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid field. Select from {valid_fields}'
        )

    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail='Invalid order. Select either asc or desc'
        )

    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by, 0),
        reverse=sort_order
    )

    return sorted_data


@app.post('/create')
def create_patient(patient: Patient):
        data =load_data()

        # check if patient already exist

        if patient.id in data :
            raise HTTPException(status_code=400, detail ='patient already exist')

        # new patient add to the database

        data[patient.id] = patient.model_dump(exclude=['id'])            # it convert pydantic obj to dict

        # save into the json file

        save_data(data)

        return JSONResponse(status_code=201, content={'msg':'patient created successfully'})

# update 

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update:PatientUpdate):

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail='patient not found')

    existing_patient = data[patient_id]

    updated_patient = patient_update.model_dump(exclude_unset=True)  # to update required field

    for key , value in updated_patient.items():
        existing_patient[key] = value

    # existing_patient -> pydantic obj -> updated bmi -> verdict -> pydantic obj -> dict

    existing_patient['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient)

    # pydantic obj -> dict

    existing_patient = patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data 

    data[patient_id] = existing_patient

    # save data

    save_data(data)


    data[patient_id] = existing_patient

    return JSONResponse(status_code=200, content={'msg':'Patient updated'})


    # delete

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data=load_data()

    if patient_id not in data :
        raise HTTPException(status_code=404, detail='patient not found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'msg':'patient deleted'})



    


    





    