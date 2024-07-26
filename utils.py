from typing import (
    Any,
    Literal,
    get_args,
    get_origin,
    Union,
    Dict,
    Type,
    Tuple,
)
import streamlit as st
from pydantic import create_model, BaseModel
from tap import Tap


def _get_streamlit_input(name: str, arg_type: Any, default: Any):
    # Handle Literal types (which are Enums or fixed choices)
    if get_origin(arg_type) is Literal:
        choices = get_args(arg_type)
        if isinstance(choices[0], str):
            return st.selectbox(name, choices, index=choices.index(default))
        elif isinstance(choices[0], bool):
            return st.checkbox(name, value=default)

    # Handle Optional types
    elif get_origin(arg_type) is Union and type(None) in get_args(arg_type):
        inner_type = [t for t in get_args(arg_type) if t is not type(None)][0]
        value = _get_streamlit_input(name, inner_type, default)
        return value if value != "" else None

    # Handle simple types
    if arg_type is str:
        return st.text_input(name, value=default)
    elif arg_type is bool:
        return st.checkbox(name, value=default)
    elif arg_type is int:
        return st.number_input(name, value=default, step=1)
    elif arg_type is float:
        return st.number_input(name, value=default)

    return None


def _parse_tap(tap_class: Tap) -> Dict[str, Tuple[Type, Any]]:
    results = {}
    obj = tap_class()
    class_dict = obj._get_class_dict()
    for name, arg_type in obj._annotations.items():
        default = class_dict.get(name)
        results[name] = (arg_type, default)
    return results


def create_streamlit_ui(tap_class: Tap) -> Dict[str, Any]:
    inputs = {}

    for name, (arg_type, default) in _parse_tap(tap_class).items():
        inputs[name] = _get_streamlit_input(name, arg_type, default)

    return inputs


def create_pydantic_model(tap_class: Tap) -> BaseModel:
    fields = {}
    for name, (arg_type, default) in _parse_tap(tap_class).items():
        fields[name] = (arg_type, default)

    # Dynamically create Pydantic model
    pydantic_model = create_model(tap_class.__name__ + "Model", **fields)
    return pydantic_model


if __name__ == "__main__":
    from cli import MyTap

    my_tap = MyTap()
    print(parsed_dict := _parse_tap(my_tap))
