## v0.6.0 (2025-02-24)

### Feat

- **tools**: add gendeb for generating deb files
- **tools**: add genspec for generating rpm spec

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
