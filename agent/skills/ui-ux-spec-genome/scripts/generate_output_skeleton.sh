#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  generate_output_skeleton.sh [out_root] [--force]

Notes:
  - Default out_root is ./ui-ux-spec.
  - Creates the standard output folders and placeholder Markdown files.
  - Existing files are preserved unless --force is provided.
EOF
}

out_root="ui-ux-spec"
force=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -f|--force)
      force=1
      shift
      ;;
    *)
      if [[ "$1" == -* ]]; then
        echo "Unknown option: $1" >&2
        usage
        exit 2
      fi
      out_root="$1"
      shift
      ;;
  esac
done

mkdir -p "$out_root"

dirs=(
  "01_Foundation"
  "02_Components"
  "03_Patterns"
  "04_Pages"
  "05_A11y"
  "06_Assets"
  "07_Engineering_Constraints"
)

for d in "${dirs[@]}"; do
  mkdir -p "$out_root/$d"
done

write_file() {
  local path="$1"
  local content="$2"
  if [[ -f "$path" && $force -eq 0 ]]; then
    echo "skip: $path"
    return
  fi
  printf "%s\n" "$content" > "$path"
  echo "write: $path"
}

write_file "$out_root/01_Foundation/FOUNDATION.md" \
"# Foundation

## Tokens
- Colors:
- Typography:
- Spacing:
- Radius:
- Shadow:
- Z-index:
- Motion:

## Global styles
- Reset/normalize:
- Body defaults:
- Links/forms:
- Focus-visible:
- Scrollbar/selection:
"

write_file "$out_root/02_Components/COMPONENTS.md" \
"# Components

## Inventory
- Component list:

## Per component template
- Purpose:
- Structure/slots:
- Variants:
- States:
- Interaction:
- A11y:
- Responsive:
- Motion:
- Theming hooks:
- Edge cases:
"

write_file "$out_root/03_Patterns/PATTERNS.md" \
"# Patterns

- Search/filter:
- Pagination/table:
- Form submit/validation:
- Confirm/destructive:
- Empty/loading/error:
"

write_file "$out_root/04_Pages/PAGES.md" \
"# Pages

- List page skeleton:
- Detail page skeleton:
- Form page skeleton:
- Dashboard skeleton:
"

write_file "$out_root/05_A11y/A11Y.md" \
"# Accessibility

- Keyboard navigation:
- Focus management:
- ARIA roles/labels:
- Contrast:
- Reduced motion:
"

write_file "$out_root/06_Assets/ASSETS.md" \
"# Assets

- Logo variants:
- Icons:
- Illustrations:
- Image rules:
- Fonts:
"

write_file "$out_root/07_Engineering_Constraints/ENGINEERING.md" \
"# Engineering Constraints

- CSS architecture:
- Naming conventions:
- Theming mechanism:
- Lint/style rules:
- Storybook/visual tests:
"
