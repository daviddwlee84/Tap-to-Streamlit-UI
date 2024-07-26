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
from wtforms import StringField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm


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


def create_pydantic_model(tap_class: Tap) -> Type[BaseModel]:
    fields = {}
    for name, (arg_type, default, _) in _parse_tap(tap_class).items():
        fields[name] = (arg_type, default)

    # Dynamically create Pydantic model
    pydantic_model = create_model(tap_class.__name__ + "Model", **fields)
    return pydantic_model


def _get_flask_input(
    name: str, arg_type: Type, default: Any, is_required: bool = False
):
    validators = [DataRequired() if is_required else Optional()]

    # Handle Literal types (which are Enums or fixed choices)
    if get_origin(arg_type) is Literal:
        choices = [(choice, choice) for choice in get_args(arg_type)]
        return SelectField(
            name, choices=choices, default=default, validators=validators
        )

    # Handle Optional types
    elif get_origin(arg_type) is Union and type(None) in get_args(arg_type):
        inner_type = [t for t in get_args(arg_type) if t is not type(None)][0]
        return _get_flask_input(name, inner_type, default, is_required)

    # Handle simple types
    if arg_type is str:
        return StringField(name, default=default, validators=validators)
    elif arg_type is bool:
        return BooleanField(name, default=default, validators=validators)
    elif arg_type is int:
        return IntegerField(name, default=default, validators=validators)
    elif arg_type is float:
        return IntegerField(name, default=default, validators=validators)

    return None


def create_flask_form_class(tap_class: Tap) -> Type[FlaskForm]:
    form_fields = {}

    for name, (arg_type, default, is_required) in _parse_tap(tap_class).items():
        form_field = _get_flask_input(name, arg_type, default, is_required)
        if form_field:
            form_fields[name] = form_field

    # Add submit buttons
    form_fields["submit_json"] = SubmitField("Send POST JSON")
    form_fields["submit_get"] = SubmitField("Send GET Request")
    form_fields["submit_form"] = SubmitField("Send POST Form")

    return type("DynamicForm", (FlaskForm,), form_fields)


if __name__ == "__main__":
    from cli import MyTap

    print(parsed_dict := _parse_tap(MyTap))

    # class MyTapModel(MyTap, BaseModel):
    #     pass

    print(pydantic_model1 := create_pydantic_model(MyTap))
    print(pydantic_model1().model_dump_json())

    import ipdb

    ipdb.set_trace()
