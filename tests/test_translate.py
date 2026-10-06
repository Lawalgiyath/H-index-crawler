import requests

url = "https://scholar-google-com.translate.goog/citations?user=I02xXeUAAAAJ&hl=en&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US"
try:
    resp = requests.get(url, timeout=15)
    print("Status:", resp.status_code)
    if "Luqman" in resp.text:
        print("Success! Found name")
except Exception as e:
    print("Error:", e)
