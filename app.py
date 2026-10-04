"""
Google Scholar Metrics Bulk Scraper Web App
"""
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
import io
import threading
from werkzeug.utils import secure_filename
from datetime import datetime

# Import scraping logic
from apify_end_to_end_scraper import get_profile_url_with_apify, scrape_metrics_with_apify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = 'scholar_results.json'

# Global progress state
crawl_progress = {
    'total': 0,
    'current': 0,
    'status': 'idle'
}

def load_results():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}")
    return []

def save_results(results):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def crawl_worker(staff_list):
    global crawl_progress
    results = load_results()
    
    success_count = 0
    crawl_progress['total'] = len(staff_list)
    crawl_progress['current'] = 0
    crawl_progress['status'] = 'running'
    
    for person in staff_list:
        name = person.get('name', '')
        if not name:
            crawl_progress['current'] += 1
            continue
            
        department = person.get('department', 'Unknown')
        
        record = {
            "name": name, 
            "Department": department,
            "Citations_All": "N/A", "Citations_Since_2021": "N/A",
            "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
            "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
        }
        
        profile_url = get_profile_url_with_apify(name)
        if profile_url:
            metrics = scrape_metrics_with_apify(profile_url, name)
            if metrics:
                record.update(metrics)
                success_count += 1
        
        # Check if already exists in DB to update or append
        updated = False
        for i, existing in enumerate(results):
            if existing.get('name') == name:
                results[i] = record
                updated = True
                break
        
        if not updated:
            results.append(record)
            
        save_results(results)
        crawl_progress['current'] += 1

    crawl_progress['status'] = 'idle'
    print(f"Crawl finished. Found {success_count}/{len(staff_list)} profiles.")

@app.route('/')
def index():
    results = load_results()
    return render_template('index.html', count=len(results))

@app.route('/api/bulk_crawl', methods=['POST'])
def api_bulk_crawl():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
        
    department = request.form.get('department', '').strip()
    if not department:
        return jsonify({'success': False, 'error': 'Department is required'})
        
    if file:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        staff_list = []
        try:
            if ext == 'json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        staff_list = data
            elif ext == 'csv':
                df = pd.read_csv(filepath)
                # Assume a 'name' column exists
                for _, row in df.iterrows():
                    name_col = next((c for c in df.columns if c.lower() == 'name'), None)
                    if name_col:
                        staff_list.append({"name": str(row[name_col])})
            elif ext in ['xls', 'xlsx']:
                df = pd.read_excel(filepath)
                for _, row in df.iterrows():
                    name_col = next((c for c in df.columns if c.lower() == 'name'), None)
                    if name_col:
                        staff_list.append({"name": str(row[name_col])})
            else:
                return jsonify({'success': False, 'error': 'Invalid file format'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': f"Error parsing file: {e}"})
            
        if not staff_list:
            return jsonify({'success': False, 'error': 'No names found in document. Ensure there is a "name" column/key.'})
            
        # Add the department to all staff
        for p in staff_list:
            p['department'] = department
            
        # Start crawl worker in a thread
        if crawl_progress['status'] == 'running':
            return jsonify({'success': False, 'error': 'A crawl is already running'})
            
        thread = threading.Thread(target=crawl_worker, args=(staff_list,))
        thread.daemon = True
        thread.start()
        
        # Wait for thread to finish since we want to return the result synchronously in this app model
        thread.join()
        
        results = load_results()
        
        return jsonify({
            'success': True,
            'total': len(staff_list)
        })

@app.route('/api/crawl_progress', methods=['GET'])
def api_crawl_progress():
    return jsonify(crawl_progress)

@app.route('/api/results', methods=['GET'])
def api_results():
    return jsonify(load_results())

@app.route('/api/clear', methods=['POST'])
def api_clear():
    save_results([])
    return jsonify({'success': True})

@app.route('/api/download/csv')
def download_csv():
    results = load_results()
    if not results:
        return jsonify({'error': 'No results to download'}), 400
        
    df = pd.DataFrame(results)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    output_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    output_bytes.seek(0)
    
    filename = f'bulk_scholar_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return send_file(output_bytes, mimetype='text/csv', as_attachment=True, download_name=filename)

@app.route('/api/download/excel')
def download_excel():
    results = load_results()
    if not results:
        return jsonify({'error': 'No results to download'}), 400
        
    df = pd.DataFrame(results)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Scholar Metrics')
    output.seek(0)
    
    filename = f'bulk_scholar_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
