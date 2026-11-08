# Domain profiles

Read this when the user names a profile (for example "Initialize continuity in this project.
Profile: video") or when a project's work is mainly a game, video edit or motion graphics.
A profile adds one compact `## Profile: NAME` section to the checkpoint, after State. It
extends the base template and never replaces it; the six base sections stay required.

| Profile | Use for | Section records |
| --- | --- | --- |
| `game` | Small games and prototypes | Engine and version, run/build commands, scene or level checklist, input mapping, last playtest, known bugs |
| `video` | Edits and renders, for example with ffmpeg scripts | Output spec, read-only sources, edit order or EDL, exact final render command, output versions with the latest marked, running renders |
| `motion` | Motion graphics, for example Remotion, Manim, Lottie or CSS | Tool and preview command, style-tokens file path, compositions with frame ranges, preview and final render status |

Profiles combine: `profile: video, motion` adds both sections. With the helper:

```sh
python3 SKILL/scripts/handoff.py init --project PROJECT --profile video,motion
```

Without the helper, copy the matching files from `assets/profiles/` into the checkpoint after
State, add `- profile: NAMES` below the `writer` line, and fill every REPLACE line from
inspected files. Link existing files (an EDL, a style-tokens file, a bug tracker) instead of
copying them. `check` warns when a listed profile has no section.

Rules that matter after a switch:

- Before starting a long render, record its exact command, output path and start time.
  A successor must check that output, and whether the process still runs, before rendering
  again. `inject.py` prints these lines under "Running operations".
- Treat source footage as read-only. Write renders to a separate output folder.
- For motion work, read the style-tokens file before producing visual output, so every
  agent keeps the same colors, fonts, easing and durations.

Size budget: each profile template stays under 150 words, and the base template with all
three profiles stays under 700 words, so a filled checkpoint can stay near the 1,200-word
reading target. Tests enforce both.

## Contributing a profile

Add `assets/profiles/NAME.md` with a lowercase name. The first line is `## Profile: NAME`;
every other line is one `Label: REPLACE with ...` instruction. Stay under the word budget,
and record links rather than content. Update this table and the tests in
`tests/test_profiles.py`. A profile must not add required files, dependencies or tools.
Deferred to v0.3.0: a media manifest command and a style-tokens template.
