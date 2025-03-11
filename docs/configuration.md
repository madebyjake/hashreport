# **Configuration Options**

hashreport uses a TOML configuration file to store user settings. The default location is `~/.config/hashreport/settings.toml`.

## **Core Settings**

Basic application settings:

```toml
[hashreport]
# Hash algorithm and output settings
default_algorithm = "md5"
default_format = "csv"
supported_formats = ["csv", "json"]

# File processing settings
chunk_size = 4096
mmap_threshold = 10485760  # 10MB - Use mmap for files larger than this
timestamp_format = "%y%m%d-%H%M"
show_progress = true
max_errors_shown = 10
```

### **Core Settings**

- `default_algorithm`: Default hash algorithm to use (default: "md5")
- `default_format`: Default output format (default: "csv")
- `supported_formats`: List of supported output formats (default: ["csv", "json"])
- `chunk_size`: Size of chunks for file reading in bytes (default: 4096)
- `mmap_threshold`: Size threshold for memory-mapped files in bytes (default: 10485760)
- `timestamp_format`: Format for timestamps in report filenames (default: "%y%m%d-%H%M")
- `show_progress`: Show progress bar during processing (default: true)
- `max_errors_shown`: Maximum number of errors to display (default: 10)

## **Resource Management**

Control system resource usage:

```toml
[hashreport]
# Resource monitoring settings
memory_threshold = 0.85  # % of total memory
min_workers = 2
max_workers = 0  # 0 = Use CPU count
worker_adjust_interval = 60  # seconds
memory_limit = 0  # 0 = 75% of total RAM
batch_size = 1000
max_retries = 3
retry_delay = 1.0
resource_check_interval = 1.0  # seconds
progress_update_interval = 0.1  # seconds
```

### **Resource Settings**

- `memory_threshold`: Memory usage threshold as percentage of total RAM (default: 0.85)
- `min_workers`: Minimum number of worker threads (default: 2)
- `max_workers`: Maximum number of worker threads (default: 0 - uses CPU count)
- `worker_adjust_interval`: Interval for adjusting worker count in seconds (default: 60)
- `memory_limit`: Memory limit in MB (default: 0 - uses 75% of total RAM)
- `batch_size`: Number of files to process in each batch (default: 1000)
- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 1.0)
- `resource_check_interval`: Interval for resource checks in seconds (default: 1.0)
- `progress_update_interval`: Interval for progress updates in seconds (default: 0.1)

## **File Processing**

Configure file processing behavior:

```toml
[hashreport]
# File processing settings
min_file_size = "0B"
max_file_size = ""  # Empty string = No limit
default_recursive = true
ignore_hidden_files = true
ignore_system_files = true
excluded_directories = [".git", "__pycache__", "node_modules"]
excluded_extensions = [""]
```

### **File Processing Settings**

- `min_file_size`: Minimum file size to process (default: "0B")
- `max_file_size`: Maximum file size to process (default: "" - no limit)
- `default_recursive`: Process subdirectories by default (default: true)
- `ignore_hidden_files`: Skip hidden files (default: true)
- `ignore_system_files`: Skip system files (default: true)
- `excluded_directories`: List of directories to exclude (default: [".git", "__pycache__", "node_modules"])
- `excluded_extensions`: List of file extensions to exclude (default: [""])

## **Email Settings**

Configure email notification settings:

```toml
[hashreport.email_defaults]
port = 587
use_tls = true
host = "localhost"
timeout = 30
default_subject = "HashReport Results"
retry_attempts = 3
```

### **Email Settings**

- `port`: SMTP server port (default: 587)
- `use_tls`: Use TLS for SMTP connection (default: true)
- `host`: SMTP server hostname (default: "localhost")
- `timeout`: SMTP connection timeout in seconds (default: 30)
- `default_subject`: Default email subject (default: "HashReport Results")
- `retry_attempts`: Number of email sending retry attempts (default: 3)

## **Logging Settings**

Configure logging behavior:

```toml
[hashreport.logging]
level = "INFO"
file_logging = false
log_directory = "logs"
max_log_size = "10MB"
backup_count = 5
```

### **Logging Settings**

- `level`: Logging level (default: "INFO")
- `file_logging`: Enable file logging (default: false)
- `log_directory`: Directory for log files (default: "logs")
- `max_log_size`: Maximum size of log files (default: "10MB")
- `backup_count`: Number of log file backups to keep (default: 5)

## **Progress Display**

Configure progress bar behavior:

```toml
[hashreport.progress]
refresh_rate = 0.1
show_eta = true
show_file_names = true
show_speed = true
```

### **Progress Settings**

- `refresh_rate`: Progress bar refresh rate in seconds (default: 0.1)
- `show_eta`: Show estimated time remaining (default: true)
- `show_file_names`: Show current file being processed (default: true)
- `show_speed`: Show processing speed (default: true)

## **Report Settings**

Configure report generation:

```toml
[hashreport.reports]
include_metadata = true
include_timing = true
max_concurrent_writes = 4
compression = false
```

### **Report Settings**

- `include_metadata`: Include file metadata in reports (default: true)
- `include_timing`: Include timing information in reports (default: true)
- `max_concurrent_writes`: Maximum number of concurrent report writes (default: 4)
- `compression`: Enable report compression (default: false)

## **Environment Variables**

For sensitive settings, use environment variables:

```bash
# Email settings
export HASHREPORT_SMTP_HOST=smtp.example.com
export HASHREPORT_SMTP_USER=username
export HASHREPORT_SMTP_PASSWORD=password

# Resource limits
export HASHREPORT_MAX_MEMORY=2048
```

## **Managing Configuration**

### **View Current Settings**

```bash
hashreport config show
```

### **Edit Settings**

```bash
hashreport config edit
```

The editor used is determined by:
1. $VISUAL environment variable
2. $EDITOR environment variable
3. Platform default (vi/vim on Unix, notepad on Windows)

Settings are automatically validated when saved.
