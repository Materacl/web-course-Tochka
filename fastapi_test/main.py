from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.get("/echo")
async def echo_headers(request: Request):
    headers = dict(request.headers)
    return headers


@app.get("/hello")
async def hello():
    return {"message": "hello"}


@app.post("/echo")
async def echo_body(request: Request):
    body = await request.json()
    return body


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, )
