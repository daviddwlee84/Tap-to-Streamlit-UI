from typing import Optional, Union
from fastapi import FastAPI, Query, Form, Depends
from pydantic import BaseModel
from cli import MyTap
from utils import create_pydantic_model

MyTapModel = create_pydantic_model(MyTap)

app = FastAPI()


# Helper function to extract query parameters as MyTapModel
def get_model_from_query(
    name: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    optional_field: Optional[Union[str, None]] = Query(None),
    choice: str = Query("Option1"),
    agree: bool = Query(False),
):
    return MyTapModel(
        name=name, age=age, optional_field=optional_field, choice=choice, agree=agree
    )


@app.post("/submit", response_model=MyTapModel)
async def submit_post(model: BaseModel):
    return model


@app.get("/submit", response_model=MyTapModel)
async def submit_get(model: BaseModel = Depends(get_model_from_query)):
    return model


@app.post("/submit-form", response_model=MyTapModel)
async def submit_form(
    name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    optional_field: Optional[Union[str, None]] = Form(None),
    choice: str = Form("Option1"),
    agree: bool = Form(False),
):
    model = MyTapModel(
        name=name, age=age, optional_field=optional_field, choice=choice, agree=agree
    )
    return model
