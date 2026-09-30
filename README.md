# University of Lagos - Google Scholar Metrics Intelligence Portal

A web-based application to automatically extract and aggregate Google Scholar metrics (H-index, citations, i10-index) for university staff members.

## 🎯 Features

- **Automated Web Scraping**: Extracts metrics directly from Google Scholar profiles
- **Batch Processing**: Process multiple staff members from a JSON file
- **Real-time Results**: View results in a professional dashboard
- **CSV Export**: Download complete reports in CSV format
- **Responsive Design**: Modern UI built with Tailwind CSS

## 📊 Metrics Extracted

- Total Citations (All-time & Since 2021)
- H-Index (All-time & Since 2021)
- i10-Index (All-time & Since 2021)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Install required packages:
```bash
pip install flask beautifulsoup4 pandas requests python-docx
```

2. Run the application:
```bash
python Crawlee.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## 📝 Usage

### Preparing Your Staff Data

1. **Option A: Use JSON directly**
   - Create a JSON file with the following format:
   ```json
   [
     {
       "name": "John Doe",
       "department": "Chemistry"
     },
     {
       "name": "Jane Smith",
       "department": "Physics"
     }
   ]
   ```

2. **Option B: Convert from Word Document**
   - Place staff names in a Word document (one per line)
   - Run the conversion script:
   ```bash
   python convert_docx_to_json.py
   ```

### Running the Scraper

1. Start the Flask application
2. Upload your JSON file through the web interface
3. Click "Start Scholar Crawler"
4. Wait for processing (includes delays to respect Google's rate limits)
5. Download results as CSV

## 📁 Project Structure

```
H-index/
├── Crawlee.py                      # Main Flask application
├── convert_docx_to_json.py         # Word to JSON converter
├── Chemistry Dept Staff.docx       # Sample staff document
├── chemistry_staff.json            # Generated staff list
├── test_sample.json                # Small sample for testing
└── README.md                       # This file
```

## ⚙️ Configuration

### Rate Limiting

The scraper includes automatic delays (2-4 seconds) between requests to:
- Respect Google Scholar's terms of service
- Avoid IP blocking
- Ensure reliable data extraction

### User Agent

The application uses a realistic browser user agent to ensure proper access to Google Scholar.

## 🔧 Technical Details

### Technologies Used

- **Backend**: Flask (Python web framework)
- **Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas
- **Frontend**: HTML5, Tailwind CSS, Lucide Icons

### How It Works

1. **Profile Discovery**: Searches Google Scholar for each staff member
2. **ID Extraction**: Extracts unique Scholar profile IDs
3. **Metrics Scraping**: Visits each profile and extracts citation metrics
4. **Data Aggregation**: Compiles results into a structured format
5. **Export**: Generates downloadable CSV reports

## 🚀 Deployment Options

### Option 1: Local Deployment

Run on your local machine (already configured):
```bash
python Crawlee.py
```

### Option 2: Cloud Deployment (PythonAnywhere)

1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload your files via the Files tab
3. Set up a web app:
   - Framework: Flask
   - Python version: 3.8+
   - WSGI file: Point to your `Crawlee.py`
4. Install requirements in a Bash console:
   ```bash
   pip install --user flask beautifulsoup4 pandas requests
   ```
5. Reload your web app

### Option 3: Heroku Deployment

1. Create `requirements.txt`:
   ```
   flask==3.1.2
   beautifulsoup4==4.14.3
   pandas==3.0.1
   requests==2.34.2
   gunicorn==21.2.0
   ```

2. Create `Procfile`:
   ```
   web: gunicorn Crawlee:app
   ```

3. Deploy:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   git push heroku main
   ```

### Option 4: Docker Deployment

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "Crawlee.py"]
   ```

2. Build and run:
   ```bash
   docker build -t scholar-scraper .
   docker run -p 5000:5000 scholar-scraper
   ```

## ⚠️ Important Notes

### Legal & Ethical Considerations

- **Terms of Service**: Web scraping Google Scholar should be done responsibly
- **Rate Limiting**: Built-in delays prevent overloading Google's servers
- **Academic Use**: Intended for institutional research and analytics
- **Respect Robots.txt**: Be mindful of Google's scraping policies

### Limitations

- **Profile Matching**: Relies on correct name matching in Google Scholar
- **Public Data Only**: Only extracts publicly available information
- **Rate Limits**: Large batches may take significant time
- **Accuracy**: Metrics depend on Google Scholar's data quality

## 🐛 Troubleshooting

### Common Issues

**Problem**: "N/A" appearing in results
- **Solution**: Staff member may not have a Google Scholar profile or name doesn't match exactly

**Problem**: Slow processing
- **Solution**: This is normal - delays are intentional to respect rate limits

**Problem**: Connection errors
- **Solution**: Check internet connection and ensure Google Scholar is accessible

## 📊 Sample Output

```csv
Name,Department,Citations_All,Citations_Since_2021,H_Index_All,H_Index_Since_2021,I10_Index_All,I10_Index_Since_2021
John Doe,Chemistry,1250,450,18,12,35,22
Jane Smith,Physics,890,320,15,10,28,18
```

## 🤝 Contributing

This is an institutional tool. For improvements or bug fixes:
1. Test thoroughly with sample data
2. Document any changes
3. Ensure compliance with ethical scraping practices

## 📄 License

Internal use for University of Lagos academic analytics.

## 👥 Support

For technical issues or questions about the tool, contact the IT department or development team.

## 🔄 Version History

- **v1.0.0** (2026-09-30): Initial release with core functionality
  - Google Scholar profile discovery
  - Metrics extraction (H-index, citations, i10-index)
  - Web interface with CSV export
  - Word document converter

---

**Built with ❤️ for University of Lagos Academic Excellence**
