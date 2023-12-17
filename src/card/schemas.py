from __future__ import annotations

from pydantic import BaseModel


class BackTextResponse(BaseModel):
    id: str
    title: str
    content: str


class CardResponse(BaseModel):
    id: int
    card_name: str
    card_type: str
    name: str
    corp_name: str
    logo: str
    background: str
    color_text: str
    color_background: str
    color_title: str
    text_left: str
    text_center: str
    text_right: str
    barcode: str
