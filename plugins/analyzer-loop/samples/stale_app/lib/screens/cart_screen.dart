import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../cart/cart_notifier.dart';

class CartScreen extends ConsumerWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = ref.watch(cartProvider);
    final CartNotifier cart = ref.read(cartProvider.notifier);
    return Scaffold(
      appBar: AppBar(title: const Text('Cart')),
      body: ListView(
        children: [
          for (final e in items)
            ListTile(
              title: Text('${e.name} x${e.qty}'),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () => cart.remove(e.sku),
              ),
            ),
          ListTile(
            title: const Text('Total'),
            trailing: Text('\$${(cart.totalCents / 100).toStringAsFixed(2)}'),
          ),
        ],
      ),
    );
  }
}
