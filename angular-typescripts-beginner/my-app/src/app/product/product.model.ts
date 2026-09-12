// A Product describes one item shown in the landing page's product list.
// Declaring this as a TypeScript interface - rather than leaving product
// objects untyped - means the compiler checks that every mock product below
// (and any product a later stage fetches from a real API) has the same
// shape, catching typos like a missing `price` at compile time instead of
// at runtime in the browser.
export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  // How many of the 5 stars are filled in for this product's rating.
  // Owned by Product (not RatingComponent) so each product card keeps its
  // own rating in sync via RatingComponent's two-way `[(rating)]` binding.
  rating: number;
}
