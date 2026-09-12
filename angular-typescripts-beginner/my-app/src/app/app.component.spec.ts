import { TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { AppComponent } from './app.component';
import { ProductComponent } from './product/product.component';
import { RatingComponent } from './rating/rating.component';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      // ProductComponent must be declared here too, since AppComponent's
      // template now uses its `<app-product>` selector - otherwise Angular's
      // template compiler doesn't recognize the tag and throws. RatingComponent
      // is declared for the same reason, one level down (ProductComponent's
      // own template uses `<app-rating>`). CommonModule is needed because
      // ProductComponent's template uses *ngFor and the `currency` pipe.
      imports: [CommonModule],
      declarations: [
        AppComponent,
        ProductComponent,
        RatingComponent
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have as title 'my-app'`, () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app.title).toEqual('my-app');
  });

  it('should render title', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('my-app');
  });
});
