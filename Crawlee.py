import os
import json
import time
import random
import urllib.parse
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify
from docx import Document
import PyPDF2
import openpyxl
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'json', 'docx', 'pdf', 'txt', 'xlsx', 'xls', 'csv'}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_names_from_docx(file_path):
    """Extract names from Word document"""
    doc = Document(file_path)
    names = []
    skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 'tel:', 
                     'fax:', 'university', 'research', 'lecturer', 'dr.', 'analysis']
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text and len(text) > 5 and len(text) < 50:
            text_lower = text.lower()
            if not any(kw in text_lower for kw in skip_keywords):
                if any(char in text for char in ['(', ')', '@', ',']):
                    continue
                words = text.split()
                if len(words) >= 2 and any(w[0].isupper() for w in words if w):
                    names.append(text.strip())
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text and len(text) > 5 and len(text) < 50:
                    text_lower = text.lower()
                    if not any(kw in text_lower for kw in skip_keywords):
                        if any(char in text for char in ['(', ')', '@', ',']):
                            continue
                        words = text.split()
                        if len(words) >= 2 and text not in names:
                            names.append(text.strip())
    
    return list(set(names))

def extract_names_from_pdf(file_path):
    """Extract names from PDF document"""
    names = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                           'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 5 and len(line) < 50:
                        line_lower = line.lower()
                        if not any(kw in line_lower for kw in skip_keywords):
                            if any(char in line for char in ['(', ')', '@', ',']):
                                continue
                            words = line.split()
                            if len(words) >= 2 and any(w[0].isupper() for w in words if w):
                                names.append(line.strip())
    except Exception as e:
        print(f"PDF extraction error: {e}")
    
    return list(set(names))

def extract_names_from_txt(file_path):
    """Extract names from text file"""
    names = []
    skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                     'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 50:
                line_lower = line.lower()
                if not any(kw in line_lower for kw in skip_keywords):
                    if any(char in line for char in ['(', ')', '@', ',']):
                        continue
                    words = line.split()
                    if len(words) >= 2 and any(w[0].isupper() for w in words if w):
                        names.append(line.strip())
    
    return list(set(names))

def extract_names_from_excel(file_path):
    """Extract names from Excel file"""
    names = []
    try:
        df = pd.read_excel(file_path)
        skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                        'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
        
        for col in df.columns:
            for value in df[col].dropna():
                text = str(value).strip()
                if text and len(text) > 5 and len(text) < 50:
                    text_lower = text.lower()
                    if not any(kw in text_lower for kw in skip_keywords):
                        if any(char in text for char in ['(', ')', '@', ',']):
                            continue
                        words = text.split()
                        if len(words) >= 2 and any(w[0].isupper() for w in words if w):
                            names.append(text.strip())
    except Exception as e:
        print(f"Excel extraction error: {e}")
    
    return list(set(names))

def extract_names_from_csv(file_path):
    """Extract names from CSV file"""
    names = []
    try:
        df = pd.read_csv(file_path)
        skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                        'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
        
        for col in df.columns:
            for value in df[col].dropna():
                text = str(value).strip()
                if text and len(text) > 5 and len(text) < 50:
                    text_lower = text.lower()
                    if not any(kw in text_lower for kw in skip_keywords):
                        if any(char in text for char in ['(', ')', '@', ',']):
                            continue
                        words = text.split()
                        if len(words) >= 2 and any(w[0].isupper() for w in words if w):
                            names.append(text.strip())
    except Exception as e:
        print(f"CSV extraction error: {e}")
    
    return list(set(names))

