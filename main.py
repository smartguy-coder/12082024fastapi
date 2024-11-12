from fastapi import FastAPI, Query

app = FastAPI(
    description='First site'
)


@app.get('/')
def index():
    return {'status': 200}


@app.get('/book/{book_id}')
def with_path_param_int(book_id: int):
    return {'book_id': book_id}


@app.get('/book/')
def with_query_param(info: str = Query(title='some_info', default='def')):
    return {'params': info}
