# NFL prediction input archive

Approved November 20, 2026. Engine Actions runs retain compressed JSON audit
inputs for 90 days. Artifact names include the GitHub run ID and attempt.
Local runs are opt-in through NFL_AUDIT_DIR; no extra API requests are made.

Inputs include the loaded market quotes, schedule, player history and context.
Candidate/estimate stages and pre-publication selections are saved separately.
NFL includes current injury, roster, snap and matchup inputs. NHL includes
skater/goalie histories, splits and the exact candidate summaries sent to Gemini.
Only existing fields are captured: no missing injury, line assignment, confirmed
goalie status, probability or usage information is invented.

Each snapshot records capture time, commit, run ID and stage. These files are
not publication receipts, bets, or proof of model accuracy. Historical input
timestamps still require validation before replay; a snapshot may include
already-started games. Unsuccessful runs upload any stages already captured.
An early exit before input assembly can legitimately produce no artifact.

The helper receives explicit data objects only, not environment dumps, API
clients, credentials or request headers. Artifacts inherit repository Actions
access. The repository's artifact retention policy may further limit retention.
Archive folders are ignored by Git. Pick rules and probability calculations
are unchanged. This does not backfill past input snapshots.

Verify after pushing: run the engine, open that Actions run, download its
nfl-accuracy-inputs artifact and inspect the gzip JSON stage files.
Run helper tests with python -m unittest discover -s tests -p test_accuracy_archive.py.
