from typing import Optional, Literal, Dict, Any, List, Set, Tuple
from tap import Tap, tapify


class MyTap(Tap):
    name: str
    age: int
    optional_field: Optional[str] = None
    choice: Literal["Option1", "Option2", "Option3"] = "Option1"
    agree: bool = False
    multiselect_list: List[Literal["Choice 1", "Choice 2", "Choice 3"]] = []
    default_multiselect_list: List[
        Literal["Selection 1", "Selection 2", "Selection 3"]
    ] = ["Selection 1", "Selection 3"]
    default_empty_list: List[int] = []
    default_empty_set: Set[str] = set()
    coordinates: Tuple[float, float] = (0.0, 0.0)
    optional_list: Optional[List[str]] = None
    optional_set: Optional[Set[int]] = None
    optional_tuple: Optional[Tuple[int, ...]] = None


def tap_func(
    name: str,
    age: int,
    optional_field: Optional[str] = None,
    choice: Literal["Option1", "Option2", "Option3"] = "Option1",
    agree: bool = False,
    items: List[str] = [],
) -> Dict[str, Any]:
    return dict(
        name=name,
        age=age,
        optional_field=optional_field,
        choice=choice,
        agree=agree,
        items=items,
        is_tap_func=True,
    )


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

    print(result := tapify(tap_func))

    import ipdb

    ipdb.set_trace()
