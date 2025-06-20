#!/usr/bin/env python3
"""
Simple test script to verify the Furniture API functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_admin_login():
    """Test admin login"""
    print("Testing admin login...")
    response = requests.post(
        f"{API_V1}/admin/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    print("✅ Admin login passed")
    return data["access_token"]

def test_products_list():
    """Test products listing"""
    print("Testing products listing...")
    response = requests.get(f"{API_V1}/products/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 0
    print(f"✅ Products listing passed - Found {data['total']} products")
    return data

def test_categories():
    """Test categories endpoint"""
    print("Testing categories endpoint...")
    response = requests.get(f"{API_V1}/products/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Categories endpoint passed - Found {len(data)} categories")

def test_search():
    """Test search functionality"""
    print("Testing search functionality...")
    response = requests.get(f"{API_V1}/products/search?q=chair")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    print(f"✅ Search functionality passed - Found {data['total']} results for 'chair'")

def test_admin_products(token):
    """Test admin products endpoint"""
    print("Testing admin products endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V1}/admin/products/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    print(f"✅ Admin products endpoint passed - Found {data['total']} products")

def test_upload_history(token):
    """Test upload history endpoint"""
    print("Testing upload history endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V1}/admin/upload-history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    print(f"✅ Upload history endpoint passed - Found {data['total']} uploads")

def main():
    """Run all tests"""
    print("🚀 Starting Furniture API Tests\n")
    
    try:
        # Test public endpoints
        test_health()
        products_data = test_products_list()
        test_categories()
        test_search()
        
        # Test admin endpoints
        token = test_admin_login()
        test_admin_products(token)
        test_upload_history(token)
        
        print(f"\n🎉 All tests passed! The API is working correctly.")
        print(f"📊 Summary:")
        print(f"   - Products in database: {products_data['total']}")
        print(f"   - API Documentation: {BASE_URL}/docs")
        print(f"   - Health Check: {BASE_URL}/health")
        
        return 0
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
