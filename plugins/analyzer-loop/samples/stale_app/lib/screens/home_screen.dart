import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../cart/cart_notifier.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalog = ref.watch(catalogProvider);
    final count = ref.watch(cartCountProvider);
    final scale = MediaQuery.of(context).textScaleFactor;
    return WillPopScope(
      onWillPop: () async => false,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Pebble & Pine Goods'),
          backgroundColor: Colors.teal.withOpacity(0.85),
          actions: [
            TextButton(
              style: ButtonStyle(
                foregroundColor: MaterialStateProperty.all(Colors.white),
              ),
              onPressed: () => context.go('/cart'),
              child: Text('Cart ($count)'),
            ),
          ],
        ),
        body: catalog.valueOrNull == null
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                children: [
                  for (final item in catalog.valueOrNull!)
                    ListTile(
                      title: Text(item.name, textScaleFactor: scale),
                      subtitle: Text('\$${(item.priceCents / 100).toStringAsFixed(2)}'),
                      tileColor: Colors.grey.withOpacity(0.05),
                      onTap: () => context.go('/product/${item.sku}'),
                      trailing: IconButton(
                        icon: const Icon(Icons.add_shopping_cart),
                        onPressed: () => ref.read(cartProvider.notifier).add(item),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}
