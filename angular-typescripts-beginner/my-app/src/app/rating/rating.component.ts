import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-rating',
  standalone: false,
  templateUrl: './rating.component.html',
  styleUrl: './rating.component.css'
})
export class RatingComponent {
  // `@Input() rating` + `@Output() ratingChange` is Angular's naming
  // convention for a *two-way bindable* property on a custom component: a
  // parent template can write `[(rating)]="someProperty"`, which Angular
  // desugars into `[rating]="someProperty" (ratingChange)="someProperty = $event"`.
  // This is the same "banana in a box" syntax `[(ngModel)]` uses on native
  // form controls - here we're implementing that same pattern ourselves.
  @Input() rating = 0;
  @Output() ratingChange = new EventEmitter<number>();

  // Always exactly 5 stars - a fixed-length array to loop over with *ngFor.
  // The values themselves (1..5) double as each star's own "value".
  stars = [1, 2, 3, 4, 5];

  // Runs on a star's (click) event binding. Updates the local `rating` and
  // emits it so a parent bound via `[(rating)]` sees the new value too.
  onStarClick(star: number): void {
    this.rating = star;
    this.ratingChange.emit(this.rating);
  }
}
