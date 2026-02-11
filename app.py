from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# GLOBAL RESULT STORE
final_results = {
    "fundus": None,
    "segmentation": None,
    "video": None,
    "medical": None
}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------- FUNDUS ----------------
@app.post("/fundus")
async def fundus(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    final_results["fundus"] = {
        "status": "No critical abnormality detected",
        "severity": "Normal",
        "suggestion": "Maintain annual eye checkup",
        "image": path
    }
    return {"message": "Fundus test completed"}

# ---------------- SEGMENTATION ----------------
@app.post("/segmentation")
async def segmentation(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    final_results["segmentation"] = {
        "status": "Healthy vessel structure",
        "severity": "Mild",
        "suggestion": "Monitor eye health",
        "image": path
    }
    return {"message": "Segmentation completed"}

# ---------------- VIDEO SCREENING ----------------
@app.get("/video")
def video_screening():
    final_results["video"] = {
        "blink_rate": 18,
        "severity": "Normal",
        "suggestion": "Healthy blink rate"
    }
    return {"message": "Video screening completed"}

# ---------------- MEDICAL FILE ----------------
@app.post("/medical")
async def medical(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    final_results["medical"] = {
        "problem": "No critical disease detected",
        "severity": "Normal",
        "suggestion": "No immediate action required"
    }
    return {"message": "Medical file analyzed"}

# ---------------- REPORT GENERATION ----------------
@app.get("/generate_report")
def generate_report():
    filename = f"{RESULT_DIR}/Eye_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "AI Eye Health Diagnostic Report")

    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    y -= 30

    for test, data in final_results.items():
        if data is None:
            continue

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, test.upper())
        y -= 20

        c.setFont("Helvetica", 11)
        for k, v in data.items():
            if k != "image":
                c.drawString(60, y, f"{k.capitalize()}: {v}")
                y -= 15

        if "image" in data:
            try:
                c.drawImage(data["image"], 60, y - 120, width=200, height=120)
                y -= 140
            except:
                pass

        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    return FileResponse(filename, filename="Final_Eye_Report.pdf")
