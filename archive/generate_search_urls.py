"""
GENERATE GOOGLE SCHOLAR SEARCH URLs
====================================
Creates search URLs for each staff member to find their profiles manually
"""
import json
import urllib.parse

def main():
    # Load staff names
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print("GOOGLE SCHOLAR PROFILE SEARCH URLs")
    print("=" * 70)
    print(f"Total staff: {len(staff_list)}\n")
    
    # Already confirmed IDs
    confirmed = {
        "Lawrence Ekebafe": "s9d437QAAAAJ",
        "Wesley Okiei": "tQgb_bgAAAAJ"
    }
    
    search_urls = []
    
    for i, staff in enumerate(staff_list, 1):
        name = staff['name']
        
        if name in confirmed:
            profile_url = f"https://scholar.google.com/citations?user={confirmed[name]}&hl=en"
            print(f"{i}. {name} ✓ CONFIRMED")
            print(f"   {profile_url}\n")
            search_urls.append({
                "name": name,
                "status": "confirmed",
                "user_id": confirmed[name],
                "url": profile_url
            })
        else:
            # Create search URL
            query = f"{name} University of Lagos"
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={encoded_query}&hl=en"
            
            print(f"{i}. {name}")
            print(f"   {search_url}\n")
            search_urls.append({
                "name": name,
                "status": "needs_search",
                "user_id": None,
                "search_url": search_url
            })
    
    # Save to JSON
    with open('scholar_search_urls.json', 'w', encoding='utf-8') as f:
        json.dump(search_urls, f, indent=2, ensure_ascii=False)
    
    # Also create an HTML file for easy clicking
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Find Google Scholar IDs - UNILAG Chemistry</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        h1 { color: #333; }
        .staff-item { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .confirmed { background-color: #d4edda; }
        .needs-search { background-color: #fff3cd; }
        .name { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .link { margin: 5px 0; }
        .link a { color: #0066cc; text-decoration: none; }
        .link a:hover { text-decoration: underline; }
        .user-id { color: #28a745; font-family: monospace; }
        .instructions { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        input[type="text"] { width: 300px; padding: 5px; margin-right: 10px; }
        button { padding: 5px 10px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <h1>Find Google Scholar IDs - UNILAG Chemistry Department</h1>
    
    <div class="instructions">
        <h3>Instructions:</h3>
        <ol>
            <li>Click the search link for each staff member (yellow boxes)</li>
            <li>Find their profile in Google Scholar</li>
            <li>Copy the user ID from the profile URL (e.g., citations?user=<strong>ABC123XYZ</strong>&hl=en)</li>
            <li>Enter it in the input box and click "Save"</li>
            <li>Once all IDs are collected, download the JSON file</li>
        </ol>
        <p><strong>Progress:</strong> <span id="progress">2/27 confirmed</span></p>
        <button onclick="downloadJSON()">Download JSON with IDs</button>
    </div>
    
"""
    
    for i, item in enumerate(search_urls):
        name = item['name']
        status = item['status']
        
        if status == 'confirmed':
            user_id = item['user_id']
            url = item['url']
            html += f"""
    <div class="staff-item confirmed" id="staff-{i}">
        <div class="name">{i+1}. {name} ✓</div>
        <div class="user-id">ID: {user_id}</div>
        <div class="link"><a href="{url}" target="_blank">View Profile</a></div>
    </div>
"""
        else:
            search_url = item['search_url']
            html += f"""
    <div class="staff-item needs-search" id="staff-{i}">
        <div class="name">{i+1}. {name}</div>
        <div class="link"><a href="{search_url}" target="_blank">🔍 Search on Google Scholar</a></div>
        <div style="margin-top: 10px;">
            <input type="text" id="userid-{i}" placeholder="Enter user ID (e.g., ABC123XYZ)" />
            <button onclick="saveUserId({i}, '{name}')">Save ID</button>
        </div>
    </div>
"""
    
    html += """
    <script>
        let staffData = """ + json.dumps(search_urls) + """;
        
        function saveUserId(index, name) {
            const input = document.getElementById('userid-' + index);
            const userId = input.value.trim();
            
            if (!userId) {
                alert('Please enter a user ID');
                return;
            }
            
            // Update data
            staffData[index].user_id = userId;
            staffData[index].status = 'confirmed';
            staffData[index].url = `https://scholar.google.com/citations?user=${userId}&hl=en`;
            delete staffData[index].search_url;
            
            // Update UI
            const item = document.getElementById('staff-' + index);
            item.className = 'staff-item confirmed';
            item.innerHTML = `
                <div class="name">${index+1}. ${name} ✓</div>
                <div class="user-id">ID: ${userId}</div>
                <div class="link"><a href="https://scholar.google.com/citations?user=${userId}&hl=en" target="_blank">View Profile</a></div>
            `;
            
            // Update progress
            const confirmed = staffData.filter(s => s.status === 'confirmed').length;
            document.getElementById('progress').textContent = `${confirmed}/27 confirmed`;
            
            alert('Saved! ID: ' + userId);
        }
        
        function downloadJSON() {
            const confirmed = staffData.filter(s => s.status === 'confirmed').length;
            if (confirmed < 27) {
                if (!confirm(`Only ${confirmed}/27 profiles confirmed. Download anyway?`)) {
                    return;
                }
            }
            
            const dataStr = JSON.stringify(staffData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'scholar_ids_collected.json';
            link.click();
        }
    </script>
</body>
</html>
"""
    
    with open('find_scholar_ids.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("=" * 70)
    print("FILES CREATED:")
    print("=" * 70)
    print("1. scholar_search_urls.json - Raw data")
    print("2. find_scholar_ids.html - Interactive search helper")
    print("\nOpen 'find_scholar_ids.html' in your browser to start searching!")
    print("=" * 70)

if __name__ == "__main__":
    main()
