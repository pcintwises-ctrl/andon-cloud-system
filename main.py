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

# ตัวแปรเก็บข้อมูลในแรม (Memory) - ข้อมูลจะรีเซ็ตถ้า Server หลับ
# เหมาะสำหรับทดสอบระบบ Andon เบื้องต้น
active_alerts = []

class PartRequest(BaseModel):
    mac_address: str
    status: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # หน้าจอ Dashboard สำหรับคนดู
    return templates.TemplateResponse("index.html", {"request": request, "alerts": active_alerts})

@app.post("/api/request_part")
async def request_part(data: PartRequest):
    # รับข้อมูลจาก ESP32
    if data.mac_address not in active_alerts:
        active_alerts.append(data.mac_address)
        print(f"🚨 ALERT: Machine {data.mac_address} needs parts!")
    return {"message": "Success", "current_queue": active_alerts}

@app.get("/api/check_alert")
async def check_alert():
    # ESP32 จะมายิงถามที่นี่เพื่อดูว่า "ของมาส่งหรือยัง?"
    return active_alerts

@app.post("/api/clear_alert")
async def clear_alert(data: dict):
    # ปุ่มบนหน้าเว็บสำหรับคนสโตร์กดเพื่อเคลียร์คิว
    mac = data.get("mac_address")
    if mac in active_alerts:
        active_alerts.remove(mac)
    return {"status": "cleared"}

if __name__ == "__main__":
    # ใช้ Port จาก Environment Variable ที่ Render กำหนดให้ (ถ้าไม่มีให้ใช้ 10000)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)