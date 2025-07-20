#!/usr/bin/env python3
"""
API Migration Test Script
========================

This script tests the API endpoints after the database migration
to ensure all responses use English field names correctly.

Usage: python test_api_migration.py
"""

import requests
import json
import sys
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIMigrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ Health endpoint working")
            logger.info(f"   Response: {data}")
            
            # Verify English field names
            expected_fields = {"status", "timestamp"}
            actual_fields = set(data.keys())
            
            if expected_fields.issubset(actual_fields):
                logger.info("✅ Health endpoint uses English field names")
                return True
            else:
                logger.error(f"❌ Health endpoint missing fields: {expected_fields - actual_fields}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Health endpoint failed: {e}")
            return False
    
    def test_latest_ui_endpoint(self):
        """Test latest UI endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/ui/latest")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ Latest UI endpoint working")
            
            # Verify structure
            if data.get("success") and data.get("data"):
                ui_data = data["data"]
                expected_fields = {"date", "value"}
                actual_fields = set(ui_data.keys())
                
                if expected_fields.issubset(actual_fields):
                    logger.info("✅ Latest UI uses English field names")
                    logger.info(f"   Sample data: date={ui_data['date']}, value={ui_data['value']}")
                    return True
                else:
                    logger.error(f"❌ Latest UI missing fields: {expected_fields - actual_fields}")
                    return False
            else:
                logger.error(f"❌ Latest UI unexpected response structure: {data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Latest UI endpoint failed: {e}")
            return False
    
    def test_ui_by_date_endpoint(self):
        """Test UI by date endpoint"""
        try:
            test_date = "2024-01-15"  # Use a recent date
            response = self.session.get(f"{self.base_url}/api/ui/{test_date}")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ UI by date endpoint working")
            
            # Verify structure
            if data.get("success") and data.get("data"):
                ui_data = data["data"]
                expected_fields = {"date", "value"}
                actual_fields = set(ui_data.keys())
                
                if expected_fields.issubset(actual_fields):
                    logger.info("✅ UI by date uses English field names")
                    logger.info(f"   Sample data: date={ui_data['date']}, value={ui_data['value']}")
                    return True
                else:
                    logger.error(f"❌ UI by date missing fields: {expected_fields - actual_fields}")
                    return False
            else:
                logger.info(f"ℹ️ UI by date no data for {test_date} (normal if date doesn't exist)")
                return True
                
        except requests.RequestException as e:
            logger.error(f"❌ UI by date endpoint failed: {e}")
            return False
    
    def test_latest_ur_endpoint(self):
        """Test latest UR endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/ur/latest")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ Latest UR endpoint working")
            
            # Verify structure
            if data.get("success") and data.get("data"):
                ur_data = data["data"]
                expected_fields = {"year", "month", "value"}
                actual_fields = set(ur_data.keys())
                
                if expected_fields.issubset(actual_fields):
                    logger.info("✅ Latest UR uses English field names")
                    logger.info(f"   Sample data: year={ur_data['year']}, month={ur_data['month']}, value={ur_data['value']}")
                    return True
                else:
                    logger.error(f"❌ Latest UR missing fields: {expected_fields - actual_fields}")
                    return False
            else:
                logger.error(f"❌ Latest UR unexpected response structure: {data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Latest UR endpoint failed: {e}")
            return False
    
    def test_ur_by_year_month_endpoint(self):
        """Test UR by year/month endpoint"""
        try:
            test_year = 2023
            test_month = 12
            response = self.session.get(f"{self.base_url}/api/ur/year-month/{test_year}/{test_month}")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ UR by year/month endpoint working")
            
            # Verify structure
            if data.get("success") and data.get("data"):
                ur_data = data["data"]
                expected_fields = {"year", "month", "value"}
                actual_fields = set(ur_data.keys())
                
                if expected_fields.issubset(actual_fields):
                    logger.info("✅ UR by year/month uses English field names")
                    logger.info(f"   Sample data: year={ur_data['year']}, month={ur_data['month']}, value={ur_data['value']}")
                    return True
                else:
                    logger.error(f"❌ UR by year/month missing fields: {expected_fields - actual_fields}")
                    return False
            else:
                logger.info(f"ℹ️ UR by year/month no data for {test_year}-{test_month} (normal if date doesn't exist)")
                return True
                
        except requests.RequestException as e:
            logger.error(f"❌ UR by year/month endpoint failed: {e}")
            return False
    
    def test_info_endpoint(self):
        """Test info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            response.raise_for_status()
            
            data = response.json()
            logger.info("✅ Info endpoint working")
            
            # Verify structure - info endpoint returns data directly, not wrapped in success/data
            if "total_records" in data and "date_range" in data:
                expected_fields = {"total_records", "date_range", "latest_ui", "data_source"}
                actual_fields = set(data.keys())
                
                if expected_fields.issubset(actual_fields):
                    logger.info("✅ Info endpoint uses English field names")
                    logger.info(f"   Total records: {data['total_records']}")
                    logger.info(f"   Date range: {data['date_range']}")
                    return True
                else:
                    logger.error(f"❌ Info endpoint missing fields: {expected_fields - actual_fields}")
                    return False
            else:
                logger.error(f"❌ Info endpoint unexpected response structure: {data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Info endpoint failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("🚀 Starting API migration tests...")
        
        tests = [
            ("Health", self.test_health_endpoint),
            ("Latest UI", self.test_latest_ui_endpoint),
            ("UI by Date", self.test_ui_by_date_endpoint),
            ("Latest UR", self.test_latest_ur_endpoint),
            ("UR by Year/Month", self.test_ur_by_year_month_endpoint),
            ("Info", self.test_info_endpoint),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Testing {test_name}...")
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name} test passed")
                else:
                    logger.error(f"❌ {test_name} test failed")
            except Exception as e:
                logger.error(f"❌ {test_name} test error: {e}")
        
        logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All API migration tests passed!")
            logger.info("✅ API is using English field names correctly")
            return True
        else:
            logger.error(f"❌ {total - passed} tests failed")
            logger.error("❌ API migration validation failed")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test API after database migration')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL for API')
    parser.add_argument('--start-server', action='store_true', help='Start server before testing')
    
    args = parser.parse_args()
    
    if args.start_server:
        logger.info("🚀 Starting server...")
        import subprocess
        import time
        
        # Start server in background
        server_process = subprocess.Popen([
            'python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'
        ])
        
        # Wait for server to start
        time.sleep(3)
        
        try:
            tester = APIMigrationTester(args.url)
            success = tester.run_all_tests()
        finally:
            # Stop server
            server_process.terminate()
            server_process.wait()
        
        sys.exit(0 if success else 1)
    else:
        tester = APIMigrationTester(args.url)
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 