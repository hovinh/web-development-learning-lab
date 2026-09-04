"""Author routes, as a flask-smorest Blueprint of MethodView resources.

This replaces app.py's old plain @app.get/@app.post routes for
/api/authors. The behavior is the same as before, but flask-smorest's
`@blp.arguments`/`@blp.response` decorators do three things at once that
used to be separate, manual steps:

1. Validate the request body against AuthorSchema (was: the
   `try/except ValidationError` blocks) - a failure here now returns
   422 Unprocessable Entity with Marshmallow's field errors, which is
   flask-smorest's default for a body that doesn't match its schema
   (see tests/test_app.py's updated status-code expectations).
2. Serialize the returned model instance/list with AuthorSchema (was:
   the manual `jsonify(author_schema.dump(...))` calls).
3. Record the endpoint - its path, methods, request/response schemas -
   into the OpenAPI spec that Api (see app.py) turns into Swagger UI.
"""

from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from models import Author, db
from schemas import AuthorSchema

blp = Blueprint(
    "Authors",
    __name__,
    url_prefix="/api/authors",
    description="Create, read, update, and delete authors.",
)


@blp.route("")
class AuthorList(MethodView):
    @blp.response(200, AuthorSchema(many=True))
    def get(self):
        """List all authors."""
        return Author.query.order_by(Author.id).all()

    @blp.arguments(AuthorSchema)
    @blp.response(201, AuthorSchema)
    def post(self, author_data: dict):
        """Create an author."""
        author = Author(name=author_data["name"])
        db.session.add(author)
        db.session.commit()
        return author


@blp.route("/<int:author_id>")
class AuthorDetail(MethodView):
    @blp.response(200, AuthorSchema)
    def get(self, author_id: int):
        """Get one author by id."""
        return db.get_or_404(
            Author, author_id, description=f"No author with id {author_id}"
        )

    @blp.arguments(AuthorSchema)
    @blp.response(200, AuthorSchema)
    def put(self, author_data: dict, author_id: int):
        """Replace an author's fields."""
        author = db.get_or_404(
            Author, author_id, description=f"No author with id {author_id}"
        )
        author.name = author_data["name"]
        db.session.commit()
        return author

    @blp.response(204)
    def delete(self, author_id: int):
        """Delete an author (cascades to their books - see models.py)."""
        author = db.get_or_404(
            Author, author_id, description=f"No author with id {author_id}"
        )
        db.session.delete(author)
        db.session.commit()
