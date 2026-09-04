from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReviewForm
from .models import Movie, Review

# Create your views here.


def home(request):
    """The site's landing page ('' in moviereviews/urls.py)."""
    # The search form in home.html submits via GET, so its "searchTerm"
    # field lands in request.GET rather than request.POST. .get() with a
    # default of "" means a fresh page load (no search submitted yet)
    # doesn't blow up with a KeyError.
    search_term = request.GET.get("searchTerm", "")

    # `icontains` is a case-insensitive substring match (Django's ORM
    # turns this into SQL's `LIKE '%term%'` under the hood) - "batman"
    # should still find "The Dark Knight"'s title only if "batman"
    # literally appears in it, so this is a title search, not a fuzzy
    # one. An empty search_term (fresh page load) shows every movie.
    if search_term:
        movies = Movie.objects.filter(title__icontains=search_term)
    else:
        movies = Movie.objects.all()

    # The dict passed as render()'s third argument is the template's
    # *context* - each key becomes a variable the template can use.
    # See movie/templates/movie/home.html. No "name" key here anymore -
    # the greeting there now reads the logged-in user directly off
    # `request.user` (available in every template for free via
    # settings.py's auth context processor), instead of a hardcoded
    # name that stayed "Xuan Vinh" regardless of who was actually
    # signed in.
    context = {"searchTerm": search_term, "movies": movies}
    return render(request, "movie/home.html", context)


def about(request):
    """The site's about page ('about/' in moviereviews/urls.py)."""
    context = {"name": "Xuan Vinh"}
    return render(request, "movie/about.html", context)


def signup(request):
    """Mailing-list signup confirmation ('signup/' in moviereviews/urls.py).

    Reached by submitting the mailing-list form on the home page.
    """
    email = request.GET.get("email", "")
    context = {"email": email}
    return render(request, "movie/signup.html", context)


def detail(request, movie_id):
    """One movie's detail page ('<int:movie_id>/' in movie/urls.py,
    reachable at '/movie/<id>/' - see moviereviews/urls.py).

    Reached by clicking a movie card's "Detail" button on the home page.
    """
    # get_object_or_404 is a shortcut for the try/except Movie.DoesNotExist
    # -> raise Http404 pattern - so visiting e.g. /movie/9999/ (an id
    # that doesn't exist) renders Django's normal 404 page instead of
    # the view crashing with an unhandled exception.
    movie = get_object_or_404(Movie, pk=movie_id)

    # movie.reviews (the related_name on Review.movie in models.py)
    # gives every review for this movie without a separate Review
    # query - already ordered most-recent-first by Review.Meta.ordering.
    reviews = movie.reviews.all()

    # Anonymous users have no meaningful "their own review" - only look
    # one up for an authenticated visitor. Used by detail.html to show
    # "Edit your review"/"Delete" instead of a "Write a Review" link
    # when this user already has one (Review.Meta.unique_together only
    # allows one per user per movie).
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(movie=movie, user=request.user).first()

    context = {"movie": movie, "reviews": reviews, "user_review": user_review}
    return render(request, "movie/detail.html", context)


@login_required
def add_review(request, movie_id):
    """Create a review for one movie ('<int:movie_id>/reviews/add/' in
    movie/urls.py, reachable at '/movie/<id>/reviews/add/').

    @login_required is the authentication half of this view's
    authorization: an anonymous visitor is redirected to LOGIN_URL
    (settings.py) with ?next=<this URL> attached, so
    accounts/views.py's loginuser() can send them straight back here
    once they've logged in.
    """
    movie = get_object_or_404(Movie, pk=movie_id)

    # Review.Meta.unique_together (models.py) would reject a second
    # INSERT for the same (movie, user) pair at the database level
    # anyway - checking here first means a user who already reviewed
    # this movie lands on their existing review to edit it, instead of
    # hitting a raw database error.
    existing_review = Review.objects.filter(movie=movie, user=request.user).first()
    if existing_review is not None:
        return redirect("edit-review", review_id=existing_review.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # commit=False builds the Review instance without saving it
            # yet, so movie/user (not part of the form - see
            # ReviewForm's docstring) can be filled in from the URL and
            # the logged-in session before the actual INSERT happens.
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect("movie-detail", movie_id=movie.id)
    else:
        form = ReviewForm()

    context = {"form": form, "movie": movie, "mode": "add"}
    return render(request, "movie/review_form.html", context)


@login_required
def edit_review(request, review_id):
    """Edit an existing review ('reviews/<int:review_id>/edit/' in
    movie/urls.py, reachable at '/movie/reviews/<id>/edit/').
    """
    review = get_object_or_404(Review, pk=review_id)

    # The authorization check that actually matters here: being logged
    # in (via @login_required) only proves *someone* is signed in, not
    # that they own *this* review. Without this check, any logged-in
    # user could edit anyone else's review just by guessing/changing
    # the id in the URL.
    if review.user != request.user:
        return HttpResponseForbidden("You can only edit your own review.")

    if request.method == "POST":
        # instance=review means form.save() updates this row instead of
        # creating a new one - the same ReviewForm as add_review(), just
        # bound to an existing Review.
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("movie-detail", movie_id=review.movie.id)
    else:
        form = ReviewForm(instance=review)

    context = {"form": form, "movie": review.movie, "mode": "edit"}
    return render(request, "movie/review_form.html", context)


@login_required
def delete_review(request, review_id):
    """Delete an existing review ('reviews/<int:review_id>/delete/' in
    movie/urls.py, reachable at '/movie/reviews/<id>/delete/').
    """
    review = get_object_or_404(Review, pk=review_id)

    # Same ownership check as edit_review() - authentication alone
    # isn't authorization to delete *this specific* review.
    if review.user != request.user:
        return HttpResponseForbidden("You can only delete your own review.")

    if request.method == "POST":
        movie_id = review.movie.id
        review.delete()
        return redirect("movie-detail", movie_id=movie_id)

    # GET: show a confirmation page rather than deleting immediately -
    # same reasoning as accounts/views.py's logoutuser() being POST-only:
    # a destructive action shouldn't be triggerable by a bare link/GET.
    return render(request, "movie/review_confirm_delete.html", {"review": review})
