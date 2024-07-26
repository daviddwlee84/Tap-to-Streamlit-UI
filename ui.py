import streamlit as st
from utils import create_streamlit_ui, create_pydantic_model
from cli import MyTap

st.title("Streamlit Tap Converter")

# Create the Streamlit UI based on the Tap class
inputs = create_streamlit_ui(MyTap)

# Display the input dictionary
st.write("Input Values")
st.write(inputs)

# Create and display the Pydantic model based on the Tap class
PydanticModel = create_pydantic_model(MyTap)
st.write("Pydantic Model Schema")
st.json(PydanticModel.model_json_schema())
