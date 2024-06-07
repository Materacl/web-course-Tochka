from datetime import date
from functools import cache
from pathlib import Path

import httpx
import pydantic
from fastapi import APIRouter, HTTPException
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent
from pydantic import BaseModel, Field, TypeAdapter

from .shared import demo_page

router = APIRouter()


class Film(BaseModel):
    id: int = Field(title='ID')
    title: str = Field(title='Title')
    description: str = Field(title='Description')


@cache
def films_list(films_json: str) -> list[Film]:
    films_adapter = TypeAdapter(list[Film])
    films = films_adapter.validate_json(films_json)
    films.sort(key=lambda film: film.id, reverse=True)
    return films


@router.get('', response_model=FastUI, response_model_exclude_none=True)
async def films_view(page: int = 1) -> list[AnyComponent]:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/films/?skip=0&limit=10")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching bookings")
        films = response.text

    page_size = 50
    films = films_list(films)
    print(films[(page - 1) * page_size: page * page_size])
    return demo_page(
        c.Table(
            data=films[(page - 1) * page_size: page * page_size],
            data_model=Film,
            columns=[
                DisplayLookup(field='id', table_width_percent=5),
                DisplayLookup(field='title', table_width_percent=33),
                DisplayLookup(field='description', table_width_percent=62),
            ],
        ),
        title='Films',
    )