def convert_document_to_json(file_path, filename, department="University of Lagos"):
    """Convert various document formats to JSON staff list"""
    ext = filename.rsplit('.', 1)[1].lower()
    names = []
    
    if ext == 'docx':
        names = extract_names_from_docx(file_path)
    elif ext == 'pdf':
        names = extract_names_from_pdf(file_path)
    elif ext == 'txt':
        names = extract_names_from_txt(file_path)
    elif ext in ['xlsx', 'xls']:
        names = extract_names_from_excel(file_path)
    elif ext == 'csv':
        names = extract_names_from_csv(file_path)
    
    staff_list = [{"name": name, "department": department} for name in names]
    return staff_list

def get_scholar_id(name):
    query = urllib.parse.quote(f"{name} University of Lagos")
    search_url = f"https://scholar.google.com/scholar?hl=en&q={query}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Add session for better connection handling
            session = requests.Session()
            session.headers.update(HEADERS)
            
            response = session.get(search_url, timeout=15)
            
            if response.status_code == 429:  # Too many requests
                time.sleep(random.uniform(10, 15))
                continue
            
            if response.status_code != 200:
                time.sleep(random.uniform(3, 5))
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            profile_link = soup.select_one(".gs_ai_pho a") or soup.select_one("h3.gs_rt a")
            
            if profile_link and "user=" in profile_link.get("href", ""):
                href = profile_link["href"]
                parsed_url = urllib.parse.urlparse(href)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if "user" in query_params:
                    return query_params["user"][0]
            
            # If no profile found, return None (not an error)
            return None
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 8))
                continue
            return None
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 8))
                continue
            return None
        except Exception as e:
            print(f"Error for {name}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 6))
                continue
            return None
    
    return None

def scrape_scholar_metrics(user_id):
    profile_url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            
            response = session.get(profile_url, timeout=15)
            
            if response.status_code == 429:  # Too many requests
                time.sleep(random.uniform(10, 15))
                continue
            
            if response.status_code != 200:
                time.sleep(random.uniform(3, 5))
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            table_rows = soup.select("#gsc_rsb_st tr")
            
            metrics = {
                "Citations_All": "0", "Citations_Since_2021": "0",
                "H_Index_All": "0", "H_Index_Since_2021": "0",
                "I10_Index_All": "0", "I10_Index_Since_2021": "0"
            }
            
            for row in table_rows:
                header = row.select_one(".gsc_rsb_sc1")
                values = row.select(".gsc_rsb_std")
                if header and len(values) >= 2:
                    row_title = header.text.strip().lower()
                    val_all = values[0].text.strip()
                    val_recent = values[1].text.strip()
                    if "citations" in row_title:
                        metrics["Citations_All"] = val_all
                        metrics["Citations_Since_2021"] = val_recent
                    elif "h-index" in row_title:
                        metrics["H_Index_All"] = val_all
                        metrics["H_Index_Since_2021"] = val_recent
                    elif "i10-index" in row_title:
                        metrics["I10_Index_All"] = val_all
                        metrics["I10_Index_Since_2021"] = val_recent
            
            return metrics
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 8))
                continue
            return None
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 8))
                continue
            return None
        except Exception as e:
            print(f"Error scraping metrics: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 6))
                continue
            return None
    
    return None

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University of Lagos Scholar Metrics Intelligence Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        unilagMaroon: '#7A0016',
                        unilagGold: '#C5A059',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-unilagMaroon text-white shadow-md border-b-4 border-unilagGold">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="bg-white p-2 rounded-lg shadow">
                    <i data-lucide="graduation-cap" class="w-8 h-8 text-unilagMaroon"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-wide">University of Lagos</h1>
                    <p class="text-xs text-unilagGold font-semibold tracking-wider uppercase">Google Scholar Metrics Intelligence Portal</p>
                </div>
            </div>
            <div class="flex items-center space-x-2 text-sm text-slate-200">
                <i data-lucide="shield-check" class="w-4 h-4 text-unilagGold"></i>
                <span>Institutional Research Analytics</span>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Control Panel -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 lg:col-span-1">
                <h2 class="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
                    <i data-lucide="upload-cloud" class="w-5 h-5 text-unilagMaroon"></i>
                    <span>Upload Staff Document</span>
                </h2>
                <p class="text-sm text-slate-600 mb-6">
                    Upload any document containing staff names. The system will automatically extract names and retrieve their Google Scholar metrics.
                </p>
                
                <form id="uploadForm" class="space-y-4">
                    <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Upload Document</label>
                    <input type="file" id="jsonFile" accept=".json,.docx,.pdf,.txt,.xlsx,.xls,.csv" required class="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-unilagMaroon file:text-white hover:file:bg-opacity-90 cursor-pointer border border-slate-200 rounded-md">
                    <p class="text-xs text-slate-500 mt-2">Supported: JSON, Word (DOCX), PDF, Text (TXT), Excel (XLSX, XLS), CSV</p>
                </div>
                    <button type="submit" id="submitBtn" class="w-full bg-unilagMaroon text-white font-semibold py-2.5 px-4 rounded-md hover:bg-opacity-90 transition duration-150 flex items-center justify-center space-x-2">
                        <i data-lucide="play" class="w-4 h-4"></i>
                        <span>Start Scholar Crawler</span>
                    </button>
                </form>

                <div id="loader" class="hidden mt-6 text-center space-y-3">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-unilagMaroon border-t-transparent"></div>
                    <p class="text-sm font-medium text-slate-600">Crawling Google Scholar metrics...</p>
                </div>
            </div>

            <!-- Results Panel -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 lg:col-span-2 flex flex-col">
                <div class="flex items-center justify-between mb-4 pb-4 border-b border-slate-100">
                    <h2 class="text-lg font-bold text-slate-900 flex items-center space-x-2">
                        <i data-lucide="bar-chart-3" class="w-5 h-5 text-unilagMaroon"></i>
                        <span>Extraction Results</span>
                    </h2>
                    <button id="downloadBtn" class="hidden bg-emerald-600 text-white text-sm font-semibold py-2 px-4 rounded-md hover:bg-emerald-700 transition duration-150 flex items-center space-x-2">
                        <i data-lucide="download" class="w-4 h-4"></i>
                        <span>Download CSV Report</span>
                    </button>
                </div>

                <div id="resultsContainer" class="flex-grow overflow-x-auto">
                    <div class="text-center py-16 text-slate-400">
                        <i data-lucide="database" class="w-12 h-12 mx-auto mb-3 stroke-1"></i>
                        <p class="text-sm">No data processed yet. Upload a staff JSON file to begin.</p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        University of Lagos Academic Analytics Service &bull; Powered by Python and BeautifulSoup
    </footer>

    <script>
        lucide.createIcons();
        let csvDataGlobal = null;

        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('jsonFile');
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const submitBtn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            const resultsContainer = document.getElementById('resultsContainer');
            const downloadBtn = document.getElementById('downloadBtn');

            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50');
            loader.classList.remove('hidden');
            resultsContainer.innerHTML = '<div class="text-center py-16 text-slate-500"><div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-unilagMaroon border-t-transparent mb-3"></div><p class="text-sm">Processing profiles across Google Scholar...</p></div>';
            downloadBtn.classList.add('hidden');

            try {
                const response = await fetch('/crawl', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    csvDataGlobal = data.csv_data;
                    renderTable(data.results);
                    downloadBtn.classList.remove('hidden');
                } else {
                    resultsContainer.innerHTML = `<div class="text-center py-16 text-rose-600"><i data-lucide="alert-circle" class="w-8 h-8 mx-auto mb-2"></i><p class="text-sm font-semibold">${data.error}</p></div>`;
                    lucide.createIcons();
                }
            } catch (err) {
                resultsContainer.innerHTML = `<div class="text-center py-16 text-rose-600"><i data-lucide="alert-circle" class="w-8 h-8 mx-auto mb-2"></i><p class="text-sm font-semibold">Network error occurred. This might happen if:</p><ul class="text-xs mt-2 list-disc list-inside"><li>Google Scholar is blocking the server IP</li><li>Too many requests were made</li><li>Internet connection issue</li></ul><p class="text-xs mt-4">Try again with fewer names or wait a few minutes.</p></div>`;
                lucide.createIcons();
            } finally {
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-50');
                loader.classList.add('hidden');
                lucide.createIcons();
            }
        });

        function renderTable(results) {
            if (!results || results.length === 0) {
                document.getElementById('resultsContainer').innerHTML = '<p class="text-center py-8 text-slate-500">No records found.</p>';
                return;
            }

            let html = `
                <table class="w-full text-left border-collapse text-xs">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 uppercase tracking-wider border-b border-slate-200">
                            <th class="p-3 font-semibold">Staff Name</th>
                            <th class="p-3 font-semibold">Department</th>
                            <th class="p-3 font-semibold text-center">Citations (All)</th>
                            <th class="p-3 font-semibold text-center">Citations (2021+)</th>
                            <th class="p-3 font-semibold text-center">H-Index (All)</th>
                            <th class="p-3 font-semibold text-center">H-Index (2021+)</th>
                            <th class="p-3 font-semibold text-center">i10-Index (All)</th>
                            <th class="p-3 font-semibold text-center">i10-Index (2021+)</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
            `;

            results.forEach(row => {
                html += `
                    <tr class="hover:bg-slate-50">
                        <td class="p-3 font-medium text-slate-900">${row.Name}</td>
                        <td class="p-3 text-slate-600">${row.Department}</td>
                        <td class="p-3 text-center font-semibold text-unilagMaroon">${row.Citations_All}</td>
                        <td class="p-3 text-center font-semibold text-slate-700">${row.Citations_Since_2021}</td>
                        <td class="p-3 text-center">${row.H_Index_All}</td>
                        <td class="p-3 text-center">${row.H_Index_Since_2021}</td>
                        <td class="p-3 text-center">${row.I10_Index_All}</td>
                        <td class="p-3 text-center">${row.I10_Index_Since_2021}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            document.getElementById('resultsContainer').innerHTML = html;
        }

        document.getElementById('downloadBtn').addEventListener('click', function() {
            if (!csvDataGlobal) return;
            const blob = new Blob([csvDataGlobal], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'unilag_scholar_metrics_report.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/crawl', methods=['POST'])
def crawl():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Empty filename"})
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "File type not supported. Please upload JSON, DOCX, PDF, TXT, XLSX, XLS, or CSV"})
    
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        # Save uploaded file temporarily
        temp_path = os.path.join(os.getcwd(), filename)
        file.save(temp_path)
        
        # Process based on file type
        if ext == 'json':
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                staff_list = json.loads(content)
        else:
            # Convert document to staff list
            staff_list = convert_document_to_json(temp_path, filename)
            if not staff_list:
                os.remove(temp_path)
                return jsonify({"success": False, "error": f"Could not extract names from {ext.upper()} file"})
        
        # Clean up temp file
        os.remove(temp_path)
        
    except json.JSONDecodeError:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": "Invalid JSON document format"})
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": f"Error processing file: {str(e)}"})
    
    results = []
    for staff in staff_list:
        name = staff.get("name")
        department = staff.get("department", "University of Lagos")
        if not name:
            continue
        
        user_id = get_scholar_id(name)
        if not user_id:
            results.append({
                "Name": name, "Department": department,
                "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
            })
        else:
            metrics = scrape_scholar_metrics(user_id)
            record = {"Name": name, "Department": department}
            if metrics:
                record.update(metrics)
            else:
                record.update({
                    "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                    "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                    "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
                })
            results.append(record)
        time.sleep(random.uniform(3, 6))  # Increased delay to avoid blocking
    
    df = pd.DataFrame(results)
    csv_string = df.to_csv(index=False)
    
    return jsonify({
        "success": True,
        "results": results,
        "csv_data": csv_string
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)