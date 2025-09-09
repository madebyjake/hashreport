## v1.1.0 (2025-09-09)

### Feat

- **scanner**: rework scanning session handling
- **scanner**: improve file filtering logic
- **filters**: add pattern matching functions
- **config**: enhance settings validation

### Fix

- **docs**: update link to upgrade doc

### Refactor

- move size validation to utils
- **tests**: remove redundant file tests
- **scanner**: remove unused file processing logic

## v1.0.0 (2025-07-06)

### Feat

- enhance report viewing and comparison
- add size string parsing utility
- add type definitions and validation utilities
- add performance metrics and adaptive scaling
- add email options validation

### Fix

- update config retrieval in CLI
- use default email config if empty
- improve hostname validation regex
- improve error handling and logging

### Refactor

- update imports for type definitions
- improve type hints in thread pool
- update JSON report type hints
- enhance CSV report type hints
- update type hints and validation
- improve config type hints and validation
- remove alias from scan command
- enhance config validation and defaults

## v0.9.0 (2025-06-24)

### Feat

- **utils**: add progress bar show file names

### Fix

- **utils**: improve filtering logic
- **utils**: restore email and validation exception

### Refactor

- enhance report validation and streaming
- **cli**: improve config and report commands
- **reports**: simplify filelist name gen

## v0.8.1 (2025-03-06)

### Fix

- **config**: fix no valid config found message

## v0.8.0 (2025-03-06)

### Feat

- **cli**: update cli to use version module
- **version**: add version module

### Fix

- poetry-dynamic-versioning to dev

### Refactor

- **cli**: use dynamic version
- **cli**: simplify version message

## v0.7.1 (2025-03-04)

### Fix

- **tools**: update build deps
- **tools**: add psutil to build

## v0.7.0 (2025-03-04)

### Feat

- **config**: add mmap_threshold
- **utils**: implement mmap for large files
- **config**: add new resource management settings
- **utils**: rework thread_pool module
- **utils**: add timing and improve formatting
- **utils**: add input validation and sanitization

### Fix

- **utils**: fix result assignment
- **utils**: update to properly close progress bar

### Refactor

- **utils**: move filter logic into helper

## v0.6.0 (2025-02-24)

### Feat

- add package build and release scripts for RPM

## v0.5.0 (2025-02-18)

### Feat

- **cli**: implement config command and refactor
- **config**: implement user config management
- **utils**: add report viewer and comparison

### Fix

- **cli**: fix size validation logic
- **viewer**: attribute ref in display_comparison

## v0.4.0 (2025-02-03)

### BREAKING CHANGE

- Pattern matching now only uses filenames instead of full paths

### Feat

- **utils**: improve scanner utility
- **cli**: add filelist command and cleanup
- **reports**: add filelist report handler
- **utils**: improve regex pattern matching
- add flag to run no-recursive

### Fix

- **cli**: reword recursive option help message
- correct output format handling

## v0.3.0 (2025-01-27)

### Feat

- rework to use improved config module
- add support for multiple output formats

### Fix

- **utils**: ensure progress bar updates correctly
- **scanner**: handle output extensions and paths
- **reports**: improve method validation
- **reports**: handle redundant exception types
- **reports**: handle redundant exception types
- **utils**: improve error logging
- **cli**: handle output path and format properly
- **utils**: modify get_report_filename
- **utils**: improve error logging
- **cli**: handle output path and format properly
- **utils**: modify get_report_filename

### Refactor

- remove old config module
- remove const module

## v0.2.0 (2025-01-24)

### Feat

- **reports**: add json handler
- **reports**: add csv handler
- **reports**: add base classes for handlers
- **reports**: add reports package
- **utils**: add email_sender module (not tested)
- **utils**: add threading module
- **utils**: add config module
- **utils**: add conversions module
- **utils**: add progress_bar module
- **utils**: add exceptions module
- **utils**: add filters module
- **utils**: add hasher module
- **utils**: add logging module
- **utils**: add scanner module
- **cli**: rework cli
- **cli**: add cli module
- **const**: handle errors reading TOML files
- **scripts**: add common check_dependency
- **scripts**: add scripts for performing common tasks
- add const module

### Fix

- **tests**: add a space to nosec
- **docs**: correct link to getting-started/install page
- comment-out coverage fail_under condition
- change coverage source from string to list
