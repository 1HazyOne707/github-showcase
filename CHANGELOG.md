# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- Notification-aware profile-stats automation with a recent-merges feed
- Interactive ontology graph visualization on the dashboard
- Live GitHub system metrics on the dashboard
- Structured ontology model with validation workflow
- GitHub Pages dashboard
- Basic GitHub Actions CI pipeline

### Fixed
- `update_profile_stats.py` was a non-functional placeholder; now pulls
  real merged-PR/repo counts via `gh search` and writes them into
  `README.md`
