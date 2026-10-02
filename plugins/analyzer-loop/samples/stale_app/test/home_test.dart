import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:stale_app/main.dart';

void main() {
  testWidgets('add to cart updates the app bar count', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: StaleApp()));
    await tester.pumpAndSettle();

    expect(find.text('Cedar Desk Tidy'), findsOneWidget);
    expect(find.text('Cart (0)'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.add_shopping_cart).first);
    await tester.pump();

    expect(find.text('Cart (1)'), findsOneWidget);
  });
}
