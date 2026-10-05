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

# scholarly - handles Google Scholar anti-bot automatically
try:
    from scholarly import scholarly, ProxyGenerator
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    print("scholarly not installed - falling back to requests")

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

def extract_staff_from_excel(file_path):
    """Extract staff from Excel file. Expects 'Name' and optional 'Department' columns."""
    staff = []
    try:
        df = pd.read_excel(file_path)
        # Check if structured (has Name column)
        cols = [c.lower() for c in df.columns]
        
        name_col = None
        dept_col = None
        
        for c in df.columns:
            if 'name' in c.lower(): name_col = c
            if 'department' in c.lower() or 'dept' in c.lower(): dept_col = c
            
        if name_col:
            for _, row in df.iterrows():
                name = str(row[name_col]).strip()
                if name and name != 'nan':
                    dept = str(row[dept_col]).strip() if dept_col else "University of Lagos"
                    if dept == 'nan': dept = "University of Lagos"
                    staff.append({"name": name, "department": dept})
            return staff

        # Fallback to unstructured extraction
        skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                        'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
        names = []
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
        return [{"name": n, "department": "University of Lagos"} for n in set(names)]
    except Exception as e:
        print(f"Excel extraction error: {e}")
        return []

def extract_staff_from_csv(file_path):
    """Extract staff from CSV file. Expects 'Name' and optional 'Department' columns."""
    staff = []
    try:
        df = pd.read_csv(file_path)
        # Check if structured (has Name column)
        cols = [c.lower() for c in df.columns]
        
        name_col = None
        dept_col = None
        
        for c in df.columns:
            if 'name' in c.lower(): name_col = c
            if 'department' in c.lower() or 'dept' in c.lower(): dept_col = c
            
        if name_col:
            for _, row in df.iterrows():
                name = str(row[name_col]).strip()
                if name and name != 'nan':
                    dept = str(row[dept_col]).strip() if dept_col else "University of Lagos"
                    if dept == 'nan': dept = "University of Lagos"
                    staff.append({"name": name, "department": dept})
            return staff
            
        # Fallback to unstructured extraction if no Name column found
        skip_keywords = ['b.sc', 'm.sc', 'ph.d', 'professor', 'department', 'email', 
                        'tel:', 'fax:', 'university', 'research', 'lecturer', 'dr.']
        names = []
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
        
        return [{"name": n, "department": "University of Lagos"} for n in set(names)]
    except Exception as e:
        print(f"CSV extraction error: {e}")
        return []

def convert_document_to_json(file_path, filename, default_department="University of Lagos"):
    """Convert various document formats to JSON staff list"""
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext == 'csv':
        return extract_staff_from_csv(file_path)
    if ext in ['xlsx', 'xls']:
        return extract_staff_from_excel(file_path)
        
    names = []
    if ext == 'docx':
        names = extract_names_from_docx(file_path)
    elif ext == 'pdf':
        names = extract_names_from_pdf(file_path)
    elif ext == 'txt':
        names = extract_names_from_txt(file_path)
    
    staff_list = [{"name": name, "department": default_department} for name in names]
    return staff_list

# ---------------------------------------------------------------------------
# SCHOLARLY-BASED SCRAPING  (handles Google Scholar anti-bot automatically)
# ---------------------------------------------------------------------------
_scholarly_ready = False

def _setup_scholarly():
    """Configure scholarly. We removed FreeProxies() because it hangs indefinitely and causes timeouts."""
    global _scholarly_ready
    if _scholarly_ready or not SCHOLARLY_AVAILABLE:
        return
    try:
        # DO NOT use FreeProxies() as it hangs the entire process trying to test public proxies.
        print("[SCHOLARLY] Using direct connection for speed.")
        _scholarly_ready = True
    except Exception as e:
        print(f"[SCHOLARLY] Proxy setup failed: {e} - continuing without proxy")
        _scholarly_ready = True

