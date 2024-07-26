from typing import Optional, Annotated
from fastapi import FastAPI, Query, Form, Depends
from pydantic import BaseModel
from cli import MyTap, tap_func
from utils import create_pydantic_model, create_pydantic_model_from_func

MyTapModel = create_pydantic_model(MyTap)


tags_metadata = [
    {
        "name": "Convert From Tap Class",
        "description": "Showcase of getting equivalent API from Tap",
    },
    {
        "name": "Convert From Function",
        "description": "Showcase of converting any Python function to API",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


# Helper function to extract query parameters as MyTapModel
# NOTE: we can use _get_tap_model_params to convert this "annotation" from a Pydantic BaseModel
def get_model_from_query(
    name: str = Query(),
    age: int = Query(),
    optional_field: Optional[str] = Query(None),
    choice: Optional[str] = Query("Option1"),
    agree: Optional[bool] = Query(False),
):
    return MyTapModel(
        name=name, age=age, optional_field=optional_field, choice=choice, agree=agree
    )


# https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags
@app.post("/submit", response_model=MyTapModel, tags=["Convert From Tap Class"])
# NOTE: we need to pass the exact Pydantic data model. And we try to ignore warning "Variable not allowed in type expressionPylancereportInvalidTypeForm"
async def submit_post(model: MyTapModel):  # type: ignore
    # BUG: it won't fill "default value" automatically like the other two
    return model


@app.get("/submit", response_model=MyTapModel, tags=["Convert From Tap Class"])
# Equivalent
# async def submit_get(model: dict = Depends(get_model_from_query)):
async def submit_get(model: Annotated[str, Depends(get_model_from_query)]):
    return model


@app.post("/submit-form", response_model=MyTapModel, tags=["Convert From Tap Class"])
async def submit_form(
    name: str = Form(),
    age: int = Form(),
    optional_field: Optional[str] = Form(None),
    choice: Optional[str] = Form("Option1"),
    agree: Optional[bool] = Form(False),
):
    model = MyTapModel(
        name=name, age=age, optional_field=optional_field, choice=choice, agree=agree
    )
    return model


MyTapFuncModel = create_pydantic_model_from_func(tap_func)


# Dependencies Injection Trick to get Pydantic schema for depends for get request
# https://fastapi.tiangolo.com/tutorial/dependencies/
def _get_tap_model_params(model: BaseModel = Depends(MyTapFuncModel)) -> dict:
    return model.model_dump()


@app.post("/test-tap-func", tags=["Convert From Function"])
async def submit_func_post(model: MyTapFuncModel):  # type: ignore
    return tap_func(**model.model_dump())


@app.get("/test-tap-func", tags=["Convert From Function"])
async def submit_func_get(model: dict = Depends(_get_tap_model_params)):  # type: ignore
    return tap_func(**model)
