from pydantic import BaseModel, Field


class GraphSettings(BaseModel):
    """
    Settings for the Neo4j graph store provider.
    """

    uri: str = Field(..., description="The connection URI for the Neo4j database.")
    user: str = Field(..., description="The user name for authentication.")
    password: str = Field(..., description="The password for the specified user.")


class VectorSettings(BaseModel):
    """
    Settings for the Weaviate vector store provider.
    """

    url: str = Field(..., description="The URL for the Weaviate instance.")


class StoreSettings(BaseModel):
    """
    Central settings for all data store providers.
    """

    graph: GraphSettings
    vector: VectorSettings
