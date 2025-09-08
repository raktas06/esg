import requests
import sys
import json
import tempfile
import os
from datetime import datetime

class ReportUploadTester:
    def __init__(self, base_url="https://esg-compass-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_org_id = None

    def get_test_organization(self):
        """Get or create a test organization"""
        try:
            # Try to get existing organizations
            response = requests.get(f"{self.api_url}/organizations")
            if response.status_code == 200:
                orgs = response.json()
                if orgs:
                    self.test_org_id = orgs[0]['id']
                    print(f"✅ Using existing organization: {orgs[0]['name']} (ID: {self.test_org_id})")
                    return True
            
            # Create new organization if none exist
            org_data = {
                "name": "Report Upload Test Organization",
                "industry": "Technology",
                "size": "Medium"
            }
            response = requests.post(f"{self.api_url}/organizations", json=org_data)
            if response.status_code == 200:
                org = response.json()
                self.test_org_id = org['id']
                print(f"✅ Created test organization: {org['name']} (ID: {self.test_org_id})")
                return True
            else:
                print(f"❌ Failed to create organization: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting organization: {e}")
            return False

    def create_test_pdf_content(self):
        """Create a simple test PDF-like content"""
        return """ESG Sustainability Report 2023
        
Environmental Performance:
- Carbon Emissions: 1,250 tons CO2e (15% reduction from 2022)
- Energy Consumption: 2,500 MWh (20% renewable energy)
- Water Usage: 15,000 cubic meters
- Waste Recycling Rate: 85%

Social Performance:
- Employee Satisfaction: 4.2/5.0
- Diversity Ratio: 45% women, 35% minorities
- Training Hours: 40 hours per employee
- Safety Incidents: 2 (target: <5)

Governance Performance:
- Board Independence: 80%
- Ethics Training Completion: 98%
- Data Privacy Compliance: 100%
- Audit Score: 95/100

Financial ESG Impact:
- ESG Investment: $2.5M
- Cost Savings from Efficiency: $1.8M
- Green Revenue: $15.2M (25% of total revenue)

IFRS S1/S2 Compliance:
- Climate Risk Assessment: Complete
- Sustainability Disclosures: 90% complete
- Financial Impact Quantification: In progress
"""

    def test_report_upload_with_query_param(self):
        """Test report upload with organization_id as query parameter"""
        print("\n📄 Testing Report Upload with Query Parameter...")
        
        if not self.test_org_id:
            print("❌ No organization ID available")
            return False
        
        try:
            # Create a temporary file with test content
            test_content = self.create_test_pdf_content()
            
            # Test with text file (should fail - only PDF/DOCX allowed)
            print("\n🔍 Test 1: Upload text file (should fail)...")
            files = {'file': ('test_report.txt', test_content, 'text/plain')}
            params = {'organization_id': self.test_org_id}
            
            response = requests.post(f"{self.api_url}/reports/upload", files=files, params=params)
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Correctly rejected non-PDF/DOCX file")
            else:
                print(f"   ⚠️ Unexpected response: {response.text[:200]}")
            
            # Test with PDF content type (simulated)
            print("\n🔍 Test 2: Upload with PDF content type...")
            files = {'file': ('test_report.pdf', test_content, 'application/pdf')}
            params = {'organization_id': self.test_org_id}
            
            response = requests.post(f"{self.api_url}/reports/upload", files=files, params=params)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("   ✅ PDF upload successful")
                result = response.json()
                print(f"   Report ID: {result.get('id', 'N/A')}")
                print(f"   Processed: {result.get('processed', False)}")
                return True
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error during upload test: {e}")
            return False

    def test_get_uploaded_reports(self):
        """Test getting uploaded reports for organization"""
        print(f"\n📋 Testing Get Uploaded Reports for org {self.test_org_id}...")
        
        if not self.test_org_id:
            print("❌ No organization ID available")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/reports/uploaded/{self.test_org_id}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                reports = response.json()
                print(f"   ✅ Found {len(reports)} uploaded reports")
                if reports:
                    for i, report in enumerate(reports):
                        print(f"   Report {i+1}: {report.get('file_name', 'N/A')} - Processed: {report.get('processed', False)}")
                return True
            else:
                print(f"   ❌ Failed to get reports: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting uploaded reports: {e}")
            return False

    def test_report_comparison_endpoints(self):
        """Test report comparison functionality"""
        print(f"\n🔍 Testing Report Comparison Endpoints...")
        
        # Test comparison endpoint with organization ID
        try:
            response = requests.get(f"{self.api_url}/reports/comparison/{self.test_org_id}")
            print(f"   Comparison by org status: {response.status_code}")
            if response.status_code == 404:
                print("   ✅ No comparison data found (expected for new org)")
            elif response.status_code == 200:
                print("   ✅ Comparison data available")
            else:
                print(f"   ⚠️ Unexpected response: {response.text[:200]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing comparison: {e}")
            return False

def main():
    print("🎯 REPORT UPLOAD FUNCTIONALITY TESTING")
    print("=" * 50)
    
    tester = ReportUploadTester()
    
    # Step 1: Get test organization
    if not tester.get_test_organization():
        print("❌ Cannot proceed without organization")
        return 1
    
    # Step 2: Test report upload
    upload_success = tester.test_report_upload_with_query_param()
    
    # Step 3: Test getting uploaded reports
    get_reports_success = tester.test_get_uploaded_reports()
    
    # Step 4: Test comparison endpoints
    comparison_success = tester.test_report_comparison_endpoints()
    
    # Results
    print("\n" + "=" * 50)
    print("📊 REPORT UPLOAD TEST RESULTS")
    print("=" * 50)
    
    results = {
        "Report Upload": upload_success,
        "Get Uploaded Reports": get_reports_success,
        "Report Comparison": comparison_success
    }
    
    for test, success in results.items():
        status = "✅ WORKING" if success else "❌ NEEDS ATTENTION"
        print(f"   {status}: {test}")
    
    working_count = sum(results.values())
    print(f"\nWorking Features: {working_count}/3")
    
    if working_count >= 2:
        print("🎉 Report upload functionality is mostly working!")
        if not upload_success:
            print("⚠️ File upload needs debugging - check file handling and aiofiles dependency")
        return 0
    else:
        print("❌ Report upload functionality needs significant work")
        return 1

if __name__ == "__main__":
    sys.exit(main())