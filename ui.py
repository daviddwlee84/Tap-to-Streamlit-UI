import streamlit as st
from utils import create_streamlit_ui, create_pydantic_model
from cli import MyTap

st.title("Streamlit Tap Converter")

with st.expander("Pydantic Model"):
    # Create and display the Pydantic model based on the Tap class
    PydanticModel = create_pydantic_model(MyTap)
    st.write("Pydantic Model Schema")
    st.json(PydanticModel.model_json_schema())

allow_empty = st.checkbox("Allow Empty")

# Create the Streamlit UI based on the Tap class
inputs, empty_args = create_streamlit_ui(MyTap, required_warning=not allow_empty)

# Display the input dictionary
st.write("Input Values")
st.write(inputs)

if not allow_empty and empty_args:
    st.warning(
        f"Missing {len(empty_args)} required arguments: {empty_args}. Fill to continue."
    )

if st.button("Continue", disabled=bool(empty_args) and not allow_empty):
    st.text("You continued!")
