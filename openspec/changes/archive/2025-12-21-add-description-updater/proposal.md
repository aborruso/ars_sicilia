# Change: Add tool to update video descriptions with seduta token

## Why
Existing videos already uploaded need the new unique seduta token and updated search link in their descriptions. Doing this manually is error-prone and slow.

## What Changes
- Add a script that scans `data/anagrafica_video.csv` and updates YouTube descriptions for videos missing the token.
- Preserve existing title/tags/category while updating only the description.
- Provide a dry-run mode to preview changes.

## Impact
- Affected specs: `ars-video-maintenance`
- Affected code: `src/metadata.py`, new script `update_descriptions.py`
