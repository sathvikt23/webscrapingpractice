from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
import uvicorn 
import authentication 
from fastapi.responses import HTMLResponse
from typing import *
app=FastAPI()
class data (BaseModel):
   name:str
   no:int 
class socketdata(BaseModel):
   username :str
   content:str

clients:List[WebSocket]=[]
@app.get("/")
def hello():
    return "Hello"
@app.post("/")
def hello2(data:data):
   return data.name

@app.get("/login")
def hello3():
   response = HTMLResponse(content="Login page")
   response.set_cookie(
            key="auth_token",
            value="blabla",
            httponly=True,
            samesite="lax",
            max_age=3600
        )
   return response
@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
   
   await websocket.accept()
   clients.append(websocket)
   try:
      while True :
         data = await websocket.receive_text()
         message=socketdata.parse_raw(data)
         for client in clients:
                await client.send_text(f"Broadcast from {message.username}: {message.content}")
   except WebSocketDisconnect:
      client.remove(websocket)
      
      
app.add_middleware(authentication.Commen)
#app.add_middleware(authentication.jwtauth)
if __name__=="__main__":
 uvicorn.run("app:app", host="0.0.0.0", port=8120, reload=True)

