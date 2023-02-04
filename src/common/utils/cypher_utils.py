def prepare_create_query(
    parent_labels: list[str],
    parent_param: str,
    node_labels: list[str],
    params: dict,
    relation: str,
) -> str:
    query = f"MATCH (p:{'|'.join(parent_labels)} {{id: ${parent_param} }})"
    query += " CREATE (o:" + "|".join(node_labels) + " { "

    lines = ["id: randomUUID()"]
    for key in params:
        lines.append(f"{key}: ${key}")

    query += ", ".join(lines)
    query += "})-[r:" + relation + "]->(p)"

    return query


def prepare_delete_query(node_labels: list[str]) -> str:
    return f"MATCH (o:{'|'.join(node_labels)} {{ id: $id }}) SET o.deleted = true"


def prepare_save_query(node_labels: list[str], relation: str, params: dict) -> str:
    query = f"MATCH (o:{'|'.join(node_labels)} {{ id: $id }})-[r:{relation}]->(p) SET "

    lines = []
    for key in params:
        lines.append(f"o.{key} = ${key}")

    query += ", ".join(lines)

    return query


def prepare_get_by_id_query(node_labels: list[str], relation: str) -> str:
    query = (
        f"MATCH (o:{'|'.join(node_labels)} {{id: $id}})-[r:{relation}]->(p)"
        + " WHERE o.deleted IS NULL"
    )

    return query


def prepare_find_query(
    parent_labels: list[str],
    node_labels: list[str],
    relation: str,
    lines: list[str],
) -> str:
    query = f"MATCH (p:{'|'.join(parent_labels)}) WHERE p.id IN $available_ou "
    query += f"MATCH (o:{'|'.join(node_labels)})-[:{relation}]->()-[:CHILD_OF*0..10]->(p)"  # 1 to 10 hops

    query += " WHERE o.deleted IS NULL "
    if lines:
        query += " ".join(lines)

    return query
