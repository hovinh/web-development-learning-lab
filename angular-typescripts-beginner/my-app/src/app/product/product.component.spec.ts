import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';

import { ProductComponent } from './product.component';
import { RatingComponent } from '../rating/rating.component';

describe('ProductComponent', () => {
  let component: ProductComponent;
  let fixture: ComponentFixture<ProductComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      // ProductComponent's template uses *ngFor and the `currency` pipe,
      // both of which live in CommonModule - the real app gets these for
      // free via AppModule's `imports: [BrowserModule]` (which re-exports
      // CommonModule), but this standalone test module needs it explicitly.
      // RatingComponent must be declared too, since the template also uses
      // its `<app-rating>` selector.
      imports: [CommonModule],
      declarations: [ProductComponent, RatingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProductComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
