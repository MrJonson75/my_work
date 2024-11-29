from sqlalchemy.orm import Session
from schemas.blog import CreateBlog, UpdateBlog
from db.models.blog import Blog


def delete_blog(id: int, author_id: int, db: Session):
    blog_in_db = db.query(Blog).filter(Blog.id == id)
    if not blog_in_db.first():
        return {"error": f"Не удалось найти блог с id {id}"}
    if not blog_in_db.first().author_id == author_id:
        return {"error": f"Только автор может удалить блог"}
    blog_in_db.delete()
    db.commit()
    return {"msg": f"удаленный блог с Id {id}"}


def update_blog(id: int, blog: UpdateBlog, author_id: int, db: Session):
    """
    Метод Update блог
    :param id:
    :param blog:
    :param author_id:
    :param db:
    :return:
    """
    blog_in_db = db.query(Blog).filter(Blog.id == id).first()
    if not blog_in_db:
        return {"error": f"Блог с идентификатором {id} не существует"}
    if not blog_in_db.author_id == author_id:
        return {"error": f"Только автор может изменять блог"}
    blog_in_db.title = blog.title
    blog_in_db.content = blog.content
    db.add(blog_in_db)
    db.commit()
    return blog_in_db


