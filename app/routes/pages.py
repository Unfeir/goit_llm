from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from conf.config import get_settings
# from fastapi.templating import Jinja2Templates
# from fastapi import Request
#
credentials_paths = get_settings()
#
templates = Jinja2Templates(directory=credentials_paths.path_templates)

router = APIRouter(
    prefix="/pages",
    tags=["Pages"]
)

# templates = Jinja2Templates(directory="templates")


@router.get("/index")
def get_index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/signup")
def get_index_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login")
def get_index_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/upload")
def get_index_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/chat")
def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
