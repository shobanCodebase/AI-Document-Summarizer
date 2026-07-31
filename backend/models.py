from pydantic import BaseModel


class DocumentSummary(BaseModel):
    executive_summary: str
    bullet_points: list[str]
    key_takeaways: list[str]
    action_items: list[str]