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


def _get_streamlit_input(
    name: str, arg_type: Type, default: Any, is_required: bool = False
):
    # Handle Literal types (which are Enums or fixed choices)
    if get_origin(arg_type) is Literal:
        choices = get_args(arg_type)
        if isinstance(choices[0], str):
            return st.selectbox(
                name,
                choices,
                index=choices.index(default),
                help="Required" if is_required else None,
            )
        elif isinstance(choices[0], bool):
            return st.checkbox(
                name, value=default, help="Required" if is_required else None
            )

    # Handle Optional types
    elif get_origin(arg_type) is Union and type(None) in get_args(arg_type):
        inner_type = [t for t in get_args(arg_type) if t is not type(None)][0]
        value = _get_streamlit_input(name, inner_type, default, is_required)
        return value if value != "" else None

    # Handle simple types
    if arg_type is str:
        return st.text_input(
            name, value=default, help="Required" if is_required else None
        )
    elif arg_type is bool:
        return st.checkbox(
            name, value=default, help="Required" if is_required else None
        )
    elif arg_type is int:
        return st.number_input(
            name, value=default, step=1, help="Required" if is_required else None
        )
    elif arg_type is float:
        return st.number_input(
            name, value=default, help="Required" if is_required else None
        )

    return None


def _parse_tap(tap_class: Tap) -> Dict[str, Tuple[Type, Any]]:
    results = {}
    obj: Tap = tap_class()
    default_value_dict = obj._get_class_dict()
    for name, arg_type in obj._annotations.items():
        default = default_value_dict.get(name)
        is_required = name not in default_value_dict
        results[name] = (arg_type, default, is_required)
    return results


def _streamlit_is_empty(arg_type: Type, value: Any) -> bool:
    if arg_type is str:
        return value is None or not value
    return value is None


def create_streamlit_ui(
    tap_class: Tap, required_warning: bool = True
) -> Dict[str, Any]:
    inputs = {}
    empty_args = []

    for name, (arg_type, default, is_required) in _parse_tap(tap_class).items():
        inputs[name] = _get_streamlit_input(name, arg_type, default)
        if is_required and _streamlit_is_empty(arg_type, inputs[name]):
            empty_args.append(name)
            if required_warning:
                st.warning(f"Field {name} is required but empty.")

    return inputs, empty_args


def create_pydantic_model(tap_class: Tap) -> BaseModel:
    fields = {}
    for name, (arg_type, default, _) in _parse_tap(tap_class).items():
        fields[name] = (arg_type, default)

    # Dynamically create Pydantic model
    pydantic_model = create_model(tap_class.__name__ + "Model", **fields)
    return pydantic_model


if __name__ == "__main__":
    from cli import MyTap

    my_tap = MyTap()
    print(parsed_dict := _parse_tap(my_tap))
