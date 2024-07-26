# Tap to Streamlit UI & API

Goal: Having same experience using CLI, API, and WebUI

Converter for Python Typed Argument Parser (Tap) to create Streamlit UI and Pydantic Model to create equivalent experience cross CLI, GUI (Web), and API

## Getting Started

```bash
pip install -r requirements.txt
```

CLI

```bash
python cli.py --name "David" --age 87python cli.py
```

API

```bash
fastapi dev .\api.py --port 8888
```

Web UI

```bash
# Streamlit
streamlit run ui.py
# Flask
flask --app ui2 --debug run --port 8889
```
