import requests
import os
import time

BASE_URL = "https://pubfiles.pagasa.dost.gov.ph/tamss/weather/bulletin/TCB%23{}_wilma.pdf"
OUTPUT_DIR = "dataset"

def download_dataset():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for i in range(1, 23):
        url = BASE_URL.format(i)
        filename = f"TCB_{i}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"Skipping {filename} (exists)")
            continue
            
        print(f"Downloading {filename} from {url}...")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                print(f"Saved {filename}")
            else:
                print(f"Failed to download {filename}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
        
        time.sleep(0.5) # Be nice to the server

if __name__ == "__main__":
    download_dataset()
