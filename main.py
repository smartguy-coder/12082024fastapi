import json
from enum import Enum

from fastapi import FastAPI, Query, status
from pydantic import BaseModel, Field

from storage import storage

app = FastAPI(
    description='First site'
)


class Genres(str, Enum):
    SCIENCE = 'science'
    HISTORY = 'history'
    BIOLOGY = 'biology'


class NewBook(BaseModel):
    title: str = Field(min_length=3, examples=['I, legend'])
    author: str
    price: float = Field(default=100, gt=0.0)
    cover: str
    tags: list[Genres] = Field(default=[], max_items=2)
    description: str


class SavedBook(NewBook):
    id: str = Field(examples=['40de287d36ab48d8a88572b8e98e7312'])


@app.get('/')
def index():
    return {'status': 200}


@app.post('/api/create', status_code=status.HTTP_201_CREATED)
def create_book(book: NewBook) -> SavedBook:
    created_book = storage.create_book(json.loads(book.json()))
    return created_book


@app.get('/api/get-books/')
def get_books(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, gt=0), search_param: str = '') -> list[
    SavedBook]:
    saved_books = storage.get_books(skip, limit, search_param)
    return saved_books


@app.get('/api/get-books/{book_id}')
def get_book(book_id: str) -> SavedBook:
    saved_book = storage.get_book_info(book_id)
    return saved_book


@app.delete('/api/get-books/{book_id}')
def delete_book(book_id: str) -> dict:
    storage.delete_book(book_id)
    return {}


@app.patch('/api/get-books/{book_id}')
def delete_book(book_id: str, author: str) -> SavedBook:
    book = storage.update_book(book_id, author=author)
    return book


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('main:app', reload=True, host='127.0.0.1', port=5000)
