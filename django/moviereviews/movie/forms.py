from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Used for both creating and editing a Review (see
    movie/views.py's add_review()/edit_review()) - only `text` is a
    user-editable field; `movie` and `user` are set by the view itself
    from the URL and the logged-in session, not from form input (a
    user shouldn't be able to submit a review as someone else, or
    against a different movie than the page they're on).
    """

    class Meta:
        model = Review
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share your thoughts on this movie...",
                }
            ),
        }
        labels = {"text": ""}
