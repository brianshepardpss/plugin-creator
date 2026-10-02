# Riverpod 3 idioms (flutter_riverpod 3.4.x, riverpod_generator 4.0.x)

Compiled against flutter_riverpod 3.4.3, riverpod_annotation 4.0.7,
riverpod_generator 4.0.9, build_runner 2.16.1 on 2026-10-02.

## Without code generation

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CartItem {
  const CartItem(this.sku, this.qty);
  final String sku;
  final int qty;
}

/// Synchronous state with methods: Notifier + NotifierProvider.
class CartNotifier extends Notifier<List<CartItem>> {
  @override
  List<CartItem> build() => const [];

  void add(String sku) => state = [...state, CartItem(sku, 1)];
}

final cartProvider = NotifierProvider<CartNotifier, List<CartItem>>(CartNotifier.new);

/// Async state with methods: AsyncNotifier.
class OrdersNotifier extends AsyncNotifier<List<String>> {
  @override
  Future<List<String>> build() async => fetchOrders();

  Future<void> refreshOrders() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(fetchOrders);
  }
}

Future<List<String>> fetchOrders() async => const ['PPG-1001'];

final ordersProvider = AsyncNotifierProvider<OrdersNotifier, List<String>>(OrdersNotifier.new);

/// Parameterised: pass the argument through the constructor.
class StockNotifier extends Notifier<int> {
  StockNotifier(this.sku);
  final String sku;

  @override
  int build() => sku.length;
}

final stockProvider = NotifierProvider.family<StockNotifier, int, String>(StockNotifier.new);

/// Read-only derived value: plain Provider / FutureProvider taking `Ref`.
final cartCountProvider = Provider<int>((ref) => ref.watch(cartProvider).fold(0, (n, e) => n + e.qty));
```

Auto-dispose: `NotifierProvider.autoDispose<...>(...)` or `isAutoDispose: true`.
`StateProvider` / `StateNotifierProvider` exist only in `package:flutter_riverpod/legacy.dart`;
do not use them in new code.

## With riverpod_generator (when `riverpod_generator` is in dev_dependencies)

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'cart.g.dart';

@riverpod
class CartNotifier extends _$CartNotifier {
  @override
  List<String> build() => const [];

  void add(String sku) => state = [...state, sku];
}
// Generates `cartProvider` (the "Notifier" suffix is stripped).

@riverpod
Future<List<String>> catalog(Ref ref) async => const ['PPG-001'];
// Generates `catalogProvider`.
```

Generated providers are auto-dispose by default; use `@Riverpod(keepAlive: true)` to keep state.
Run `dart run build_runner build --delete-conflicting-outputs` after every change.

## Testing

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('add puts one item in the cart', () {
    final container = ProviderContainer.test();
    container.read(cartProvider.notifier).add('PPG-001');
    expect(container.read(cartProvider), hasLength(1));
  });
}
```

`ProviderContainer.test()` disposes itself at the end of the test. Override with
`ProviderContainer.test(overrides: [ordersProvider.overrideWith(() => FakeOrders())])`.
In widgets: `ConsumerWidget` + `ref.watch` in build, `ref.read(p.notifier).method()` in callbacks,
`ref.listen` for side effects (snackbars, navigation).
