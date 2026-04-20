from pydantic import BaseModel

class Patient(BaseModel):
    name: str
    age: int

def insert_patient_detail(patient:Patient):
    print(patient.name)
    print(patient.age)

detail={'name':'Michel', 'age':'30'}

patient1=Patient(**detail)


insert_patient_detail(patient1)
