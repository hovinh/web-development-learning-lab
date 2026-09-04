"""Book routes, as a flask-smorest Blueprint of MethodView resources.

Same conversion as resources/authors.py's docstring describes. The one
piece of validation that flask-smorest's schema-driven `@blp.arguments`
*can't* express - that `author_id` must point at a real Author, not just
be an int - stays as an explicit check in each write method below,
same as it was in the original app.py.
"""

from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models import Author, Book, db
from schemas import BookSchema

blp = Blueprint(
    "Books",
    __name__,
    url_prefix="/api/books",
    description="Create, read, update, and delete books.",
)


def _check_author_exists(author_id: int) -> None:
    if db.session.get(Author, author_id) is None:
        abort(400, message=f"No author with id {author_id}")


@blp.route("")
class BookList(MethodView):
    @blp.response(200, BookSchema(many=True))
    def get(self):
        """List all books."""
        return Book.query.order_by(Book.id).all()

    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, book_data: dict):
        """Create a book."""
        _check_author_exists(book_data["author_id"])
        book = Book(
            title=book_data["title"],
            published_year=book_data["published_year"],
            author_id=book_data["author_id"],
        )
        db.session.add(book)
        db.session.commit()
        return book


@blp.route("/<int:book_id>")
class BookDetail(MethodView):
    @blp.response(200, BookSchema)
    def get(self, book_id: int):
        """Get one book by id."""
        return db.get_or_404(Book, book_id, description=f"No book with id {book_id}")

    @blp.arguments(BookSchema)
    @blp.response(200, BookSchema)
    def put(self, book_data: dict, book_id: int):
        """Replace a book's fields."""
        book = db.get_or_404(Book, book_id, description=f"No book with id {book_id}")
        _check_author_exists(book_data["author_id"])
        book.title = book_data["title"]
        book.published_year = book_data["published_year"]
        book.author_id = book_data["author_id"]
        db.session.commit()
        return book

    @blp.response(204)
    def delete(self, book_id: int):
        """Delete a book."""
        book = db.get_or_404(Book, book_id, description=f"No book with id {book_id}")
        db.session.delete(book)
        db.session.commit()
