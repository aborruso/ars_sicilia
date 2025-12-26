## Implementation

- [x] 1.1 Add `no_transcript` column to anagrafica CSV schema (update header row)
- [x] 1.2 Modify `generate_digests.sh`: add transcript size check after `qv` download (threshold: 100 bytes)
- [x] 1.3 Modify `generate_digests.sh`: mark video as `no_transcript=true` in CSV when transcript too small
- [x] 1.4 Modify `generate_digests.sh`: skip videos with `no_transcript=true` before download attempt
- [x] 1.5 Modify `generate_digests.sh`: add separate counter `no_transcript_count` for skipped no-transcript videos
- [x] 1.6 Update final summary log to show "Skipped (no transcript): N" separately from "Falliti: N"
- [x] 1.7 Test with known silent video (e.g., `dIkMd2LLKgw` with 0 minutes duration)
- [x] 1.8 Verify CSV update mechanism works correctly (mlr or direct echo append)

## Validation

- [ ] 2.1 Run script on full anagrafica and verify no-transcript videos are detected
- [ ] 2.2 Re-run script and verify no-transcript videos are skipped (no retry attempts)
- [ ] 2.3 Check final log output shows correct counters
- [ ] 2.4 Verify existing digest JSONs are not deleted for no-transcript videos
