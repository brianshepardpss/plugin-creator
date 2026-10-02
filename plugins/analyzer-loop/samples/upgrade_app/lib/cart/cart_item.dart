/// A line in the Pebble & Pine Goods demo cart. All data is fake.
class CartItem {
  const CartItem({required this.sku, required this.name, required this.priceCents, this.qty = 1});

  final String sku;
  final String name;
  final int priceCents;
  final int qty;

  CartItem copyWith({int? qty}) =>
      CartItem(sku: sku, name: name, priceCents: priceCents, qty: qty ?? this.qty);
}

const demoCatalog = <CartItem>[
  CartItem(sku: 'PPG-001', name: 'Cedar Desk Tidy', priceCents: 2400),
  CartItem(sku: 'PPG-002', name: 'Moss Felt Coasters', priceCents: 1200),
  CartItem(sku: 'PPG-003', name: 'Granite Bookend', priceCents: 3150),
];
