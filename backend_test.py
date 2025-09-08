import requests
import sys
import json
from datetime import datetime

class ESGAPITester:
    def __init__(self, base_url="https://impact-data.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_org_id = None
        self.test_assessment_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) > 0:
                        print(f"   Response keys: {list(response_data.keys())}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: Non-JSON content (length: {len(response.content)})")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")

            return success, response.json() if success and response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_initialize_comprehensive_data(self):
        """Test comprehensive data initialization"""
        return self.run_test(
            "Initialize Comprehensive Data",
            "POST",
            "initialize-comprehensive-data",
            200
        )

    def test_get_organizations(self):
        """Test getting organizations"""
        success, response = self.run_test("Get Organizations", "GET", "organizations", 200)
        if success and response and len(response) > 0:
            self.test_org_id = response[0]['id']
            print(f"   Found {len(response)} organizations, using: {response[0]['name']}")
        return success, response

    def test_create_organization(self):
        """Test creating a new organization"""
        org_data = {
            "name": "Test ESG Corp",
            "industry": "Technology",
            "size": "Large",
            "country": "United States",
            "headquarters": "San Francisco, CA",
            "website": "https://test-esg.com",
            "employee_count": 1500,
            "annual_revenue": "$100M - $500M",
            "stock_symbol": "TESG"
        }
        success, response = self.run_test(
            "Create Organization",
            "POST",
            "organizations",
            200,
            data=org_data
        )
        if success and response:
            self.test_org_id = response['id']
            print(f"   Created organization with ID: {self.test_org_id}")
        return success, response

    def test_get_questions(self):
        """Test getting questions"""
        success, response = self.run_test("Get Questions", "GET", "questions", 200)
        if success and response:
            print(f"   Found {len(response)} questions")
            # Check question structure
            if len(response) > 0:
                sample_q = response[0]
                print(f"   Sample question: {sample_q.get('question_text', 'N/A')[:50]}...")
                print(f"   ESG categories found: {set(q.get('esg_category') for q in response)}")
                print(f"   Canvas sections found: {set(q.get('canvas_section') for q in response)}")
        return success, response

    def test_create_assessment(self):
        """Test creating an assessment"""
        if not self.test_org_id:
            print("❌ Skipping assessment creation - no organization ID")
            return False, {}
        
        assessment_data = {
            "organization_id": self.test_org_id,
            "name": "Test ESG Assessment",
            "description": "Comprehensive ESG assessment for testing"
        }
        success, response = self.run_test(
            "Create Assessment",
            "POST",
            "assessments",
            200,
            data=assessment_data
        )
        if success and response:
            self.test_assessment_id = response['id']
            print(f"   Created assessment with ID: {self.test_assessment_id}")
        return success, response

    def test_create_answer(self):
        """Test creating an answer"""
        if not self.test_org_id:
            print("❌ Skipping answer creation - no organization ID")
            return False, {}
        
        # Get a question first
        success, questions = self.run_test("Get Questions for Answer", "GET", "questions", 200)
        if not success or not questions:
            print("❌ Cannot create answer - no questions available")
            return False, {}
        
        question = questions[0]
        answer_data = {
            "question_id": question['id'],
            "organization_id": self.test_org_id,
            "answer_value": "Test answer for comprehensive testing",
            "comments": "This is a test answer"
        }
        
        return self.run_test(
            "Create Answer",
            "POST",
            "answers",
            200,
            data=answer_data
        )

    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        if not self.test_org_id:
            print("❌ Skipping dashboard test - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Dashboard Data",
            "GET",
            f"reports/dashboard/{self.test_org_id}",
            200
        )

    def test_benchmarking_data(self):
        """Test benchmarking data endpoint"""
        if not self.test_org_id:
            print("❌ Skipping benchmarking test - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Benchmarking Data",
            "GET",
            f"reports/benchmarking/{self.test_org_id}",
            200
        )

    def test_assessment_progress(self):
        """Test assessment progress endpoint"""
        if not self.test_assessment_id:
            print("❌ Skipping progress test - no assessment ID")
            return False, {}
        
        return self.run_test(
            "Get Assessment Progress",
            "GET",
            f"assessments/{self.test_assessment_id}/progress",
            200
        )

    def test_html_comprehensive_report(self):
        """Test comprehensive HTML report generation"""
        if not self.test_org_id:
            print("❌ Skipping HTML report test - no organization ID")
            return False, {}
        
        success, response = self.run_test(
            "Generate Comprehensive HTML Report",
            "GET",
            f"reports/html/{self.test_org_id}/comprehensive",
            200
        )
        
        # For HTML response, check if it contains expected HTML elements
        if success:
            try:
                # Make the actual request to check HTML content
                url = f"{self.api_url}/reports/html/{self.test_org_id}/comprehensive"
                html_response = requests.get(url)
                if html_response.status_code == 200:
                    html_content = html_response.text
                    if "ESG Sustainability Report" in html_content and "<!DOCTYPE html>" in html_content:
                        print("   ✅ HTML report contains expected content")
                        print(f"   HTML length: {len(html_content)} characters")
                    else:
                        print("   ⚠️ HTML report may be missing expected content")
                        print(f"   Content preview: {html_content[:200]}...")
            except Exception as e:
                print(f"   ⚠️ Could not verify HTML content: {e}")
        
        return success, response

    def test_html_executive_report(self):
        """Test executive summary HTML report generation"""
        if not self.test_org_id:
            print("❌ Skipping executive report test - no organization ID")
            return False, {}
        
        success, response = self.run_test(
            "Generate Executive Summary HTML Report",
            "GET",
            f"reports/html/{self.test_org_id}/executive",
            200
        )
        
        # For HTML response, check if it contains expected HTML elements
        if success:
            try:
                # Make the actual request to check HTML content
                url = f"{self.api_url}/reports/html/{self.test_org_id}/executive"
                html_response = requests.get(url)
                if html_response.status_code == 200:
                    html_content = html_response.text
                    if "ESG Executive Summary" in html_content and "<!DOCTYPE html>" in html_content:
                        print("   ✅ Executive HTML report contains expected content")
                        print(f"   HTML length: {len(html_content)} characters")
                    else:
                        print("   ⚠️ Executive HTML report may be missing expected content")
                        print(f"   Content preview: {html_content[:200]}...")
            except Exception as e:
                print(f"   ⚠️ Could not verify HTML content: {e}")
        
        return success, response

def main():
    print("🚀 Starting Comprehensive ESG API Testing")
    print("=" * 60)
    
    tester = ESGAPITester()
    
    # Test sequence
    test_results = []
    
    # Basic API tests
    test_results.append(tester.test_root_endpoint())
    test_results.append(tester.test_initialize_comprehensive_data())
    test_results.append(tester.test_get_organizations())
    
    # If no organizations exist, create one
    if not tester.test_org_id:
        test_results.append(tester.test_create_organization())
    
    # Core functionality tests
    test_results.append(tester.test_get_questions())
    test_results.append(tester.test_create_assessment())
    test_results.append(tester.test_create_answer())
    
    # Analytics and reporting tests
    test_results.append(tester.test_dashboard_data())
    test_results.append(tester.test_benchmarking_data())
    test_results.append(tester.test_assessment_progress())
    
    # HTML report generation tests
    test_results.append(tester.test_html_comprehensive_report())
    test_results.append(tester.test_html_executive_report())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL TESTS PASSED! Backend API is fully functional.")
        return 0
    else:
        print(f"\n⚠️ {tester.tests_run - tester.tests_passed} tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())