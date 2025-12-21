# Change: Update video title format to separate seduta and recording date

## Why
Some sedute span multiple days, so the recording date can differ from the official seduta date. The current title uses the recording date, which is confusing. We want the title to keep the seduta date and explicitly show the recording date/time.

## What Changes
- Update the YouTube title format to:
  `Lavori d'aula: seduta n. {numero} ({data_seduta}), {data_video} dalle ore {ora_video}`
- Add a script option to backfill titles for already uploaded videos.

## Impact
- Affected specs: `ars-video-metadata`
- Affected code: `src/metadata.py`, new or updated script for title backfill
