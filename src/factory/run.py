'''
    Uvicorn is a fast, lightweight ASGI (Asynchronous Server Gateway Interface) web server for Python, 
    used to run async web apps and APIs built with frameworks like FastAPI or Starlette, 
    handling network requests and sending responses efficiently using an event loop for high concurrency 
    and minimal overhead, supporting modern features like WebSockets and HTTP/2. 
'''

# run.py
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)