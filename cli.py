from typing import Optional, Literal
from tap import Tap


class MyTap(Tap):
    name: str
    age: int
    optional_field: Optional[str] = None
    choice: Literal["Option1", "Option2", "Option3"] = "Option1"
    agree: bool = False


if __name__ == "__main__":
    # python cli.py --name "David" --age 87
    my_tap = MyTap()
    args = my_tap.parse_args()
    print(args)
    print(my_tap.get_reproducibility_info())

    import os
    import json
    from tap.utils import define_python_object_encoder

    # Equivalent args.save()
    arg_log = args.as_dict()
    arg_log["reproducibility"] = args.get_reproducibility_info(
        repo_path=os.path.dirname(os.path.abspath(__file__))
    )
    print(
        json.dumps(
            arg_log,
            indent=4,
            sort_keys=True,
            cls=define_python_object_encoder(skip_unpicklable=True),
        )
    )

    print(my_tap._annotations)

    import ipdb

    ipdb.set_trace()
