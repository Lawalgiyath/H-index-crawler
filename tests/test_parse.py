from bs4 import BeautifulSoup
import requests

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    metrics = {
        "Citations_All": "0", "Citations_Since_2021": "0",
        "H_Index_All": "0", "H_Index_Since_2021": "0",
        "I10_Index_All": "0", "I10_Index_Since_2021": "0"
    }
    
    name_elem = soup.select_one("#gsc_prf_in")
    if name_elem: metrics["Exact_Name"] = name_elem.text.strip()
    affil_elem = soup.select_one(".gsc_prf_il")
    if affil_elem: metrics["Exact_Affiliation"] = affil_elem.text.strip()
    
    table_rows = soup.select("#gsc_rsb_st tr")
    for row in table_rows:
        header = row.select_one(".gsc_rsb_sc1")
        values = row.select(".gsc_rsb_std")
        if header and len(values) >= 2:
            t = header.text.strip().lower()
            if "citations" in t:
                metrics["Citations_All"] = values[0].text.strip()
                metrics["Citations_Since_2021"] = values[1].text.strip()
            elif "h-index" in t:
                metrics["H_Index_All"] = values[0].text.strip()
                metrics["H_Index_Since_2021"] = values[1].text.strip()
            elif "i10" in t:
                metrics["I10_Index_All"] = values[0].text.strip()
                metrics["I10_Index_Since_2021"] = values[1].text.strip()
    return metrics

import urllib.request
req = urllib.request.Request("https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en", headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read()
print(parse_html(html))
