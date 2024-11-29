from typing import Optional, Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Form, responses, status
from fastapi.security.utils import get_authorization_scheme_param
from starlette.exceptions import HTTPException

from db.models.blog import Blog
from db.models.user import User
from db.repository.blog import update_blog
from db.session import get_db
from schemas.blog import CreateBlog, UpdateBlog
from apis.v1.route_login import get_current_user
from db.repository.blog import delete_blog

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
def home(request: Request, alert: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        blogs = db.query(Blog).all()
        print(blogs)

        return templates.TemplateResponse(
            "blog/home.html", {"request": request, "blogs": blogs, "alert": alert}
        )
    except Exception as e:
        errors = ["что то пошло не так"]
        print("Ошибка", e)
    return templates.TemplateResponse(
        "blog/home.html",
        {"request": request, "errors": errors}, )


@router.get("/app/blog/{id}")
def blog_detail(request: Request, id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == id).first()
    return templates.TemplateResponse(
        "blog/detail.html", {"request": request, "blog": blog}
    )


@router.get("/app/create_blog")
def create_blog(request: Request):
    return templates.TemplateResponse("blog/create_blog.html", {"request": request})


@router.post("/app/create_blog")
def create_blog(request: Request,
                title: str = Form(...),
                content: str = Form(...),
                db: Session = Depends(get_db),
                ):
    token = request.cookies.get("access_token")
    _, token = get_authorization_scheme_param(token)
    try:
        author = get_current_user(token=token, db=db)
        slug = slugify(title)
        blog = Blog(
            title=title,
            slug=slug,
            content=content,
            author_id=author.id,
            is_active=True
        )
        db.add(blog)
        db.commit()
        db.refresh(blog)
        return responses.RedirectResponse(
            "/?alert=Blog Submitted for Review", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        errors = ["Пожалуйста, войдите, чтобы создать"]
        print("Ошибка", e)
        return templates.TemplateResponse(
            "blog/create_blog.html",
            {"request": request, "errors": errors, "title": title, "content": content},
        )


@router.get("/delete/{id}")
def delete_a_blog(request: Request, id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    _, token = get_authorization_scheme_param(token)
    try:
        author = get_current_user(token=token, db=db)
        msg = delete_blog(id=id, author_id=author.id, db=db)
        alert = msg.get("error") or msg.get("msg")
        return responses.RedirectResponse(
            f"/?alert={alert}", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(f"Ошибка {e}")
        blog = db.query(Blog).filter(Blog.id == id).first()
        return templates.TemplateResponse("blog/detail.html", {"request": request, "alert": "Авторизуйтесь",
                                                               "blog": blog})


@router.put("/blog/{id}")
def update_a_blog(request: Request, id: int, blog: Annotated[UpdateBlog, Form()], db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    blog = update_blog(id=id, blog=blog, author_id=current_user.id, db=db)
    if isinstance(blog, dict):
        raise HTTPException(
            detail=blog.get("error"),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return blog
