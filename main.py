from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn
import os

app = FastAPI()

# ตั้งค่าโฟลเดอร์สำหรับ HTML
templates = Jinja2Templates(directory="templates")

# ตัวแปรเก็บข้อมูลในแรม (Memory)
active_alerts = []

class PartRequest(BaseModel):
    mac_address: str
    status: str

# เพิ่ม Model สำหรับตอนเคลียร์ข้อมูลด้วย
class ClearRequest(BaseModel):
    mac_address: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "alerts": active_alerts})

@app.post("/api/request_part")
async def request_part(data: PartRequest):
    if data.mac_address not in active_alerts:
        active_alerts.append(data.mac_address)
    return {"message": "Success", "current_queue": active_alerts}

@app.get("/api/check_alert")
async def check_alert():
    return active_alerts

@app.post("/api/clear_alert")
async def clear_alert(data: ClearRequest): # แก้ไขตรงนี้ให้ใช้ Model ที่ถูกต้อง
    if data.mac_address in active_alerts:
        active_alerts.remove(data.mac_address)
    return {"status": "cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
