import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'router.dart';

void main() {
  runApp(const ProviderScope(child: StaleApp()));
}

class StaleApp extends StatelessWidget {
  const StaleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Pebble & Pine Goods',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal, background: Colors.white),
      ),
      routerConfig: router,
    );
  }
}
