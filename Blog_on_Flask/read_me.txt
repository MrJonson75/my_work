flask db migrate -m "users table"
flask db upgrade




is_authenticated: свойство, которое возвращает значение True если у пользователя действительные учетные данные или False в ином случае.

is_active: свойство, которое возвращает значение, True если учетная запись пользователя активна или False в ином случае.

is_anonymous: свойство, которое возвращает False для обычных пользователей и True только для специального анонимного пользователя.

get_id(): метод, который возвращает уникальный идентификатор пользователя в виде строки.





posts = db.session.scalars(current_user.following_posts()).all()

Метод following_posts класса User возвращает объект запроса SQLAlchemy,
который настроен для получения записей, которые интересуют пользователя,
из базы данных. После выполнения этого запроса и вызова all() для объекта
 результатов переменная posts определяется списком со всеми результатами.



users = db.session.scalars(query).all()

Вот еще один способ выполнения запросов. Если вы знаете id пользователя, вы можете получить этого пользователя следующим образом:

u = db.session.get(User, 1)


печать автора и текста сообщения для всех сообщений

>>> query = sa.select(Post)
>>> posts = db.session.scalars(query)
>>> for p in posts:
...     print(p.id, p.author.username, p.body)


получить всех пользователей, имена которых начинаются на "s".

>>> query = sa.select(User).where(User.username.like('s%'))
>>> db.session.scalars(query).all()


>>> from app import app, db
>>> from app.models import User, Post
>>> import sqlalchemy as sa
>>> app.app_context().push()


set FLASK_DEBUG=1


    query = sa.select(Post).where(Post.slug.like(slug))
    posts = db.session.scalars(query)


удаление объекта
def delete(name: str) -&gt; UserBase:
	with Session(engine) as session:
		statement = select(UserBase).where(UserBase.name == name)
		object = session.scalars(statement).one()

		session.delete(object)
		session.commit()
		return object


	Обновление объекта
def update(new_object: UserBase) -> None:
	with Session(engine) as session:
		session.merge(new_object)
		session.commit()

update(new_joe)