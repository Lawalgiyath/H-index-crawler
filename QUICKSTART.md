# 🚀 Quick Start Guide - 5 Minutes to Your First Report

## Step 1: Start the Application (30 seconds)

### Windows
```bash
start_app.bat
```

### Mac/Linux
```bash
python3 Crawlee.py
```

**Wait for**: "Running on http://127.0.0.1:5000"

---

## Step 2: Open Your Browser (10 seconds)

Navigate to:
```
http://localhost:5000
```

You should see the University of Lagos Scholar Metrics Intelligence Portal.

---

## Step 3: Upload Test File (20 seconds)

1. Click the **file upload button**
2. Select **`test_sample.json`** from the project folder
3. Click **"Start Scholar Crawler"**

---

## Step 4: Wait for Results (1-2 minutes)

- You'll see a loading animation
- Processing takes ~20-40 seconds for 3 people
- **Do not close the browser**

---

## Step 5: Download Report (10 seconds)

1. Results appear in a table
2. Click **"Download CSV Report"**
3. Open in Excel or Google Sheets

---

## 🎉 Done!

You've successfully:
- ✅ Started the application
- ✅ Processed Google Scholar data
- ✅ Exported a CSV report

---

## Next Steps

### Test with Your Data

1. **Have a Word document?**
   ```bash
   python convert_docx_to_json.py
   ```

2. **Have a JSON file?**
   - Upload directly through the web interface

3. **Need to create JSON?**
   ```json
   [
     {"name": "John Doe", "department": "Chemistry"},
     {"name": "Jane Smith", "department": "Physics"}
   ]
   ```
   Save as `your_file.json`

---

## Deploy Online (Optional)

### Easiest: Render.com (Free)

1. Push code to GitHub
2. Connect to Render.com
3. Deploy in 2 clicks
4. Get public URL

**Full instructions**: See `DEPLOYMENT.md`

---

## Need Help?

- 📖 **Detailed Guide**: `USER_GUIDE.md`
- 🚀 **Deployment**: `DEPLOYMENT.md`
- 📋 **Overview**: `README.md`
- 🐛 **Issues**: Check error messages in terminal

---

## Common First-Time Issues

### "Address already in use"
```python
# Change port in Crawlee.py (last line)
app.run(debug=True, port=5001)
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Invalid JSON"
- Check format at jsonlint.com
- Use test_sample.json as template

---

**Total Time**: ~5 minutes  
**Difficulty**: ⭐ Easy  
**Result**: Working web application with sample data

**Ready to process your full staff list?** See USER_GUIDE.md