def get_scholar_id(name):
    """Find Google Scholar user ID for a person using scholarly."""
    _setup_scholarly()

    if SCHOLARLY_AVAILABLE:
        try:
            query = f"{name} University of Lagos"
            search_results = scholarly.search_author(query)
            author = next(search_results, None)
            if author:
                # Verify the name matches
                found_name = author.get('name', '').lower()
                search_parts = name.lower().split()
                if any(p in found_name for p in search_parts if len(p) > 3):
                    return author.get('scholar_id')
            return None
        except StopIteration:
            return None
        except Exception as e:
            print(f"[scholarly] Error searching {name}: {e}")
            # Fall through to requests fallback

    # Fallback: raw requests or Apify (for cloud deployments like Render)
    import os
    token = os.environ.get('APIFY_TOKEN')
    if token:
        try:
            print(f"[Apify Fallback] Searching Google Scholar for {name}...")
            from apify_client import ApifyClient
            client = ApifyClient(token)
            run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input={
                "query": name, "maxResults": 3, "includeDetails": False, "compact": True
            })
            for item in client.dataset((run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id)).iterate_items():
                res_id = item.get('userId')
                if res_id:
                    return res_id
        except Exception as e:
            print(f"[Apify Fallback] Error: {e}")
            
    return _get_scholar_id_requests(name)

def _get_scholar_id_requests(name):
    """Raw requests fallback for get_scholar_id."""
    query = urllib.parse.quote(f"{name} University of Lagos")
    search_url = f"https://scholar.google.com/scholar?hl=en&q={query}"
    for attempt in range(3):
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(search_url, timeout=15)
            if response.status_code == 429:
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
            return None
        except Exception as e:
            print(f"[requests] Error for {name}: {e}")
            if attempt < 2:
                time.sleep(random.uniform(3, 6))
    return None

def scrape_scholar_metrics(user_id):
    """Get citation metrics for a Scholar user ID using raw requests for speed."""
    # scholarly hangs indefinitely without proxies, so we bypass it directly to raw requests
    return _scrape_metrics_requests(user_id)

