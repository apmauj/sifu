"""Test script to compare BHU and INE UR data sources"""
import requests
import pandas as pd
import io
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BHU_URL = "https://bhu.com.uy/sites/default/files/2025-10/historico-ur.xls"
INE_URL = "https://www5.ine.gub.uy/documents/Estad%C3%ADsticasecon%C3%B3micas/SERIES%20Y%20OTROS/UR/UR.xls"

def fetch_source(url, name):
    print(f"\n{'='*60}")
    print(f"Testing {name}: {url}")
    print('='*60)
    
    try:
        print(f"Downloading from {name}...")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=30, headers=headers, verify=False)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
        
        # Check if it's HTML
        content_start = response.content[:100]
        if b'<!DOCTYPE' in content_start or b'<html' in content_start:
            print(f"⚠️  {name} returned HTML, not Excel!")
            print(f"Content start: {content_start}")
            return None
        
        print(f"✓ {name} returned binary content (likely Excel)")
        
        # Try to parse as Excel
        print(f"\nParsing Excel from {name}...")
        df = pd.read_excel(io.BytesIO(response.content), engine='xlrd')
        
        print(f"\nShape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 10 rows:")
        print(df.head(10))
        print("\nData types:")
        print(df.dtypes)
        
        return df
        
    except Exception as e:
        print(f"❌ Error with {name}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing UR data sources...")
    
    bhu_data = fetch_source(BHU_URL, "BHU")
    ine_data = fetch_source(INE_URL, "INE")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"BHU: {'✓ Valid' if bhu_data is not None else '❌ Failed'}")
    print(f"INE: {'✓ Valid' if ine_data is not None else '❌ Failed'}")
    
    if ine_data is not None and bhu_data is not None:
        print("\n🔍 Format comparison:")
        print(f"  BHU shape: {bhu_data.shape}")
        print(f"  INE shape: {ine_data.shape}")
        print(f"  Same format: {bhu_data.shape == ine_data.shape}")
