from fastapi.templating import Jinja2Templates
from pathlib import Path

#set up templates
templates_dir = Path(__file__).resolve().parent / "templates"
if not templates_dir.exists():
    raise FileNotFoundError(f"Templates directory {templates_dir} does not exist.")
templates = Jinja2Templates(directory=templates_dir)