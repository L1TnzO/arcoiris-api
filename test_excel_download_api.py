"""Test the Excel download API endpoint."""

import requests
import json
from datetime import datetime


def test_admin_login():
    """Test admin login and get access token."""
    login_url = "http://localhost:8000/api/v1/admin/login"
    
    # Try to login with default admin credentials
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(login_url, data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None


def test_excel_download(access_token):
    """Test the Excel download endpoint."""
    download_url = "http://localhost:8000/api/v1/admin/download-excel"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test 1: Download active products only
    print("📥 Testing download of active products...")
    response = requests.get(download_url, headers=headers)
    
    if response.status_code == 200:
        filename = f"downloaded_active_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Active products downloaded successfully: {filename}")
        print(f"📊 File size: {len(response.content)} bytes")
    else:
        print(f"❌ Download failed: {response.status_code} - {response.text}")
        return
    
    # Test 2: Download all products (including inactive)
    print("\n📥 Testing download of all products (including inactive)...")
    params = {"include_inactive": True}
    response = requests.get(download_url, headers=headers, params=params)
    
    if response.status_code == 200:
        filename = f"downloaded_all_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ All products downloaded successfully: {filename}")
        print(f"📊 File size: {len(response.content)} bytes")
    else:
        print(f"❌ Download failed: {response.status_code} - {response.text}")
        return
    
    # Test 3: Download with category filter
    print("\n📥 Testing download with category filter...")
    params = {"category": "Sillas"}
    response = requests.get(download_url, headers=headers, params=params)
    
    if response.status_code == 200:
        filename = f"downloaded_category_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Category filtered products downloaded successfully: {filename}")
        print(f"📊 File size: {len(response.content)} bytes")
    else:
        print(f"❌ Download failed: {response.status_code} - {response.text}")


def main():
    """Main test function."""
    print("🧪 Testing Excel Download API Endpoint")
    print("=" * 50)
    
    # First, test login
    print("🔐 Testing admin login...")
    access_token = test_admin_login()
    
    if not access_token:
        print("❌ Cannot proceed without valid access token")
        return
    
    print("✅ Login successful!")
    print(f"🎫 Access token: {access_token[:20]}...")
    
    # Test Excel download
    print("\n" + "=" * 50)
    test_excel_download(access_token)
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    main()
