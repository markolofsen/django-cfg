"""
Test script for SPA routing logic.

Run this to verify that URL paths resolve correctly to static files.
"""

from pathlib import Path
import django_cfg


def test_resolve_spa_path():
    """Test the SPA path resolution logic."""

    # Simulate the base directory
    base_dir = Path(django_cfg.__file__).parent / 'static' / 'frontend' / 'admin'

    print(f"Base directory: {base_dir}")
    print(f"Base directory exists: {base_dir.exists()}\n")

    # Test cases
    test_cases = [
        # (input_path, expected_output_path, description)
        ('', 'index.html', 'Root path'),
        ('/', 'index.html', 'Root path with slash'),
        ('private/centrifugo', 'private/centrifugo/index.html', 'Nested route without trailing slash'),
        ('private/centrifugo/', 'private/centrifugo/index.html', 'Nested route with trailing slash'),
        ('private', 'private.html', 'Single segment route'),
        ('private/', 'private/index.html', 'Single segment with trailing slash'),
        ('_next/static/chunks/app.js', '_next/static/chunks/app.js', 'Static asset (exact match)'),
        ('favicon.ico', 'favicon.ico', 'Favicon (exact match)'),
        ('unknown/route', 'index.html', 'Unknown route (SPA fallback)'),
    ]

    def resolve_spa_path(base_dir, path):
        """
        Exact copy of the view's _resolve_spa_path method.

        This should match the logic in views.py exactly.
        """
        # Handle empty path (done in view before calling this method)
        if not path or path == '/':
            path = 'index.html'
            return path

        file_path = base_dir / path
        path_normalized = path.rstrip('/')

        # Strategy 1: Exact file match (for static assets like JS, CSS, images)
        if file_path.exists() and file_path.is_file():
            return path

        # Strategy 2: Try path/index.html (most common for SPA routes)
        index_in_dir = base_dir / path_normalized / 'index.html'
        if index_in_dir.exists():
            resolved_path = f"{path_normalized}/index.html"
            return resolved_path

        # Strategy 3: Try with trailing slash + index.html
        if path.endswith('/'):
            index_path = path + 'index.html'
            if (base_dir / index_path).exists():
                return index_path

        # Strategy 4: Try path.html (Next.js static export behavior)
        html_file = base_dir / (path_normalized + '.html')
        if html_file.exists():
            resolved_path = path_normalized + '.html'
            return resolved_path

        # Strategy 5: Check if it's a directory without index.html
        if file_path.exists() and file_path.is_dir():
            # Try index.html in that directory
            index_in_existing_dir = file_path / 'index.html'
            if index_in_existing_dir.exists():
                resolved_path = f"{path_normalized}/index.html"
                return resolved_path

        # Strategy 6: SPA fallback - serve root index.html
        # This allows client-side routing to handle unknown routes
        root_index = base_dir / 'index.html'
        if root_index.exists():
            return 'index.html'

        # Strategy 7: Nothing found - return original path (will 404)
        return path

    print("=" * 80)
    print("SPA ROUTING TEST RESULTS")
    print("=" * 80)

    passed = 0
    failed = 0

    for input_path, expected, description in test_cases:
        result = resolve_spa_path(base_dir, input_path)

        # Check if file exists
        resolved_file = base_dir / result
        file_exists = resolved_file.exists() and resolved_file.is_file()

        # Determine test status
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"\n{status} - {description}")
        print(f"  Input:    '{input_path}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        print(f"  File exists: {file_exists}")

        if result != expected:
            print(f"  ⚠️  Mismatch detected!")

    print("\n" + "=" * 80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    # Additional info
    print("\n📁 File structure check:")
    if base_dir.exists():
        print(f"  - index.html: {(base_dir / 'index.html').exists()}")
        print(f"  - private.html: {(base_dir / 'private.html').exists()}")
        print(f"  - private/index.html: {(base_dir / 'private' / 'index.html').exists()}")
        print(f"  - private/centrifugo/index.html: {(base_dir / 'private' / 'centrifugo' / 'index.html').exists()}")
    else:
        print(f"  ⚠️  Base directory does not exist!")


if __name__ == '__main__':
    test_resolve_spa_path()
