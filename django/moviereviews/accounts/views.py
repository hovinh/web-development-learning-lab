from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
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
    # ?next=<path> is how @login_required (see movie/views.py's review
    # views) says "come back here once you're logged in" - settings.py's
    # LOGIN_URL is what makes it redirect here in the first place with
    # that query string attached. GET reads it off the query string
    # (first visit); POST reads it back off the hidden field
    # accounts/templates/accounts/login.html renders, since a form
    # submission doesn't carry the original URL's query string.
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    # An unvalidated ?next= is an open-redirect risk (a crafted login
    # link could send a user somewhere malicious right after they
    # authenticate) - url_has_allowed_host_and_scheme is the same check
    # Django's own built-in LoginView applies to its next parameter.
    # Falls back to "/" for anything that doesn't pass, rather than
    # rejecting the login itself.
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = "/"

    if request.method == "POST":
        # AuthenticationForm takes the request itself (not just the
        # POST data) so it can rate-limit/log failed attempts per
        # request - see Django's docs on AuthenticationForm.
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url)
        # Invalid credentials: form.non_field_errors() now has the
        # generic "Please enter a correct username and password" message
        # - falls through to re-render with that shown.
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


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
