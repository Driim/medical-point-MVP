def create_node_query(labels: list[str], params: dict[str, any]) -> str:
    pass


def update_node_query(labels: list[str], params: dict[str, any]) -> str:
    pass


def transform_to_dict(dto: any) -> dict[str, any]:
    dict_with_empty: dict[str, any] = dto.__dict__
    result: dict[str, any] = {}

    for key, value in dict_with_empty.items():
        if value is not None:
            result[key] = value

    return result
