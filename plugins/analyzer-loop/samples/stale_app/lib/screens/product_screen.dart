import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../cart/cart_item.dart';
import '../cart/cart_notifier.dart';

class ProductScreen extends ConsumerWidget {
  const ProductScreen({super.key, required this.sku, this.ref});

  final String sku;
  final String? ref;

  @override
  Widget build(BuildContext context, WidgetRef widgetRef) {
    final item = demoCatalog.firstWhere((e) => e.sku == sku);
    final accent = Theme.of(context).colorScheme.primary;
    return Scaffold(
      appBar: AppBar(title: Text(item.name)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 120,
              color: accent.withOpacity(0.2),
              child: Center(child: Text('#${accent.value.toRadixString(16)}')),
            ),
            const SizedBox(height: 12),
            Text('SKU ${item.sku}'),
            if (ref != null) Text('Referred by $ref'),
            ButtonBar(
              children: [
                ElevatedButton(
                  onPressed: () => widgetRef.read(cartProvider.notifier).add(item),
                  child: const Text('Add to cart'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
