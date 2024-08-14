from typing import (
    Any,
    Literal,
    get_args,
    get_origin,
    Union,
    Dict,
    Type,
    Tuple,
    get_type_hints,
)
import streamlit as st
from pydantic import create_model, BaseModel
from tap import Tap
from wtforms import StringField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm
import inspect
import datetime


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

    # Handle List, Set, and Tuple types
    elif get_origin(arg_type) in {list, set}:
        inner_type = get_args(arg_type)[0]
        choices = default if default else []
        if inner_type is str:
            text_area_result = st.text_area(
                name,
                value="\n".join(choices),
                help=(
                    "Required. (Per item per line.)"
                    if is_required
                    else "(Per item per line.)"
                ),
            )
            # NOTE: "".split("\n") is ['']
            return default if not text_area_result else text_area_result.split("\n")
        elif inner_type in {int, float}:
            text_area_result = st.text_area(
                name,
                value="\n".join(map(str, choices)),
                help=(
                    "Required. (Per item per line.)"
                    if is_required
                    else "(Per item per line.)"
                ),
            )
            return default if not text_area_result else text_area_result.split("\n")
        elif get_origin(inner_type) is Literal:
            choices = get_args(inner_type)
            return st.multiselect(name, choices, default=default)
        else:
            st.warning(f"Unknown inner_type of {name} {arg_type}")

    elif get_origin(arg_type) is tuple:
        inner_types = get_args(arg_type)
        if len(inner_types) == 2 and inner_types[1] is ...:
            return st.text_area(
                name,
                value=", ".join(map(str, default if default else [])),
                help=(
                    "Required. (Items should be separated by `, `.)"
                    if is_required
                    else "(Items should be separated by `, `.)"
                ),
            ).split(", ")
        else:
            return tuple(
                _get_streamlit_input(
                    f"{name}[{i}]", t, default[i] if default else None, is_required
                )
                for i, t in enumerate(inner_types)
            )

    # Handle simple types
    if arg_type is str:
        try:
            # Try to see if a string is a "isoformat date"
            date = datetime.date.fromisoformat(default)
            return st.date_input(name, value=date, help="Required" if is_required else None).isoformat()
        except:
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
        if default:
            default = float(default)
            decimal_places_length = len("{:f}".format(default).split(".", 1)[1])
            if decimal_places_length <= 2:
                step = 0.01
                format_str = "%0.2f"
            else:
                step = 10**-decimal_places_length
                # format_str = f"%0.{decimal_places_length}f"
                # https://stackoverflow.com/questions/6913532/display-a-decimal-in-scientific-notation
                format_str = f"%0.E"
        else:
            step = None
            format_str = None
        return st.number_input(
            name,
            value=default,
            step=step,
            format=format_str,
            help="Required" if is_required else None,
        )

    return None


# NOTE: actually they can be combine into single try except..., but let's leave it as what it is...
def _parse_tap_class(tap_class: Type[Tap]) -> Dict[str, Tuple[Type, Any]]:
    results = {}
    obj: Tap = tap_class()
    default_value_dict = obj._get_class_dict()
    for name, arg_type in obj._annotations.items():
        default = default_value_dict.get(name)
        is_required = name not in default_value_dict
        results[name] = (arg_type, default, is_required)
    return results


def _parse_tap_obj(tap_obj: Tap) -> Dict[str, Tuple[Type, Any]]:
    results = {}
    default_value_dict = tap_obj._get_class_dict()
    for name, arg_type in tap_obj._annotations.items():
        try:
            # Already parse_args
            default = getattr(tap_obj, name)
            is_required = False
        except AttributeError:
            # Fallback to raw one
            default = default_value_dict.get(name)
            is_required = name not in default_value_dict
        results[name] = (arg_type, default, is_required)
    return results


def _parse_tap(tap_class_or_obj: Union[Type[Tap], Tap]) -> Dict[str, Tuple[Type, Any]]:
    if isinstance(tap_class_or_obj, type(Tap)):
        return _parse_tap_class(tap_class_or_obj)
    elif isinstance(tap_class_or_obj, Tap):
        return _parse_tap_obj(tap_class_or_obj)
    else:
        raise NotImplementedError(f"Unknown type {type(tap_class_or_obj)}.")


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
    for name, (arg_type, default, is_required) in _parse_tap(tap_class).items():
        fields[name] = (arg_type, ... if is_required else default)

    # Dynamically create Pydantic model
    pydantic_model = create_model(tap_class.__name__ + "Model", **fields)
    return pydantic_model


def create_pydantic_model_from_func(func: callable) -> Type[BaseModel]:
    type_hints = get_type_hints(func)
    fields = {}
    for param_name, param_type in type_hints.items():
        if param_name != "return":
            default = inspect.signature(func).parameters[param_name].default
            if default is inspect.Parameter.empty:
                fields[param_name] = (param_type, ...)
            else:
                fields[param_name] = (param_type, default)
    return create_model("DynamicModel", **fields)


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
    from cli import MyTap, tap_func

    print(parsed_dict := _parse_tap(MyTap))

    # NOTE: must set required arguments otherwise will throw error pydantic_core._pydantic_core.ValidationError
    print(pydantic_model1 := create_pydantic_model(MyTap))
    print(pydantic_model1(name="David", age=87).model_dump_json())

    print(pydantic_model2 := create_pydantic_model_from_func(tap_func))
    print(pydantic_model2(name="David", age=87).model_dump_json())

    print(parsed_obj_dict := _parse_tap_obj(obj := MyTap()))
    print(
        parsed_obj_dict_init := _parse_tap_obj(
            obj := MyTap().parse_args(["--name", "David", "--age", "87"])
        )
    )

    import ipdb

    ipdb.set_trace()
