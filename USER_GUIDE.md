# User Guide - Google Scholar Metrics Intelligence Portal

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Preparing Your Data](#preparing-your-data)
3. [Using the Web Interface](#using-the-web-interface)
4. [Understanding the Results](#understanding-the-results)
5. [Exporting Data](#exporting-data)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### What This Tool Does

The Google Scholar Metrics Intelligence Portal automatically:
- Searches for staff members on Google Scholar
- Extracts their citation metrics
- Compiles data into organized reports
- Exports results as CSV files

### What You Need

1. A list of staff names (in JSON format)
2. An internet connection
3. A web browser
4. Basic understanding of JSON format (or use our converter tool)

---

## 📝 Preparing Your Data

### Method 1: Create JSON File Manually

Create a file with `.json` extension containing:

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

**Key Points:**
- Each person needs a `name` and `department`
- Names should match Google Scholar profiles
- Use proper JSON syntax (quotes, commas, brackets)

### Method 2: Convert from Word Document

If you have names in a Word document:

1. Save your Word file in the project folder
2. Run the converter:
   ```bash
   python convert_docx_to_json.py
   ```
3. A JSON file will be created automatically

### Sample Files Included

- `test_sample.json` - Small sample (3 people) for quick testing
- `chemistry_staff.json` - Generated from Word document

---

## 🖥️ Using the Web Interface

### Step 1: Start the Application

**On Windows:**
```bash
start_app.bat
```

**On Mac/Linux:**
```bash
python3 Crawlee.py
```

### Step 2: Open Your Browser

Navigate to:
```
http://localhost:5000
```

### Step 3: Upload Your JSON File

1. Click the file upload button
2. Select your JSON file
3. Click "Start Scholar Crawler"

### Step 4: Wait for Processing

- The system will search for each person on Google Scholar
- This includes intentional delays (2-4 seconds per person)
- A loading animation will show progress
- **DO NOT close the browser during processing**

### Step 5: View Results

Results appear in a table showing:
- Staff Name
- Department
- Citations (All-time and Since 2021)
- H-Index (All-time and Since 2021)
- i10-Index (All-time and Since 2021)

---

## 📊 Understanding the Results

### Citation Metrics Explained

#### **Total Citations**
- Number of times the researcher's work has been cited
- **All-time**: Complete citation count
- **Since 2021**: Recent citations (last ~5 years)

#### **H-Index**
- A researcher has an h-index of h if:
  - They have h papers cited at least h times each
- **Example**: h-index of 20 = 20 papers with 20+ citations each
- **Interpretation**:
  - 0-10: Early career or minimal publications
  - 10-20: Established researcher
  - 20-40: Highly productive researcher
  - 40+: Leading scholar in field

#### **i10-Index**
- Number of publications with at least 10 citations
- **Example**: i10 of 15 = 15 papers with 10+ citations
- Shows breadth of impact

### What "N/A" Means

If you see "N/A" in results:
- No Google Scholar profile found for that person
- Name might not match exactly
- Profile might be private or restricted
- Person may not have published academic work

---

## 💾 Exporting Data

### Download CSV Report

1. After processing completes
2. Click "Download CSV Report" button
3. File downloads as `unilag_scholar_metrics_report.csv`
4. Open with Excel, Google Sheets, or any spreadsheet software

### Using Exported Data

**In Excel:**
1. Double-click the CSV file
2. Use "Sort & Filter" to analyze
3. Create charts and visualizations
4. Calculate department averages

**In Google Sheets:**
1. Go to Google Sheets
2. File → Import → Upload
3. Select your CSV file

**Sample Analysis:**
```
=AVERAGE(C2:C50)    // Average citations
=SUM(C2:C50)        // Total citations
=MAX(E2:E50)        // Highest H-index
```

---

## 💡 Tips & Best Practices

### For Best Results

1. **Use Full Names**
   - Include middle initials if known
   - Example: "John A. Smith" vs "John Smith"

2. **Check Name Spelling**
   - Verify names are spelled correctly
   - Small errors can prevent profile discovery

3. **Process in Batches**
   - For large lists (50+ people), consider breaking into smaller batches
   - This makes it easier to track progress

4. **Run During Off-Peak Hours**
   - Better Google Scholar availability
   - Faster processing

5. **Keep Backups**
   - Save your JSON files
   - Keep copies of CSV exports

### Understanding Processing Time

- **Small batch (1-10 people)**: 20-40 seconds
- **Medium batch (10-50 people)**: 2-5 minutes
- **Large batch (50+ people)**: 5-15 minutes

**Why so long?**
- Intentional delays prevent overwhelming Google Scholar
- Ensures reliable data extraction
- Respects Google's rate limits

---

## 🔧 Troubleshooting

### Problem: App Won't Start

**Solution:**
```bash
# Check if Python is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Try different port
# Edit Crawlee.py line at bottom:
app.run(debug=True, port=5001)
```

### Problem: "Invalid JSON" Error

**Solution:**
- Use a JSON validator: https://jsonlint.com
- Check for:
  - Missing commas between entries
  - Missing quotes around text
  - Extra commas at the end
  - Matching brackets [ ]

**Valid JSON Example:**
```json
[
  {
    "name": "Person One",
    "department": "Department A"
  },
  {
    "name": "Person Two",
    "department": "Department B"
  }
]
```

### Problem: Many "N/A" Results

**Possible Causes:**
1. Names don't match Google Scholar profiles exactly
2. Staff members don't have Google Scholar profiles
3. Profiles are private

**Solutions:**
- Try variations of names (with/without middle initial)
- Manually verify profiles exist on Google Scholar
- Contact staff to confirm their Scholar profile names

### Problem: Processing Seems Stuck

**What to do:**
- Wait patiently (delays are normal)
- Check your internet connection
- If truly stuck (10+ minutes), refresh and try again
- Try with a smaller batch first

### Problem: Can't Download CSV

**Solutions:**
- Check if browser is blocking downloads
- Try a different browser
- Results appear even if download fails - you can copy from the table

---

## 📈 Advanced Usage

### Creating Department Reports

1. Process all staff from one department
2. Download CSV
3. In Excel:
   - Calculate average H-index: `=AVERAGE(E:E)`
   - Find top performers: Sort by Citations (All)
   - Create charts showing distribution

### Tracking Over Time

1. Run the same JSON file periodically (e.g., every 6 months)
2. Save CSVs with dates: `chemistry_2026_09.csv`
3. Compare metrics over time
4. Track growth in citations and H-index

### Bulk Processing Multiple Departments

Create separate JSON files:
- `chemistry_staff.json`
- `physics_staff.json`
- `biology_staff.json`

Process each separately, then combine CSVs in Excel.

---

## 📞 Getting Help

### If You Encounter Issues

1. **Check this guide first**
2. **Verify your JSON format** at jsonlint.com
3. **Test with sample file** (test_sample.json)
4. **Review error messages** carefully
5. **Check application logs** if accessible

### Contact Information

For technical support, contact:
- University IT Department
- System Administrator
- Academic Analytics Team

---

## 📋 Quick Reference

### File Upload Requirements
- Format: `.json`
- Structure: Array of objects
- Required fields: `name`, `department`
- Encoding: UTF-8

### Supported Browsers
- ✓ Chrome (recommended)
- ✓ Firefox
- ✓ Edge
- ✓ Safari

### Processing Limits
- Recommended: 50 people per batch
- Maximum: 100 people (technical limit)
- Time per person: 2-4 seconds

### Output Format
- CSV (Comma-Separated Values)
- UTF-8 encoding
- Compatible with Excel, Google Sheets

---

## 🎓 Example Workflow

### Complete Process from Start to Finish

1. **Prepare Data**
   ```
   chemistry_staff.docx → python convert_docx_to_json.py → chemistry_staff.json
   ```

2. **Start Application**
   ```
   start_app.bat
   ```

3. **Open Browser**
   ```
   http://localhost:5000
   ```

4. **Upload & Process**
   - Click upload button
   - Select chemistry_staff.json
   - Click "Start Scholar Crawler"
   - Wait for completion

5. **Review Results**
   - Check the table
   - Verify data looks correct
   - Note any N/A entries

6. **Export Data**
   - Click "Download CSV Report"
   - Save as: `chemistry_metrics_2026_09_30.csv`

7. **Analyze in Excel**
   - Open CSV file
   - Sort by H-Index
   - Create summary statistics
   - Generate charts

---

## 📚 Additional Resources

### Learn More About Metrics

- **Google Scholar Help**: https://scholar.google.com/intl/en/scholar/help.html
- **Understanding H-Index**: Academic literature on citation metrics
- **Research Impact**: University library resources

### JSON Resources

- **JSON Validator**: https://jsonlint.com
- **JSON Tutorial**: https://www.w3schools.com/js/js_json_intro.asp
- **JSON Formatter**: https://jsonformatter.org

---

**Version**: 1.0.0  
**Last Updated**: September 30, 2026  
**For**: University of Lagos Faculty & Staff
