#This file receives the request, calls a function from another file, and returns the final JSON response to the user.
from fastapi import FastAPI

app = FastAPI(title="GitPulse")

@app.get("/")
def health():
    return {"status" : "ok","message":"GitPulse is running"}  

