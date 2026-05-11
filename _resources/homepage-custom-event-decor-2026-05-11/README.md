# Homepage Custom Event Decor Archive - 2026-05-11

Purpose: preserve the hidden homepage `Custom Event Decor` block before it was
removed from the launch page.

## Contents

- `custom-event-decor-before-hide.png` - live screenshot of the block at
  1366px width before hiding.
- `icons/` - extracted SVG source for the eight inline category icons.
- `icons-manifest.json` - label-to-file manifest for the extracted icons.

## Current Site State

The homepage controller sets `show_custom_event_decor = False`, and
`home.html` only renders the block when that flag is explicitly true.

To restore the block, flip the flag intentionally, rerun website cache clear,
then verify the homepage desktop/mobile layout gates before committing.
