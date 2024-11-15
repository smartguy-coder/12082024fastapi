import json
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4


class BaseStorage(ABC):

    @abstractmethod
    def create_book(self, book: dict):
        pass

    @abstractmethod
    def get_books(self, skip: int = 0, limit: int = 10, search_param: str = ''):
        pass

    @abstractmethod
    def get_book_info(self, book_id: str):
        pass

    @abstractmethod
    def update_book(self, book_id: str, author: str):
        pass

    @abstractmethod
    def delete_book(self, book_id: str):
        pass


class JSONStorage(BaseStorage):
    def __init__(self):
        self.file_name = 'storage.json'

        my_file = Path(self.file_name)
        if not my_file.is_file():
            with open(self.file_name, mode='w', encoding='utf-8') as file:
                json.dump([], file, indent=4)

    def create_book(self, book: dict):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)

        book['id'] = uuid4().hex
        content.append(book)
        with open(self.file_name, mode='w', encoding='utf-8') as file:
            json.dump(content, file, indent=4)

    def get_books(self, skip: int = 0, limit: int = 10, search_param: str = ''):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)

        if search_param:
            data = []
            for book in content:
                if search_param in book['author']:
                    data.append(book)
            sliced = data[skip:][:limit]
            return sliced

        sliced = content[skip:][:limit]
        return sliced

    def get_book_info(self, book_id: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        for book in content:
            if book_id == book['id']:
                return book
        return {}

    def update_book(self, book_id: str, author: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        was_found = False
        for book in content:
            if book_id == book['id']:
                book['author'] = author
                was_found = True
                break
        if was_found:
            with open(self.file_name, mode='w', encoding='utf-8') as file:
                json.dump(content, file, indent=4)
        raise ValueError()

    def delete_book(self, book_id: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        was_found = False
        for book in content:
            if book_id == book['id']:
                content.remove(book)
                was_found = True
                break
        if was_found:
            with open(self.file_name, mode='w', encoding='utf-8') as file:
                json.dump(content, file, indent=4)
        raise ValueError()


storage = JSONStorage()
