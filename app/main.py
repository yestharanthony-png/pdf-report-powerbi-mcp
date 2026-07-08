from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import home, report

app = FastAPI(
    title="AI Business Report Generator",
    description="MCP-powered Business Intelligence Application",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

# Static folder (CSS, JS, Images, Charts)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# Generated reports/charts (optional)
app.mount(
    "/generated",
    StaticFiles(directory="generated"),
    name="generated"
)

app.include_router(home.router)
app.include_router(report.router)

@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "application": "AI Business Report Generator",
        "version": "1.0.0"
    }