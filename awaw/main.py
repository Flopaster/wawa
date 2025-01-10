from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Dish(BaseModel):
    id: int
    name: str
    description: str
    price: float

dishes_db = []

@app.get("/dishes/", response_model=List[Dish])
def get_dishes():
    return dishes_db

@app.get("/dishes/{dish_id}", response_model=Dish)
def get_dish(dish_id: int):
    for dish in dishes_db:
        if dish.id == dish_id:
            return dish
    raise HTTPException(status_code=404, detail="Dish not found")

@app.post("/dishes/", response_model=Dish)
def create_dish(dish: Dish):
    for existing_dish in dishes_db:
        if existing_dish.id == dish.id:
            raise HTTPException(status_code=400, detail="Dish with this ID already exists")
    dishes_db.append(dish)
    return dish

@app.put("/dishes/{dish_id}", response_model=Dish)
def update_dish(dish_id: int, updated_dish: Dish):
    for index, dish in enumerate(dishes_db):
        if dish.id == dish_id:
            dishes_db[index] = updated_dish
            return updated_dish
    raise HTTPException(status_code=404, detail="Dish not found")

@app.delete("/dishes/{dish_id}", response_model=dict)
def delete_dish(dish_id: int):
    for index, dish in enumerate(dishes_db):
        if dish.id == dish_id:
            dishes_db.pop(index)
            return {"message": "Dish deleted successfully"}
    raise HTTPException(status_code=404, detail="Dish not found")