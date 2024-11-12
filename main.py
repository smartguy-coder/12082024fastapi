from fastapi import FastAPI

app = FastAPI(
    description='First site'
)


@app.get('/')
def index():
    return {'status': 200}
