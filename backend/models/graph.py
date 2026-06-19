from pydantic import BaseModel


class GraphNeighbourhoodResponse(BaseModel):
    nodes: list[dict]
    links: list[dict]
