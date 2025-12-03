from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ClassifiedData:
    text: str
    source_path: str
    category: str = "uncategorized"
    tags: List[str] = field(default_factory=list)


@dataclass
class EnrichedData(ClassifiedData):
    entities: Dict[str, List[str]] = field(default_factory=dict)
    summary: str = ""
