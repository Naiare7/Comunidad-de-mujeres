# Importamos los modelos para que SQLAlchemy los descubra al crear las tablas.
# Sin este import, Base.metadata.create_all() no sabría qué tablas crear.

from app.models.user import User
from app.models.forum import Forum, Subforum
from app.models.thread import Thread
from app.models.reply import Reply
from app.models.thread_image import ThreadImage
from app.models.reply_image import ReplyImage
