from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/echo")
async def read_headers(request: Request):
    headers = dict(request.headers)
    return headers

@app.get("/hello")
async def hello():
    return "hello"

@app.post("/echo")
async def echo_post(request_body: str):
    return request_body

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000,)
