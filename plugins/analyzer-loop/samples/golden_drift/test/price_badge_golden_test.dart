import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:golden_drift/price_badge.dart';

void main() {
  testWidgets('price badge golden', (tester) async {
    await tester.binding.setSurfaceSize(const Size(240, 80));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      const MaterialApp(
        debugShowCheckedModeBanner: false,
        home: Scaffold(
          body: Center(
            child: RepaintBoundary(
              child: PriceBadge(label: r'$24.00', onSale: true),
            ),
          ),
        ),
      ),
    );

    await expectLater(
      find.byType(PriceBadge),
      matchesGoldenFile('goldens/price_badge.png'),
    );
  });
}
