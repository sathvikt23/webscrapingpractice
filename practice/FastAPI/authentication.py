from fastapi import FastAPI ,HTTPException,Request
from fastapi.responses import JSONResponse ,RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json 
import jwt 
import base64
class Commen(BaseHTTPMiddleware):
    async def dispatch(self,request:Request ,call_next):
        path=request.url.path
        auth_header =request.headers.get("Authorization")
        if (path.startswith("/") and path!="/login"):
            print("Enters middleware ")
            print("Autorization " ,auth_header)
            return await self.handle_user(request,call_next,auth_header)
        return JSONResponse(status_code=401,content={"message":"Not Authorized "})
        #return RedirectResponse(url="/login")
    def decode(self,auth_header):
        encoded=auth_header.split(" ")[1]
        decode=base64.b64decode(encoded)
        data = decode.decode("utf-8")
        print(data)
        username,pasword=data.split(":")
        return username,pasword

        
    async def handle_user(self ,request:Request,call_next,auth_header):
        username ,password=self.decode(auth_header)
        if username=="sathvik" and password=="123456":
            return await call_next(request)
        return JSONResponse(status_code=401,content={"message":"Not Authorized "})
        #return RedirectResponse(url="/login")
    
class jwtauth(BaseHTTPMiddleware): 
    async def dispatch(self, request:Request, call_next):
        path=request.url.path
        cookie =request.cookies.get("auth_token")
        print("In jwt verfication ",cookie)
        return await call_next(request)
    


