import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'screens/cart_screen.dart';
import 'screens/home_screen.dart';
import 'screens/product_screen.dart';

final router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (context, state) => const HomeScreen()),
    GoRoute(
      path: '/product/:sku',
      builder: (context, state) => ProductScreen(
        sku: state.params['sku']!,
        ref: state.queryParams['ref'],
      ),
    ),
    GoRoute(path: '/cart', builder: (context, state) => const CartScreen()),
  ],
  errorBuilder: (context, state) => Scaffold(
    body: Center(child: Text('No route for ${state.location}')),
  ),
);
