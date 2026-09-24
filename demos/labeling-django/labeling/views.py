from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LabelForm
from .models import Item, Label


@login_required
def queue(request):
    """A reviewer's worklist ('' in labeling/urls.py).

    This one line is the whole "ownership filtering" story the blog post
    promises: every reviewer only ever sees the rows assigned to them,
    with no per-view "is this mine?" check to remember - the query
    itself can't return anyone else's items. Compare
    demos/labeling-fastapi-react/api/deps.py, where the equivalent check
    has to be written (and remembered) on every endpoint.
    """
    items = Item.objects.filter(assigned_to=request.user).order_by("id")

    # select_related isn't needed here (Label doesn't point back at
    # Item's labels list without a query) - instead, prefetch this
    # reviewer's own label for each item in one extra query, and hand
    # the template a plain dict so it can show "labeled"/"not yet"
    # without an N+1 query per row.
    my_labels = Label.objects.filter(reviewer=request.user, item__in=items)
    labeled_item_ids = {label.item_id for label in my_labels}

    context = {"items": items, "labeled_item_ids": labeled_item_ids}
    return render(request, "labeling/queue.html", context)


@login_required
def label_item(request, item_id):
    """Label one item ('<int:item_id>/' in labeling/urls.py).

    get_object_or_404(..., assigned_to=request.user) is the enforcement
    half of the ownership rule above: even if a reviewer guesses another
    reviewer's item id in the URL, the query simply finds no row for
    them and 404s - see labeling/tests.py's
    test_reviewer_cannot_open_another_reviewers_item for the check that
    proves this.
    """
    item = get_object_or_404(Item, pk=item_id, assigned_to=request.user)

    # A reviewer relabeling an item they've already labeled edits their
    # existing Label row (Meta.unique_together on Label enforces one per
    # reviewer per item at the database level too) rather than creating
    # a second one.
    existing_label = Label.objects.filter(item=item, reviewer=request.user).first()

    if request.method == "POST":
        form = LabelForm(request.POST, instance=existing_label)
        if form.is_valid():
            label = form.save(commit=False)
            label.item = item
            label.reviewer = request.user
            label.save()
            return redirect("queue")
    else:
        form = LabelForm(instance=existing_label)

    context = {"item": item, "form": form}
    return render(request, "labeling/label_item.html", context)
