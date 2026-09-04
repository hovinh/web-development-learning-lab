"""Marshmallow schemas: validate incoming JSON and shape outgoing JSON.

See rest-apis-flask/README.md's "Persistence and serialization" section
for how this fits with Flask-SQLAlchemy: models.py owns the database
shape, these schemas own the API's request/response shape - the two
aren't required to look identical, which is exactly why each author's
response nests a trimmed-down BookSummarySchema (no `author` field
inside it) rather than dumping the full Book/Author objects into each
other and recursing forever.
"""

from marshmallow import Schema, fields, validate


class BookSummarySchema(Schema):
    """A book's fields as seen nested inside an author's response."""

    id = fields.Int(dump_only=True)
    title = fields.Str()
    published_year = fields.Int()


class AuthorSummarySchema(Schema):
    """An author's fields as seen nested inside a book's response."""

    id = fields.Int(dump_only=True)
    name = fields.Str()


class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    # validate.Length(min=1) rejects "" - required=True alone only checks
    # the key is present, not that its value is non-empty.
    name = fields.Str(required=True, validate=validate.Length(min=1))
    # dump_only: books are added via POST /api/books (author_id points
    # at the author), never by writing to this field directly.
    books = fields.List(fields.Nested(BookSummarySchema), dump_only=True)


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    published_year = fields.Int(required=True)
    # load_only: incoming requests set the author by id ("author_id": 3);
    # outgoing responses show the resolved author object instead (below),
    # not the raw id twice.
    author_id = fields.Int(required=True, load_only=True)
    author = fields.Nested(AuthorSummarySchema, dump_only=True)
