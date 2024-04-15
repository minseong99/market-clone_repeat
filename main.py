from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from typing import Annotated
import sqlite3 

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



# title은 Form데이터 형식으로 문자열로 온다는 의미 
@app.post("/items")
async def create_itms(image:UploadFile, 
                title:Annotated[str, Form()], 
                price:Annotated[int, Form()],
                description:Annotated[str, Form()],
                place:Annotated[str, Form()],
                insertAt:Annotated[int, Form()]):
    
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
def read_items():
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
