from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


def _bootstrapify(form):
    """Add Bootstrap's `form-control` class to every field's widget.

    Django's built-in auth forms render plain, unstyled <input> tags by
    default - this is the one line that makes {{ field }} in a template
    pick up Bootstrap's input styling, without having to redeclare each
    field's widget by hand.
    """
    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control"})


class SignUpForm(UserCreationForm):
    """Django's inbuilt UserCreationForm, used as-is apart from styling.

    UserCreationForm already gives us exactly what was asked for:
    `username`, `password1`, and `password2` (the confirmation field),
    plus the "already exists" check for free - because Meta.model is
    User and `username` is `unique=True` on that model, Django's
    ModelForm validation (via the model's own full_clean()) rejects a
    duplicate username automatically and attaches the error to that
    field. No manual `User.objects.filter(username=...).exists()`
    check needed - that would just be reimplementing what the model
    constraint + form already do.
    """

    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)


class LoginForm(AuthenticationForm):
    """Django's inbuilt AuthenticationForm - validates the
    username/password pair against the database and produces a generic
    "Please enter a correct username and password" error on failure
    (deliberately generic, so a login attempt can't be used to probe
    which usernames exist).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)
