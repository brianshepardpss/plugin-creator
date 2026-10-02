# Golden test recipes

Compiled against Flutter 3.47.6 and alchemist 0.14.0 on 2026-10-02.

## A. Tolerant comparator for every test in a package

`test/flutter_test_config.dart` (Flutter runs it before each test file in `test/`):

```dart
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';

/// Accepts goldens whose pixel diff ratio is <= [tolerance] (0.0005 = 0.05%).
class TolerantGoldenComparator extends LocalFileComparator {
  TolerantGoldenComparator(super.testFile, {required this.tolerance});

  final double tolerance;

  @override
  Future<bool> compare(Uint8List imageBytes, Uri golden) async {
    final result = await GoldenFileComparator.compareLists(imageBytes, await getGoldenBytes(golden));
    if (result.passed || result.diffPercent <= tolerance) {
      result.dispose();
      return true;
    }
    final error = await generateFailureOutput(result, golden, basedir);
    result.dispose();
    throw FlutterError(error);
  }
}

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  if (goldenFileComparator is LocalFileComparator) {
    final testUrl = (goldenFileComparator as LocalFileComparator).basedir;
    goldenFileComparator = TolerantGoldenComparator(
      // basedir is the test file's directory; the comparator wants a file inside it.
      testUrl.resolve('flutter_test_config.dart'),
      tolerance: 0.0005,
    );
  }
  await testMain();
}
```

`diffPercent` is a ratio (0.0 to 1.0) despite its name. Set `tolerance` from
`golden_diff.py`'s "min tolerance" and round up modestly.

## B. Compare goldens on Linux only

Tag golden tests and keep them out of local runs on other OSes.

`dart_test.yaml` at the package root:

```yaml
tags:
  golden:
```

In each golden test file:

```dart
@Tags(['golden'])
library;

import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('price badge', (tester) async {
    // ...
  }, skip: !Platform.isLinux);
}
```

Regenerate on the platform CI compares against, with the same Flutter
version as CI:

- In CI: a manually triggered job on the Linux runner that runs
  `flutter test --tags golden --update-goldens` and uploads `test/**/goldens/*.png`
  as an artifact for review.
- Locally: any Linux container with the same Flutter version
  (`flutter --version` must match CI), mounting the repo and running the same
  command.

Day-to-day: `flutter test --exclude-tags golden` locally, `flutter test --tags golden` on CI.

## C. Alchemist (cross-platform CI goldens)

`pubspec.yaml`: `dev_dependencies: alchemist: ^0.14.0`

`test/flutter_test_config.dart`:

```dart
import 'dart:async';
import 'dart:io';

import 'package:alchemist/alchemist.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  final isCi = Platform.environment.containsKey('CI');
  return AlchemistConfig.runWithConfig(
    config: AlchemistConfig(
      platformGoldensConfig: PlatformGoldensConfig(enabled: !isCi),
    ),
    run: testMain,
  );
}
```

A test:

```dart
import 'package:alchemist/alchemist.dart';
import 'package:golden_drift/price_badge.dart';

void main() {
  goldenTest(
    'price badge variants',
    fileName: 'price_badge',
    builder: () => GoldenTestGroup(
      children: [
        GoldenTestScenario(name: 'regular', child: const PriceBadge(label: r'$24.00')),
        GoldenTestScenario(name: 'on sale', child: const PriceBadge(label: r'$19.00', onSale: true)),
      ],
    ),
  );
}
```

CI goldens land in `goldens/ci/` (text drawn as blocks, shadows flattened);
platform goldens in `goldens/<os>/` and are for humans. Commit `goldens/ci/`.
Generate with `flutter test --update-goldens` once, when the user asks.

## D. Plain matchesGoldenFile template for a new test

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('<widget> golden', (tester) async {
    await tester.binding.setSurfaceSize(const Size(400, 200));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.teal),
        home: const Scaffold(body: Center(child: RepaintBoundary(child: /* widget */ SizedBox()))),
      ),
    );
    await tester.pumpAndSettle();
    await expectLater(find.byType(RepaintBoundary).last, matchesGoldenFile('goldens/<name>.png'));
  });
}
```

## E. Real fonts in readable goldens

Widget tests render text with the Ahem test font (solid blocks) unless fonts
are loaded. To load an app font bundled in `pubspec.yaml`:

```dart
import 'package:flutter/services.dart';

Future<void> loadFont(String family, String assetPath) async {
  final loader = FontLoader(family)..addFont(rootBundle.load(assetPath));
  await loader.load();
}
```

Call it in `setUpAll` or `testExecutable`. Real fonts make goldens readable
but reintroduce OS-specific hinting, so combine with recipe B or C.
