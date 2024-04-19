from fastapi import FastAPI, UploadFile, Form, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3 
import hashlib
from datetime import timedelta
from pydantic import BaseModel


class Token(BaseModel):
    refresh_token:str
    
    
con = sqlite3.connect("market.db", check_same_thread=False)
cur = con.cursor()


cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items(
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAt INTEGER NOT NULL 
            );
            """)


app = FastAPI()

#문자열을 bytes단위로 인코딩 
#hexdigest 값을 16진수 문자열로 바꿈 
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#secret은 access token을 어떻게 인코딩할지 정하는것
#secret이 노출되면 다른사람이 access token을 decoding할 수 있다. 
SECRET = "super-coding2"
manager = LoginManager(SECRET, '/login')

def find_id(token):
    con.row_factory = sqlite3.Row
    cur=con.cursor()
    row = cur.execute(f"""
                      SELECT * FROM tokens
                      WHERE refresh_token='{token}'
                      """).fetchone()
   

    return row["id"]
    
def delete_token(token):
    
    cur.execute(f"""
                DELETE FROM tokens 
                WHERE refresh_token='{token}'
                """)
    con.commit()
    
def make_access_token(id):
    user = query_user(id)
    
    access_token = manager.create_access_token(data={
        "sub":{
            "id":user["id"],
            "name":user["name"],
            "email":user["email"]
            
        }
    }, expires=timedelta(minutes=1))
    return {"access_token":access_token}

@app.post("/token")
def create_access_token(token_info:Token):
    token=token_info.refresh_token
   
    
    try:
        payload = manager._get_payload(token)
    
        id = find_id(token)
        access_token = make_access_token(id)
    except:
        delete_token(token)
        raise InvalidCredentialsException
    

    return access_token
    

#LoginManager가 key도 조회하기 때문에 아래 문구 추가
@manager.user_loader()
def query_user(data):
    #access_token은 sub로 한번 감싸주었기 때문에 string이 아니어 오류가 난다. 
    #data가 dict형태로 온다. 
    #일반적인 경우
    WHERE_STATEMENTS = f'id="{data}"'
    #access_token 으로 로그인 검증할때
    if type(data) == dict:
        WHERE_STATEMENTS= f'id="{data['id']}"'
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user = cur.execute(f"""
                       SELECT * FROM users 
                       WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user

@app.post("/login")
def login(id:Annotated[str, Form()],
          password:Annotated[str, Form()]):
    user = query_user(id)
    hash = hash_password(password)
    
    #sever status code 
    if not user:
        #401을 자동으로 생성해서 보내준다.
        raise InvalidCredentialsException
    elif hash != user['password']:
        raise InvalidCredentialsException
    
    #jwt
    access_token = manager.create_access_token(data={
        "sub": {
            "id":user["id"],
            "name":user["name"],
            "email":user["email"]
        }}, expires=timedelta(minutes=1))
    # from datetime import timedelta
    # timedelta(minutes=15) is defalut 
    refresh_token = manager.create_access_token(data={
        "sub":{
            "message": "this is refresh!"
        }},expires=timedelta(minutes=10))
    
    cur.execute(f"""
            INSERT INTO tokens(id, refresh_token)
            VALUES ('{user["id"]}', '{refresh_token}')
            """)  
    con.commit()
    
    
    
    return {"access_token":access_token, 
            "refresh_token":refresh_token}
    
    

@app.post("/signup")
def signup(id:Annotated[str, Form()],
           password:Annotated[str, Form()],
           name:Annotated[str, Form()],
           email:Annotated[str, Form()]):
    try:
        hash = hash_password(password)
        
        cur.execute(f"""
                    INSERT INTO users(id, name, email, password)
                    VALUES ('{id}', '{name}', '{email}', '{hash}')
                    """)
        con.commit()
    except:
        print("id가 이미 존재합니다.")
        return "401"

    return "200"


# title은 Form데이터 형식으로 문자열로 온다는 의미 
@app.post("/items")
async def create_itms(image:UploadFile, 
                title:Annotated[str, Form()], 
                price:Annotated[int, Form()],
                description:Annotated[str, Form()],
                place:Annotated[str, Form()],
                insertAt:Annotated[int, Form()],
                user=Depends(manager)):
    
    image_byte = await image.read()
    #python에서 사용하는 문자열에 변수를 넣는 f문자열 
    cur.execute(f"""
                INSERT INTO 
                items(title, image, price, description, place, insertAt)
                VALUES ('{title}','{image_byte.hex()}', {price}, '{description}', '{place}', {insertAt})
                """)
    con.commit()
    
    return "200"

@app.get("/items")
def read_items(user=Depends(manager)):# user가 인증된 상태에서만 이용 가능 
    # column도 가져옴 
    con.row_factory = sqlite3.Row
    
    cur=con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items;
                       """).fetchall()
    #rows = [[1,"의자"]] // column을 안가져 왔을 때 
    #->  [[["id", 1], ["title","의자"]...][]]
    
    #-> {[id:1, title:의자 ..][]} // dictionary 형태로 바꾼다.
   
    # -> jsonable_encoder로 json형태로 바꾼다.
    return JSONResponse(
        jsonable_encoder(dict(row) for row in rows)
        )
    
    

    
@app.get("/images/{item_id}")
def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image FROM items 
                              WHERE id={item_id}
                              """).fetchone()[0] # 껍대기를 벗기는 과정
    
    # bytes.fromhex() -> 16진수를 해석해서 bytes 형식으로 변환
    return Response(content=bytes.fromhex(image_bytes), media_type="image/*")
    





app.mount("/",StaticFiles(directory="frontend", html=True), name="frontend" )
