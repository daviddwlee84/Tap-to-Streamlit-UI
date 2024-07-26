import streamlit as st
from utils import create_streamlit_ui, create_pydantic_model
from cli import MyTap
import requests

# FastAPI endpoint URL
API_URL = "http://127.0.0.1:8888/submit"

st.set_page_config("Streamlit Tap Converter")
st.title("Streamlit Tap Converter")

allow_empty = st.checkbox("Allow Empty")

st.divider()

# Create the Streamlit UI based on the Tap class
inputs, empty_args = create_streamlit_ui(MyTap, required_warning=not allow_empty)

local_tap, api_tab = st.tabs(["Local", "API"])


with local_tap:
    st.caption(
        "With Local, you can run downstream task in Streamlit (not recommend since might restrict by multiprocessing)."
    )
    with st.expander("Pydantic Model"):
        # Create and display the Pydantic model based on the Tap class
        PydanticModel = create_pydantic_model(MyTap)
        st.write("Pydantic Model Schema")
        st.json(PydanticModel.model_json_schema())

    # Display the input dictionary
    st.write("Input Values")
    st.write(inputs)

    if not allow_empty and empty_args:
        st.warning(
            f"Missing {len(empty_args)} required arguments: {empty_args}. Fill to continue."
        )

    if st.button("Continue", disabled=bool(empty_args) and not allow_empty):
        st.text("You continued!")

with api_tab:
    st.caption("With API, you can do downstream task in FastAPI backend.")
    if st.button("Send POST JSON", disabled=bool(empty_args) and not allow_empty):
        response = requests.post(API_URL, json=inputs)
        if response.ok:
            st.json(response.json())
        else:
            st.error("Failed to get response from API")

    if st.button("Send GET Request", disabled=bool(empty_args) and not allow_empty):
        response = requests.get(API_URL, params=inputs)
        if response.ok:
            st.json(response.json())
        else:
            st.error("Failed to get response from API")

    if st.button("Send POST Form", disabled=bool(empty_args) and not allow_empty):
        response = requests.post(f"{API_URL}-form", data=inputs)
        if response.ok:
            st.json(response.json())
        else:
            st.error("Failed to get response from API")

    st.divider()
    st.link_button("API Document", API_URL.rsplit("/", 1)[0] + "/docs")
