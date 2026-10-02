import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cart_item.dart';

/// Old Riverpod 2 style: StateNotifier + StateNotifierProvider.
class CartNotifier extends StateNotifier<List<CartItem>> {
  CartNotifier() : super(const []);

  void add(CartItem item) {
    final i = state.indexWhere((e) => e.sku == item.sku);
    if (i == -1) {
      state = [...state, item];
    } else {
      state = [
        for (final e in state) e.sku == item.sku ? e.copyWith(qty: e.qty + 1) : e,
      ];
    }
  }

  void remove(String sku) {
    state = state.where((e) => e.sku != sku).toList();
  }

  int get totalCents => state.fold(0, (sum, e) => sum + e.priceCents * e.qty);
}

final cartProvider = StateNotifierProvider<CartNotifier, List<CartItem>>((ref) {
  return CartNotifier();
});

final cartCountProvider = Provider<int>((ref) {
  return ref.watch(cartProvider).fold(0, (sum, e) => sum + e.qty);
});

final catalogProvider = FutureProvider<List<CartItem>>((FutureProviderRef<List<CartItem>> ref) async {
  return demoCatalog;
});
