import { Component } from '@angular/core';
import { Product } from './product.model';

@Component({
  selector: 'app-product',
  standalone: false,
  templateUrl: './product.component.html',
  styleUrl: './product.component.css'
})
export class ProductComponent {
  // Mock data, hardcoded here rather than fetched from a server - this stage
  // is about the component itself (property binding + *ngFor over a list),
  // not about talking to a backend yet. A later stage that adds a
  // ProductService would replace this hardcoded array with data fetched over
  // HTTP, without the template below needing to change at all - the template
  // only cares that it gets a Product[], not where that array came from.
  products: Product[] = [
    {
      id: 1,
      name: 'Wireless Headphones',
      description: 'Over-ear headphones with active noise cancellation.',
      price: 89.99,
      imageUrl: 'https://placehold.co/300x200?text=Headphones',
      rating: 4,
    },
    {
      id: 2,
      name: 'Mechanical Keyboard',
      description: 'Tactile mechanical keyboard with hot-swappable switches.',
      price: 129.0,
      imageUrl: 'https://placehold.co/300x200?text=Keyboard',
      rating: 5,
    },
    {
      id: 3,
      name: 'Smart Watch',
      description: 'Tracks steps, heart rate, and sleep; syncs with your phone.',
      price: 199.5,
      imageUrl: 'https://placehold.co/300x200?text=Smart+Watch',
      rating: 3,
    },
    {
      id: 4,
      name: 'Portable Charger',
      description: '20,000 mAh power bank with fast-charging USB-C output.',
      price: 39.99,
      imageUrl: 'https://placehold.co/300x200?text=Charger',
      rating: 0,
    },
  ];
}
