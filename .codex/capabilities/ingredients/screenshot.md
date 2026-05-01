---
name: Screenshot
level: ingredient
last_verified: 2026-04-25
---

## What it does

Captures the current screen to a file on disk so the agent can inspect it like any other image.

## When to reach for it

- The user mentions a UI bug, a layout issue, or anything visual you can't see from the code alone.
- You've made a frontend change and want to verify the result without asking the user to describe it.
- Anything where "look at the screen" would unblock you.

## How to use it

Use whichever screenshot tool exists on the host:

- **macOS:** `screencapture -x ~/screenshot.png`
- **Linux (X11):** `import -window root ~/screenshot.png`
- **Linux (Wayland):** `grim ~/screenshot.png`
- **Windows (PowerShell):** `Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{PRTSC}')` — or write a small Python script using `Pillow.ImageGrab.grab().save('~/screenshot.png')`.

Then `Read ~/screenshot.png`.

## What it depends on

Nothing. This is a base ingredient — one tool, no composition.

## Failure modes

- **Multi-monitor setups capture only the primary display by default.** Pass `-D <display>` (macOS) or use `grim -o <output>` (Wayland) to target a specific screen.
- **Permission prompts.** First run on macOS will prompt for Screen Recording permission. The script will appear to hang until the user approves.
- **Headless environments.** No display = no screenshot. Don't reach for this in CI.
