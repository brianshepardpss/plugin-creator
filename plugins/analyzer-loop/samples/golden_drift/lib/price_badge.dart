import 'package:flutter/material.dart';

/// Sale badge used on the Pebble & Pine Goods product grid (fake demo data).
class PriceBadge extends StatelessWidget {
  const PriceBadge({super.key, required this.label, this.onSale = false});

  final String label;
  final bool onSale;

  @override
  Widget build(BuildContext context) {
    final color = onSale ? const Color(0xFFD84315) : const Color(0xFF00796B);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        border: Border.all(color: color, width: 2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 18)),
    );
  }
}
