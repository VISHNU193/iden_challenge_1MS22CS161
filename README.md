# Iden Challenge Automation Script

A robust Playwright-based automation script for extracting product data from the Iden Challenge application with intelligent batch processing and incremental file saving.

## Features

- **Batch Processing**: Extracts data in configurable batches (default: 250 products)
- **Incremental Saving**: Saves data regularly to prevent loss during long extractions
- **Session Management**: Maintains login sessions across runs
- **Memory Efficient**: Processes data incrementally instead of loading everything at once
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Recovery**: Continues processing even if individual batches fail
- **Duplicate Prevention**: Avoids re-extracting already processed products

## Requirements

- Python 3.7+
- Playwright
- Modern web browser (Chromium/Chrome)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/VISHNU193/iden_challenge_1MS22CS161
cd iden_challenge_1MS22CS161
```

2. Install Python dependencies:
```bash
pip install playwright
```

3. Install browser dependencies:
```bash
playwright install
```

## Configuration

Before running the script, update the credentials in the `__init__` method:

```python
self.credentials = {
    "email": "your_email@example.com",
    "password": "your_password"
}
```

### Configurable Parameters

You can modify these settings in the `main()` function:

- `BASE_URL`: The application URL (default: "https://hiring.idenhq.com/")
- `HEADLESS`: Run browser in headless mode (default: True)
- `BATCH_SIZE`: Products per batch (default: 2000)

## Usage

### Basic Usage

```bash
python3 iden_challenge_final_script.py
```

### Configuration Options

```python
# In main() function, modify these values:
BASE_URL = "https://hiring.idenhq.com/"
HEADLESS = True  # Set to False to see browser in action
BATCH_SIZE = 250  # Adjust batch size as needed
```

## How It Works

### Authentication Flow
1. Checks for existing session file
2. If no valid session, performs fresh login
3. Navigates through the application hierarchy

### Navigation Path
```
Login → Instructions → Challenge → Dashboard → Inventory → Products → Full Catalog
```

### Data Extraction Process
1. **Incremental Loading**: Scrolls progressively to trigger lazy loading
2. **Batch Detection**: Monitors product count and processes in batches
3. **Data Extraction**: Extracts product details using robust DOM selectors
4. **File Saving**: Saves each batch to individual files
5. **Final Consolidation**: Creates a final file with all products

### Extracted Data Fields

For each product, the script extracts:
- **Name**: Product title
- **ID**: Unique product identifier
- **Category**: Product category
- **Description**: Product description
- **Dimensions**: Product dimensions
- **Price**: Raw price string and parsed numeric value
- **Updated**: Last update timestamp
- **Extraction Metadata**: Timestamp of data extraction

## Output Files

### Batch Files
```
batch_data_YYYYMMDD_HHMMSS/
├── batch_001.json
├── batch_002.json
├── batch_003.json
└── ...
```

Each batch file contains:
```json
{
  "batch_metadata": {
    "batch_number": 1,
    "timestamp": "2025-09-01T10:30:00",
    "products_in_batch": 250,
    "total_products_so_far": 250,
    "base_url": "https://hiring.idenhq.com/"
  },
  "products": [...]
}
```

### Final Consolidated File
```
all_products_YYYYMMDD_HHMMSS.json
```

Contains all extracted products with comprehensive metadata:
```json
{
  "extraction_metadata": {
    "timestamp": "2025-09-01T12:45:00",
    "total_products": 15000,
    "total_batches": 60,
    "batch_size": 250,
    "base_url": "https://hiring.idenhq.com/",
    "extractor": "Iden Challenge Playwright Automation - Batch Processing"
  },
  "products": [...]
}
```

### Session File
```
session_state.json
```
Stores authentication session for reuse in subsequent runs.

### Log File
```
iden_challenge.log
```
Comprehensive logs of the extraction process.

## Example Product Data Structure

```json
{
  "name": "Ultimate Clothing Tool",
  "id": 12345,
  "category": "Tools",
  "description": "Professional clothing management system",
  "dimensions": "10x5x2 inches",
  "price": "$49.99",
  "price_value": 49.99,
  "updated": "2025-08-15",
  "extracted_at": "2025-09-01T10:30:15.123Z"
}
```

## Error Handling

The script includes robust error handling:

- **Network Issues**: Automatic retries and graceful degradation
- **Authentication Failures**: Clear error messages and session management
- **Element Detection**: Multiple selector strategies for reliability
- **Data Parsing**: Safe extraction with fallbacks for missing elements
- **Interruption Recovery**: Saves partial data if script is stopped

## Logging

Comprehensive logging includes:
- Authentication status
- Navigation progress
- Batch processing updates
- Error details and recovery attempts
- Performance metrics

Log levels can be configured in the logging setup section.

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check credentials in the script
   - Verify the login URL is correct
   - Check for CAPTCHA or 2FA requirements

2. **Products Not Loading**
   - Increase scroll delay in configuration
   - Check if page structure has changed
   - Use debug mode to inspect page elements

3. **Batch Processing Stuck**
   - Verify lazy loading is working properly
   - Check network connectivity
   - Monitor log files for specific errors

### Debug Mode

To enable detailed debugging, modify the logging level:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

Or use the `debug_page_structure()` method to inspect page elements.


### Memory Management
- Script processes data incrementally
- Batch files prevent memory accumulation
- Session reuse reduces authentication overhead

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Update documentation as needed
5. Submit a pull request


---
