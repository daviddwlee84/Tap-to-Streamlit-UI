from typing import Optional, Annotated, Literal, Tuple, List
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
    choice: Literal["Option1", "Option2", "Option3"] = Query("Option1"),
    agree: Optional[bool] = Query(False),
    coordinates: Optional[str] = Query("0.0,0.0"),
    optional_list: Optional[str] = Query(None),
    multiselect_list: Optional[str] = Query(
        None,
        # examples=["Choice 1", "Choice 2", "Choice 3"],
        description='["Choice 1", "Choice 2", "Choice 3"]',
    ),
    default_multiselect_list: Optional[str] = Query(
        "Selection 1,Selection 2",
        # examples=["Selection 1", "Selection 2", "Selection 3"],
        description='["Selection 1", "Selection 2", "Selection 3"]',
    ),
):
    return MyTapModel(
        name=name,
        age=age,
        optional_field=optional_field,
        choice=choice,
        agree=agree,
        coordinates=(
            tuple(float(x) for x in coordinates.split(","))
            if coordinates
            else (0.0, 0.0)
        ),
        optional_list=optional_list.split(",") if optional_list else [],
        multiselect_list=multiselect_list.split(",") if multiselect_list else [],
        default_multiselect_list=(
            default_multiselect_list.split(",") if default_multiselect_list else []
        ),
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
    choice: Literal["Option1", "Option2", "Option3"] = Form("Option1"),
    agree: Optional[bool] = Form(False),
    # BUG: not converting string to float
    # coordinates: Tuple[float, float] = Form((0.0, 0.0)),
    optional_list: List[str] = Form([]),
    # BUG: cannot multi-select
    multiselect_list: List[Literal["Choice 1", "Choice 2", "Choice 3"]] = Form(
        [],
    ),
    # BUG: UI not showing default value correctly
    # default_multiselect_list: Optional[
    #     List[Literal["Selection 1", "Selection 2", "Selection 3"]]
    # ] = Form(["Selection 1", "Selection 2"]),
):
    # https://github.com/fastapi/fastapi/issues/562
    # https://github.com/pydantic/pydantic/issues/1350
    model = MyTapModel(
        name=name,
        age=age,
        optional_field=optional_field,
        choice=choice,
        agree=agree,
        # coordinates=[float(item) for item in coordinates],
        optional_list=optional_list,
        multiselect_list=multiselect_list,
        # default_multiselect_list=default_multiselect_list,
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
