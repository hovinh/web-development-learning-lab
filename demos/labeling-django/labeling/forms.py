from django import forms

from .models import Label


class LabelForm(forms.ModelForm):
    """Used by labeling/views.py's label_item() to record a reviewer's
    decision on one Item. `item` and `reviewer` are set by the view from
    the URL and the logged-in session, not from form input - a reviewer
    shouldn't be able to submit a label as someone else or against an
    item that isn't theirs.
    """

    class Meta:
        model = Label
        fields = ["decision", "corrected_label", "note"]
        widgets = {
            "decision": forms.RadioSelect,
            "corrected_label": forms.TextInput(
                attrs={
                    "class": "input w-full",
                    "placeholder": "Only needed if marking Incorrect",
                }
            ),
            "note": forms.Textarea(attrs={"class": "textarea w-full", "rows": 3}),
        }
