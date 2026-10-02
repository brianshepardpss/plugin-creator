# Bloc 9 idioms (bloc 9.2.x, flutter_bloc 9.1.x, bloc_test 10.x)

Compiled against bloc 9.2.1, flutter_bloc 9.1.1, bloc_test 10.0.0 on 2026-10-02.

## Cubit (no events; prefer for simple state)

```dart
import 'package:flutter_bloc/flutter_bloc.dart';

class ThemeCubit extends Cubit<bool> {
  ThemeCubit() : super(false);

  void toggle() => emit(!state);
}
```

## Bloc (events, sealed classes, one handler per event)

```dart
import 'package:flutter_bloc/flutter_bloc.dart';

sealed class CartEvent {}

final class CartItemAdded extends CartEvent {
  CartItemAdded(this.sku);
  final String sku;
}

final class CartCleared extends CartEvent {}

final class CartState {
  const CartState({this.skus = const []});
  final List<String> skus;
}

class CartBloc extends Bloc<CartEvent, CartState> {
  CartBloc() : super(const CartState()) {
    on<CartItemAdded>((event, emit) => emit(CartState(skus: [...state.skus, event.sku])));
    on<CartCleared>((event, emit) => emit(const CartState()));
  }
}
```

Async handlers: `on<E>((event, emit) async { emit(loading); final r = await repo.load(); emit(done(r)); })`.
Concurrency: `on<E>(handler, transformer: droppable())` from `bloc_concurrency`.
Observers: `Bloc.observer = const AppObserver();` in `main` (`BlocOverrides` was removed in 9.0);
combine several with `MultiBlocObserver(observers: [...])`.
Widgets: `BlocProvider(create: (_) => CartBloc())`, `BlocBuilder`, `BlocListener`, `BlocSelector`,
`context.read<CartBloc>().add(CartItemAdded('PPG-001'))`, `context.watch<CartBloc>().state`.

## Testing (bloc_test 10)

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  blocTest<CartBloc, CartState>(
    'adds a sku',
    build: CartBloc.new,
    act: (bloc) => bloc.add(CartItemAdded('PPG-001')),
    expect: () => [isA<CartState>().having((s) => s.skus, 'skus', ['PPG-001'])],
  );
}
```