def _scrape_metrics_requests(user_id):
    """Raw requests fallback for scrape_scholar_metrics."""
    profile_url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    for attempt in range(3):
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(profile_url, timeout=15)
            
            html_content = ""
            if response.status_code in (429, 503) or (response.status_code == 200 and ("g-recaptcha" in response.text.lower() or "sorry" in response.text.lower() or "did not match any articles" in response.text.lower())):
                # Fallback to Apify if Google blocks the IP (e.g. on Render)
                import os
                from apify_client import ApifyClient
                token = os.environ.get('APIFY_TOKEN')
                if token:
                    print("[Fallback] Using Apify Cheerio Scraper for metrics...")
                    client = ApifyClient(token)
                    run_input = {
                        "startUrls": [{"url": profile_url}],
                        "pageFunction": "async function pageFunction(context) { const $ = context.$; return { html: $('body').html() }; }",
                        "proxyConfiguration": {"useApifyProxy": True}
                    }
                    run = client.actor('apify/cheerio-scraper').call(run_input=run_input)
                    for item in client.dataset((run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id)).iterate_items():
                        html_content = item.get("html", "")
                        break
                if not html_content:
                    time.sleep(random.uniform(5, 10))
                    continue
            elif response.status_code != 200:
                time.sleep(random.uniform(3, 5))
                continue
            else:
                html_content = response.text

            if not html_content:
                continue

            soup = BeautifulSoup(html_content, "html.parser")
            table_rows = soup.select("#gsc_rsb_st tr")
            metrics = {
                "Citations_All": "0", "Citations_Since_2021": "0",
                "H_Index_All": "0", "H_Index_Since_2021": "0",
                "I10_Index_All": "0", "I10_Index_Since_2021": "0"
            }
            
            # Extract Name and Affiliation
            name_elem = soup.select_one("#gsc_prf_in")
            if name_elem:
                metrics["Exact_Name"] = name_elem.text.strip()
            
            affil_elem = soup.select_one(".gsc_prf_il")
            if affil_elem:
                metrics["Exact_Affiliation"] = affil_elem.text.strip()

            for row in table_rows:
                header = row.select_one(".gsc_rsb_sc1")
                values = row.select(".gsc_rsb_std")
                if header and len(values) >= 2:
                    t = header.text.strip().lower()
                    if "citations" in t:
                        metrics["Citations_All"]        = values[0].text.strip()
                        metrics["Citations_Since_2021"] = values[1].text.strip()
                    elif "h-index" in t:
                        metrics["H_Index_All"]          = values[0].text.strip()
                        metrics["H_Index_Since_2021"]   = values[1].text.strip()
                    elif "i10" in t:
                        metrics["I10_Index_All"]        = values[0].text.strip()
                        metrics["I10_Index_Since_2021"] = values[1].text.strip()
            return metrics
        except Exception as e:
            print(f"[requests] Error fetching metrics: {e}")
            if attempt < 2:
                time.sleep(random.uniform(3, 6))
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
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 lg:col-span-1 space-y-6">
                <!-- Bulk Upload Section -->
                <div>
                    <h2 class="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
                        <i data-lucide="upload-cloud" class="w-5 h-5 text-unilagMaroon"></i>
                        <span>Upload Staff Document</span>
                    </h2>
                    <p class="text-sm text-slate-600 mb-6">
                        Upload any document containing staff names. The system will automatically extract names and retrieve their Google Scholar metrics.
                    </p>
                    
                    <div id="uploadWrapper">
                        <button id="showGuideBtn" type="button" class="w-full bg-slate-100 text-slate-700 font-semibold py-3 px-4 rounded-md hover:bg-slate-200 transition duration-150 flex items-center justify-center space-x-2 border border-slate-300">
                            <i data-lucide="book-open" class="w-5 h-5"></i>
                            <span>Read Data Formatting Guide to Unlock Upload</span>
                        </button>
                        
                        <div id="guideSection" class="hidden mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md shadow-sm">
                            <h3 class="text-sm font-bold text-blue-900 mb-2 flex items-center">
                                <i data-lucide="info" class="w-4 h-4 mr-2"></i> Data Formatting Guide
                            </h3>
                            <p class="text-xs text-blue-800 mb-3">For perfect extraction, upload a <strong>CSV</strong> or <strong>Excel</strong> file structured with two exact columns: <strong>Name</strong> and <strong>Department</strong>.</p>
                            <table class="w-full text-xs text-left bg-white border border-blue-200 rounded overflow-hidden mb-4 shadow-sm">
                                <thead class="bg-blue-100 text-blue-900">
                                    <tr><th class="px-3 py-2 border-r border-blue-200">Name</th><th class="px-3 py-2">Department</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td class="px-3 py-2 border-r border-blue-200">Maureen Egenti</td><td class="px-3 py-2 text-slate-600">Adult Education</td></tr>
                                    <tr><td class="px-3 py-2 border-r border-blue-200">John Doe</td><td class="px-3 py-2 text-slate-600">Computer Science</td></tr>
                                </tbody>
                            </table>
                            <p class="text-xs text-blue-700 italic mb-4">Note: If you upload Word/PDF files, the department will default to "University of Lagos".</p>
                            
                            <button id="unlockUploadBtn" type="button" class="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded hover:bg-blue-700 transition flex items-center justify-center space-x-2">
                                <i data-lucide="unlock" class="w-4 h-4"></i>
                                <span>I understand, unlock upload</span>
                            </button>
                        </div>

                        <form id="uploadForm" class="hidden space-y-4 mt-6">
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
                    </div>

                    <div id="loader" class="hidden mt-6 text-center space-y-3">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-unilagMaroon border-t-transparent"></div>
                        <p class="text-sm font-medium text-slate-600">Crawling Google Scholar metrics...</p>
                    </div>
                </div>

                <!-- Divider -->
                <div class="border-t border-slate-200"></div>

                <!-- Individual Search Section -->
                <div>
                    <h2 class="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
                        <i data-lucide="user-plus" class="w-5 h-5 text-unilagGold"></i>
                        <span>Add Individual Profile</span>
                    </h2>
                    <p class="text-sm text-slate-600 mb-6">
                        Search for one person at a time. Results accumulate in the table.
                    </p>
                    
                    <form id="individualForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">First Name</label>
                            <input type="text" id="firstName" placeholder="e.g., John" required class="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-unilagMaroon text-sm">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Middle Name (Optional)</label>
                            <input type="text" id="middleName" placeholder="e.g., Adeyemi" class="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-unilagMaroon text-sm">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Surname</label>
                            <input type="text" id="lastName" placeholder="e.g., Doe" required class="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-unilagMaroon text-sm">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Department</label>
                            <input type="text" id="departmentIndividual" placeholder="e.g., Chemistry" required class="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-unilagMaroon text-sm">
                        </div>
                        <button type="submit" id="searchIndividualBtn" class="w-full bg-unilagGold text-white font-semibold py-2.5 px-4 rounded-md hover:bg-opacity-90 transition duration-150 flex items-center justify-center space-x-2">
                            <i data-lucide="search" class="w-4 h-4"></i>
                            <span>Search & Add Profile</span>
                        </button>
                    </form>

                    <div id="individualLoader" class="hidden mt-4 text-center space-y-2">
                        <div class="inline-block animate-spin rounded-full h-6 w-6 border-4 border-unilagGold border-t-transparent"></div>
                        <p class="text-xs font-medium text-slate-600">Searching...</p>
                    </div>
                </div>
            </div>

            <!-- Results Panel -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 lg:col-span-2 flex flex-col">
                <div class="flex items-center justify-between mb-4 pb-4 border-b border-slate-100">
                    <h2 class="text-lg font-bold text-slate-900 flex items-center space-x-2">
                        <i data-lucide="bar-chart-3" class="w-5 h-5 text-unilagMaroon"></i>
                        <span>Extraction Results</span>
                    </h2>
                    
                    <div id="downloadContainer" class="hidden flex items-center space-x-2">
                        <button onclick="clearAll()" class="bg-rose-100 text-rose-700 text-xs font-semibold py-1.5 px-3 rounded hover:bg-rose-200 transition flex items-center space-x-1 mr-2" title="Clear All Data">
                            <i data-lucide="trash-2" class="w-4 h-4"></i><span>Clear All</span>
                        </button>
                        <span class="text-xs text-slate-500 font-semibold uppercase tracking-wider mr-1">Download:</span>
                        <button onclick="downloadFormat('csv')" class="bg-emerald-600 text-white text-xs font-semibold py-1.5 px-3 rounded hover:bg-emerald-700 transition flex items-center space-x-1" title="Download as CSV">
                            <i data-lucide="file-text" class="w-4 h-4"></i><span>CSV</span>
                        </button>
                        <button onclick="downloadFormat('excel')" class="bg-emerald-600 text-white text-xs font-semibold py-1.5 px-3 rounded hover:bg-emerald-700 transition flex items-center space-x-1" title="Download as Excel">
                            <i data-lucide="table" class="w-4 h-4"></i><span>Excel</span>
                        </button>
                        <button onclick="downloadFormat('parquet')" class="bg-emerald-600 text-white text-xs font-semibold py-1.5 px-3 rounded hover:bg-emerald-700 transition flex items-center space-x-1" title="Download as Parquet (Parakeet)">
                            <i data-lucide="database" class="w-4 h-4"></i><span>Parquet</span>
                        </button>
                    </div>
                </div>

                <div id="resultsContainer" class="flex-grow overflow-x-auto">
                    <div class="text-center py-16 text-slate-400">
                        <i data-lucide="database" class="w-12 h-12 mx-auto mb-3 stroke-1"></i>
                        <p class="text-sm">No data processed yet. Upload a staff document to begin.</p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        University of Lagos Academic Analytics Service &bull; Powered by Python and BeautifulSoup
    </footer>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-4 right-4 bg-emerald-600 text-white px-6 py-3 rounded-md shadow-lg transform transition-transform duration-300 translate-y-20 opacity-0 z-50 flex items-center space-x-2">
        <i data-lucide="check-circle" class="w-5 h-5"></i>
        <span id="toastMsg" class="font-medium text-sm"></span>
    </div>

    <script>
        lucide.createIcons();
        let globalResults = [];

        // Persistence Load
        window.onload = function() {
            const saved = localStorage.getItem('unilag_scholar_data');
            if (saved) {
                try {
                    globalResults = JSON.parse(saved);
                    if (globalResults.length > 0) {
                        renderTable(globalResults);
                        document.getElementById('downloadContainer').classList.remove('hidden');
                        showToast("Restored your previous results.");
                    }
                } catch(e) { console.error(e); }
            }
        };

        function saveData() {
            localStorage.setItem('unilag_scholar_data', JSON.stringify(globalResults));
        }

        function showToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 3000);
        }

        // Guide Unlock Logic
        document.getElementById('showGuideBtn').addEventListener('click', function() {
            this.classList.add('hidden');
            document.getElementById('guideSection').classList.remove('hidden');
        });
        document.getElementById('unlockUploadBtn').addEventListener('click', function() {
            document.getElementById('guideSection').classList.add('hidden');
            document.getElementById('uploadForm').classList.remove('hidden');
        });

        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('jsonFile');
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const submitBtn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            const resultsContainer = document.getElementById('resultsContainer');
            const downloadContainer = document.getElementById('downloadContainer');

            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50');
            loader.classList.remove('hidden');
            resultsContainer.innerHTML = '<div class="text-center py-16 text-slate-500"><div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-unilagMaroon border-t-transparent mb-3"></div><p class="text-sm" id="progressText">Parsing document...</p></div>';
            downloadContainer.classList.add('hidden');

            try {
                // 1. Upload and parse file
                const response = await fetch('/crawl', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (!data.success) {
                    resultsContainer.innerHTML = `<div class="text-center py-16 text-rose-600"><i data-lucide="alert-circle" class="w-8 h-8 mx-auto mb-2"></i><p class="text-sm font-semibold">${data.error}</p></div>`;
                    lucide.createIcons();
                    return;
                }
                
                const staffList = data.staff_list;
                if (!staffList || staffList.length === 0) {
                    resultsContainer.innerHTML = `<div class="text-center py-16 text-slate-500"><p class="text-sm">No valid names found in document.</p></div>`;
                    return;
                }

                // 2. Process each staff member individually
                // We clear globalResults if user uploaded a new batch, or we can append? Let's append to existing table!
                // Actually, let's keep it simple: we render the table first and then append.
                if (globalResults.length === 0) {
                    renderTable([]); // Just to draw headers
                }
                
                let processedCount = 0;
                
                for (let i = 0; i < staffList.length; i++) {
                    const staff = staffList[i];
                    document.getElementById('progressText').innerText = `Processing ${i + 1} of ${staffList.length}: ${staff.name}...`;
                    
                    // Call individual search
                    let names = staff.name.split(' ');
                    let first = names.length > 1 ? names[0] : staff.name;
                    let last = names.length > 1 ? names.slice(1).join(' ') : '';
                    
                    try {
                        const res = await fetch('/search_individual', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                first_name: first, 
                                last_name: last,
                                affiliation: staff.department || "University of Lagos"
                            })
                        });
                        const resData = await res.json();
                        
                        if (resData.success && resData.result) {
                            globalResults.push(resData.result);
                        } else {
                            // If failed to find, add blank record
                            globalResults.push({
                                "Title": "", "Name": staff.name, "Department": staff.department || "University of Lagos", "Profile_URL": "",
                                "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                                "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                                "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
                            });
                        }
                    } catch (err) {
                        console.error("Individual search failed for", staff.name, err);
                        globalResults.push({
                            "Title": "", "Name": staff.name, "Department": staff.department || "University of Lagos", "Profile_URL": "",
                            "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                            "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                            "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
                        });
                    }
                    
                    processedCount++;
                    saveData();
                    renderTable(globalResults);
                    downloadContainer.classList.remove('hidden');
                }
                
                document.getElementById('progressText').innerText = `Completed processing ${processedCount} records!`;
                showToast("Batch processing completed!");
                
            } catch (err) {
                console.error(err);
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
                document.getElementById('downloadContainer').classList.add('hidden');
                return;
            }

            let html = `
                <table class="w-full text-left border-collapse text-xs">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 uppercase tracking-wider border-b border-slate-200">
                            <th class="p-3 font-semibold">Title</th>
                            <th class="p-3 font-semibold">Staff Name</th>
                            <th class="p-3 font-semibold">Department</th>
                            <th class="p-3 font-semibold">Profile URL</th>
                            <th class="p-3 font-semibold text-center">Citations (All)</th>
                            <th class="p-3 font-semibold text-center">Citations (2021+)</th>
                            <th class="p-3 font-semibold text-center">H-Index (All)</th>
                            <th class="p-3 font-semibold text-center">H-Index (2021+)</th>
                            <th class="p-3 font-semibold text-center">i10-Index (All)</th>
                            <th class="p-3 font-semibold text-center">i10-Index (2021+)</th>
                            <th class="p-3 font-semibold text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
            `;

            results.forEach((row, index) => {
                html += `
                    <tr class="hover:bg-slate-50 group transition-colors">
                        <td class="p-3 font-medium text-slate-900 border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Title', this.innerText)">${row.Title || ''}</td>
                        <td class="p-3 font-medium text-slate-900 border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Name', this.innerText)">${row.Name}</td>
                        <td class="p-3 text-slate-600 border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Department', this.innerText)">${row.Department}</td>
                        <td class="p-3 text-slate-500 truncate max-w-xs border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Profile_URL', this.innerText)">${row.Profile_URL || ''}</td>
                        <td class="p-3 text-center font-semibold text-unilagMaroon border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Citations_All', this.innerText)">${row.Citations_All}</td>
                        <td class="p-3 text-center font-semibold text-slate-700 border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'Citations_Since_2021', this.innerText)">${row.Citations_Since_2021}</td>
                        <td class="p-3 text-center border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'H_Index_All', this.innerText)">${row.H_Index_All}</td>
                        <td class="p-3 text-center border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'H_Index_Since_2021', this.innerText)">${row.H_Index_Since_2021}</td>
                        <td class="p-3 text-center border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'I10_Index_All', this.innerText)">${row.I10_Index_All}</td>
                        <td class="p-3 text-center border border-transparent focus-within:border-unilagGold focus-within:bg-white" contenteditable="true" onblur="updateVal(${index}, 'I10_Index_Since_2021', this.innerText)">${row.I10_Index_Since_2021}</td>
                        <td class="p-3 text-center flex justify-center space-x-1 opacity-20 group-hover:opacity-100 transition-opacity">
                            <button onclick="moveRow(${index}, -1)" class="p-1 hover:bg-slate-200 rounded text-slate-600" title="Move Up"><i data-lucide="arrow-up" class="w-3.5 h-3.5"></i></button>
                            <button onclick="moveRow(${index}, 1)" class="p-1 hover:bg-slate-200 rounded text-slate-600" title="Move Down"><i data-lucide="arrow-down" class="w-3.5 h-3.5"></i></button>
                            <button onclick="deleteRow(${index})" class="p-1 hover:bg-rose-100 rounded text-rose-600" title="Delete"><i data-lucide="trash" class="w-3.5 h-3.5"></i></button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            document.getElementById('resultsContainer').innerHTML = html;
            lucide.createIcons();
        }

        function updateVal(index, key, val) {
            if (globalResults[index][key] !== val.trim()) {
                globalResults[index][key] = val.trim();
                saveData();
                showToast("Value updated");
            }
        }

        function moveRow(index, direction) {
            if (index + direction < 0 || index + direction >= globalResults.length) return;
            const temp = globalResults[index];
            globalResults[index] = globalResults[index + direction];
            globalResults[index + direction] = temp;
            saveData();
            renderTable(globalResults);
        }

        function deleteRow(index) {
            if (confirm("Delete this record?")) {
                globalResults.splice(index, 1);
                saveData();
                renderTable(globalResults);
                showToast("Record deleted");
            }
        }

        function clearAll() {
            if (confirm("Are you sure you want to clear all data? This cannot be undone.")) {
                globalResults = [];
                saveData();
                renderTable(globalResults);
                showToast("All data cleared");
            }
        }

        async function downloadFormat(fmt) {
            if (globalResults.length === 0) return;
            
            try {
                // We show loading state on the button
                const btn = event.currentTarget;
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<div class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div><span>Wait...</span>';
                
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ results: globalResults, format: fmt })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    
                    let ext = fmt === 'excel' ? 'xlsx' : fmt === 'parquet' ? 'parquet' : 'csv';
                    a.download = `unilag_scholar_metrics_report.${ext}`;
                    
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } else {
                    alert("Error generating download file.");
                }
                btn.innerHTML = originalHtml;
                lucide.createIcons();
            } catch (e) {
                alert("Download failed: " + e.message);
            }
        }

        // Individual Search
        document.getElementById('individualForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const firstName = document.getElementById('firstName').value.trim();
            const middleName = document.getElementById('middleName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const department = document.getElementById('departmentIndividual').value.trim();
            
            if (!firstName || !lastName || !department) return;
            
            const btn = document.getElementById('searchIndividualBtn');
            const loader = document.getElementById('individualLoader');
            const resultsContainer = document.getElementById('resultsContainer');
            const downloadContainer = document.getElementById('downloadContainer');
            
            btn.disabled = true;
            btn.classList.add('opacity-50');
            loader.classList.remove('hidden');
            
            try {
                const response = await fetch('/search_individual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        first_name: firstName,
                        middle_name: middleName,
                        last_name: lastName,
                        affiliation: department
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Add to global results
                    globalResults.push(data.result);
                    saveData();
                    
                    // Render table
                    renderTable(globalResults);
                    
                    // Show download buttons
                    downloadContainer.classList.remove('hidden');
                    
                    // Clear form
                    document.getElementById('firstName').value = '';
                    document.getElementById('lastName').value = '';
                    
                    // Show success message
                    showToast(`Found: ${data.result.Name}`);
                } else {
                    alert(`✗ Error: ${data.error}`);
                }
            } catch (err) {
                alert(`✗ Error: ${err.message}`);
            } finally {
                btn.disabled = false;
                btn.classList.remove('opacity-50');
                loader.classList.add('hidden');
                lucide.createIcons();
            }
        });
    </script>
</body>
</html>
"""

from flask import make_response

@app.route('/')
def index():
    response = make_response(render_template_string(INDEX_HTML))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
                try:
                    staff_list = json.loads(content)
                    if not isinstance(staff_list, list):
                        raise ValueError("JSON must be a list of objects.")
                    if len(staff_list) > 0 and 'name' not in staff_list[0]:
                        raise ValueError("JSON objects must contain a 'name' key.")
                except Exception as je:
                    os.remove(temp_path)
                    return jsonify({"success": False, "error": f"JSON Format Error: {str(je)}"})
        else:
            # Convert document to staff list
            staff_list = convert_document_to_json(temp_path, filename)
            
        # Clean up temp file
        os.remove(temp_path)
        
        # Format Checker
        if not staff_list or len(staff_list) == 0:
            return jsonify({
                "success": False, 
                "error": f"Format Error: Could not extract any valid names from the {ext.upper()} file. Please check the Data Formatting Guide."
            })
            
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": f"Error processing file: {str(e)}"})
    
    return jsonify({
        "success": True,
        "staff_list": staff_list
    })

@app.route('/search_individual', methods=['POST'])
def search_individual():
    """Search for a single person by first and last name"""
    try:
        import urllib.parse, requests
        from bs4 import BeautifulSoup
        
        data = request.json
        first_name = data.get('first_name', '').strip()
        middle_name = data.get('middle_name', '').strip()
        last_name = data.get('last_name', '').strip()
        affiliation = data.get('affiliation', 'University of Lagos').strip()
        
        if not first_name and not last_name:
            return jsonify({'success': False, 'error': 'First name and last name required'})
        
        full_name = f"{first_name} {middle_name} {last_name}".strip()
        full_name = " ".join(full_name.split())
        
        # Fallback: if user pasted a URL instead of a name
        if 'user=' in full_name:
            user_id = ""
            for token in full_name.split():
                if 'user=' in token:
                    parsed = urllib.parse.urlparse(token)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if 'user' in qs:
                        user_id = qs['user'][0]
                        break
            if user_id:
                metrics = scrape_scholar_metrics(user_id)
                if metrics:
                    name = "Extracted Profile"
                    try:
                        resp = requests.get(f"https://scholar.google.com/citations?user={user_id}&hl=en", headers=HEADERS)
                        soup = BeautifulSoup(resp.text, "html.parser")
                        name_elem = soup.select_one("#gsc_prf_in")
                        if name_elem:
                            name = name_elem.text
                    except:
                        pass
                    return jsonify({
                        'success': True,
                        'result': {
                            'Title': '',
                            'Name': name,
                            'Department': affiliation,
                            'Citations_All': str(metrics.get('Citations_All', 0)),
                            'Citations_Since_2021': str(metrics.get('Citations_Since_2021', 0)),
                            'H_Index_All': str(metrics.get('H_Index_All', 0)),
                            'H_Index_Since_2021': str(metrics.get('H_Index_Since_2021', 0)),
                            'I10_Index_All': str(metrics.get('I10_Index_All', 0)),
                            'I10_Index_Since_2021': str(metrics.get('I10_Index_Since_2021', 0)),
                            'Profile_URL': f"https://scholar.google.com/citations?user={user_id}"
                        }
                    })

        # Use Apify Google Search to find the profile accurately
        from apify_client import ApifyClient
        
        APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')
        if not APIFY_TOKEN:
            return jsonify({'success': False, 'error': 'APIFY_TOKEN environment variable is not set. Please set it and restart the server.'})
        client = ApifyClient(APIFY_TOKEN)
        
        full_name = f"{first_name} {last_name}".strip()
        
        query = f'{full_name}'
        
        user_id = None
        matched_url = None
        debug_info = []
        
        try:
            run_input = {
                "query": query,
                "maxResults": 20,
                "includeDetails": True,
                "compact": False
            }
            
            run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
            
            for item in client.dataset((run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id)).iterate_items():
                res_name = (item.get('name') or '').lower()
                res_affil = (item.get('affiliation') or '').lower()
                res_id = item.get('userId')
                
                if not res_id:
                    continue
                
                last_lower = last_name.lower()
                affil_lower = affiliation.lower()
                
                # Check fuzzy match
                last_parts = [p for p in last_lower.replace('-', ' ').split() if len(p) > 2]
                first_parts = [p for p in first_name.lower().replace('-', ' ').split() if len(p) > 2]
                all_parts = last_parts + first_parts
                name_match = any(p in res_name for p in all_parts) if all_parts else (last_lower in res_name)
                affil_match = (
                    affil_lower in res_name or affil_lower in res_affil
                    or 'lagos' in res_affil or 'unilag' in res_affil
                )
                
                if name_match and affil_match:
                    user_id = res_id
                    matched_url = f"https://scholar.google.com/citations?user={user_id}"
                    break
                elif name_match and not user_id:
                    # Weaker match - fallback
                    user_id = res_id
                    matched_url = f"https://scholar.google.com/citations?user={user_id}"
        except Exception as qe:
            debug_info.append(f"Search Query Exception: {str(qe)}")
            print(f"[Search] Query failed: {query} -> {qe}")
        if user_id:
            try:
                metrics = scrape_scholar_metrics(user_id)
            except Exception as me:
                metrics = None
                debug_info.append(f"Metrics Scrape Exception: {str(me)}")

            if metrics:
                profile_name = metrics.get('Exact_Name', full_name)
                profile_dept = affiliation
                
                title = ""
                prefixes = ["prof. ", "prof ", "professor ", "dr. ", "dr ", "mr. ", "mr ", "mrs. ", "mrs ", "engr. ", "engr ", "arc. ", "arc ", "pharm. ", "pharm "]
                lname = profile_name.lower()
                for p in prefixes:
                    if lname.startswith(p):
                        # Use the original case for Title if possible, or just capitalize the prefix
                        title = p.strip().capitalize()
                        if title == "Prof": title = "Prof."
                        elif title == "Dr": title = "Dr."
                        elif title == "Mr": title = "Mr."
                        elif title == "Mrs": title = "Mrs."
                        elif title == "Engr": title = "Engr."
                        elif title == "Arc": title = "Arc."
                        elif title == "Pharm": title = "Pharm."
                        
                        profile_name = profile_name[len(p):].strip()
                        break

                return jsonify({
                    'success': True,
                    'result': {
                        'Title': title,
                        'Name': profile_name,
                        'Department': profile_dept,
                        'Citations_All': str(metrics.get('Citations_All', 0)),
                        'Citations_Since_2021': str(metrics.get('Citations_Since_2021', 0)),
                        'H_Index_All': str(metrics.get('H_Index_All', 0)),
                        'H_Index_Since_2021': str(metrics.get('H_Index_Since_2021', 0)),
                        'I10_Index_All': str(metrics.get('I10_Index_All', 0)),
                        'I10_Index_Since_2021': str(metrics.get('I10_Index_Since_2021', 0)),
                        'Profile_URL': f"https://scholar.google.com/citations?user={user_id}"
                    }
                })
            else:
                debug_info.append(f"Found user_id {user_id}, but scrape_scholar_metrics returned None.")

        return jsonify({
            'success': False, 
            'error': f'No profile found for {full_name}. Debug Info: {"; ".join(debug_info)}'
        })
    
    except Exception as e:
        print(f"[DEBUG] Search individual exception: {e}")
        return jsonify({'success': False, 'error': f"Fatal Error: {str(e)}"})

@app.route('/download', methods=['POST'])
def download():
    """Generates the downloadable file dynamically in the selected format"""
    data = request.json
    results = data.get('results', [])
    fmt = data.get('format', 'csv')
    
    if not results:
        return jsonify({"error": "No data available"}), 400
        
    df = pd.DataFrame(results)
    
    import io
    from flask import send_file, Response
    
    if fmt == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=scholar_metrics.csv"}
        )
    elif fmt == 'excel':
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="unilag_scholar_metrics_report.xlsx"
        )
    elif fmt == 'parquet':
        output = io.BytesIO()
        # Fast parquet serialization
        df.to_parquet(output, index=False, engine='pyarrow')
        output.seek(0)
        return send_file(
            output,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="unilag_scholar_metrics_report.parquet"
        )
        
    return jsonify({"error": "Invalid format"}), 400

@app.route('/health')
def health():
    return jsonify({"status": "ok", "scholarly": SCHOLARLY_AVAILABLE})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
