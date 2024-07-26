from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Input, Button, Checkbox, Select, Pretty
import requests

API_URL = "http://127.0.0.1:8888/submit"


class FastAPIRequestTester(App):
    # CSS_PATH = "static/css/style.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        # ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("FastAPI Request Tester", id="header")
        yield Input(placeholder="Name", id="name")
        yield Input(placeholder="Age", id="age", type="number")
        yield Input(placeholder="Optional Field", id="optional_field")
        yield Select(
            id="choice",
            options=[
                ("Option1", "Option1"),
                ("Option2", "Option2"),
                ("Option3", "Option3"),
            ],
            value="Option1",  # NOTE: force default value
        )
        yield Checkbox("Agree", id="agree")
        yield Horizontal(
            Button("Send POST JSON", id="post_json"),
            Button("Send GET Request", id="get_request"),
            Button("Send POST Form", id="post_form"),
        )
        yield Pretty("(waiting to submit)", id="response")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        name = self.query_one("#name", Input).value
        age = self.query_one("#age", Input).value
        optional_field = self.query_one("#optional_field", Input).value
        choice = self.query_one("#choice", Select).value
        agree = self.query_one("#agree", Checkbox).value

        data = {
            "name": name,
            "age": int(age) if age else None,
            "optional_field": optional_field,
            "choice": choice if choice != Select.BLANK else None,
            "agree": agree,
        }
        print(data)

        if event.button.id == "post_json":
            response = requests.post(API_URL, json=data)
        elif event.button.id == "get_request":
            response = requests.get(API_URL, params=data)
        elif event.button.id == "post_form":
            response = requests.post(f"{API_URL}-form", data=data)

        if response.ok:
            self.query_one("#response", Pretty).update(response.json())
        else:
            self.query_one("#response", Pretty).update(f"Error: {response.status_code}")


if __name__ == "__main__":
    FastAPIRequestTester().run()
