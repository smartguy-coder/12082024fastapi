import json
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from storage import storage


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')


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


fake_db_users = [
    {
        'username': 'alex',
        'password': 'admin',
        'is_admin': True,
        'token': 'eb038beaac3f45de8831b9a584da1218',
    },
    {
        'username': 'alice',
        'password': 'secret',
        'is_admin': False,
        'token': 'eb038beafc3f45de8831b9a584da1210',
    },
]


class User(BaseModel):
    username: str
    is_admin: bool
    token: str
    password: str


@app.post('/api/token')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user_dict = {}
    for user in fake_db_users:
        found_user = user['username'] == form_data.username
        if found_user:
            user_dict = user
            break
    if not user_dict:
        raise HTTPException(status_code=400, detail='Incorrect username or password')

    user = User(**user_dict)
    password = form_data.password
    if password != user.password:
        raise HTTPException(status_code=400, detail='Incorrect username or password')

    return {'access_token': user.token, 'token_type': 'bearer'}


def get_user_by_token(token: str, is_admin: bool = False) -> User:
    user = None
    for user_data in fake_db_users:
        if token == user_data['token']:
            if is_admin:
                if not user_data['is_admin']:
                    raise HTTPException(status_code=403, detail='You do not have enough permissions')
            user = User(**user_data)
            break
    if not user:
        raise HTTPException(status_code=403, detail='Invalid credentials')

    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    user = get_user_by_token(token)
    return user


def get_current_user_admin(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    user = get_user_by_token(token, is_admin=True)
    return user


@app.post('/api/create', status_code=status.HTTP_201_CREATED)
def create_book(book: NewBook, admin_user: Annotated[User, Depends(get_current_user_admin)]) -> SavedBook:
    created_book = storage.create_book(json.loads(book.json()))
    return created_book


@app.get('/api/get-books/')
def get_books(any_user: Annotated[User, Depends(get_current_user)], skip: int = Query(default=0, ge=0),
              limit: int = Query(default=10, gt=0),
              search_param: str = '', ) -> list[
    SavedBook]:
    saved_books = storage.get_books(skip, limit, search_param)
    return saved_books


@app.get('/api/get-books/{book_id}')
def get_book(book_id: str, any_user: Annotated[User, Depends(get_current_user)]) -> SavedBook:
    saved_book = storage.get_book_info(book_id)
    return saved_book


@app.delete('/api/get-books/{book_id}')
def delete_book(book_id: str, admin_user: Annotated[User, Depends(get_current_user_admin)]) -> dict:
    storage.delete_book(book_id)
    return {}


@app.patch('/api/get-books/{book_id}')
def update_book(book_id: str, author: str, admin_user: Annotated[User, Depends(get_current_user_admin)]) -> SavedBook:
    book = storage.update_book(book_id, author=author)
    return book


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run('main:app', reload=True, host='127.0.0.1', port=5000)
