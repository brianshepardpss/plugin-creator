import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:stale_app/cart/cart_item.dart';
import 'package:stale_app/cart/cart_notifier.dart';

void main() {
  test('adding the same sku twice bumps qty and total', () {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    final cart = container.read(cartProvider.notifier);
    cart.add(demoCatalog[0]);
    cart.add(demoCatalog[0]);
    cart.add(demoCatalog[2]);

    expect(container.read(cartProvider).length, 2);
    expect(container.read(cartCountProvider), 3);
    expect(cart.totalCents, 2400 * 2 + 3150);
  });
}
