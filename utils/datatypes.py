from pydantic import BaseModel
from typing import List
from enum import Enum

class Job(BaseModel):
    id: str
    status: str
    inputs: List[dict]
    outputs: List[dict]
    tags: dict