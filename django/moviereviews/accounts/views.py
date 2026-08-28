from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignUpForm


def signupaccount(request):
    """Create-account page ('signup/' in accounts/urls.py, reachable at
    '/accounts/signup/' - see moviereviews/urls.py).
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # form.save() creates the User row (SignUpForm/UserCreationForm
            # handles hashing the password - the raw password is never
            # stored). login() then starts a session for the new user
            # immediately, so signing up also logs them in - no separate
            # "now go log in" step.
            user = form.save()
            login(request, user)
            return redirect("/")
        # form.is_valid() is False: form.errors is now populated (e.g.
        # "A user with that username already exists." on the username
        # field, or "The two password fields didn't match." on
        # password2) - fall through to re-render the form below, which
        # displays those errors next to the offending fields.
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def loginuser(request):
    """Login page ('login/' in accounts/urls.py, reachable at
    '/accounts/login/' - see moviereviews/urls.py).
    """
    if request.method == "POST":
        # AuthenticationForm takes the request itself (not just the
        # POST data) so it can rate-limit/log failed attempts per
        # request - see Django's docs on AuthenticationForm.
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("/")
        # Invalid credentials: form.non_field_errors() now has the
        # generic "Please enter a correct username and password" message
        # - falls through to re-render with that shown.
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logoutuser(request):
    """Logs the current user out ('logout/' in accounts/urls.py,
    reachable at '/accounts/logout/' - see moviereviews/urls.py).

    POST-only (see the "Log Out" <form> in movie/templates/movie/base.html)
    rather than a plain link - Django's own docs recommend this so a
    bare GET (e.g. a link a browser might prefetch, or a crawler
    following it) can't log a user out as a side effect.
    """
    logout(request)
    return redirect("/")
