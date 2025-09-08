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
        url = f"{self.base_url}/{endpoint}"
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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_initialize_sample_data(self):
        """Test initializing sample data"""
        return self.run_test("Initialize Sample Data", "POST", "initialize-sample-data", 200)

    def test_get_organizations(self):
        """Test getting organizations"""
        success, data = self.run_test("Get Organizations", "GET", "organizations", 200)
        if success and isinstance(data, list) and len(data) > 0:
            self.created_org_id = data[0]['id']
            print(f"   Found organization: {data[0]['name']} (ID: {self.created_org_id})")
        return success, data

    def test_create_organization(self):
        """Test creating a new organization"""
        org_data = {
            "name": "Green Tech Solutions",
            "industry": "Technology", 
            "size": "Medium",
            "country": "United States"
        }
        success, data = self.run_test("Create Organization", "POST", "organizations", 200, org_data)
        if success and 'id' in data:
            self.created_org_id = data['id']
            print(f"   Created organization ID: {self.created_org_id}")
        return success, data

    def test_get_organization_by_id(self):
        """Test getting a specific organization"""
        if not self.created_org_id:
            print("❌ Skipped - No organization ID available")
            return False, {}
        return self.run_test("Get Organization by ID", "GET", f"organizations/{self.created_org_id}", 200)

    def test_get_questions(self):
        """Test getting all questions"""
        return self.run_test("Get All Questions", "GET", "questions", 200)

    def test_get_questions_with_filters(self):
        """Test getting questions with filters"""
        # Test by ESG category
        success1, _ = self.run_test("Get Environmental Questions", "GET", "questions", 200, 
                                   params={"esg_category": "environmental"})
        
        # Test by canvas section
        success2, _ = self.run_test("Get Key Partnerships Questions", "GET", "questions", 200,
                                   params={"canvas_section": "key_partnerships"})
        
        # Test by standard
        success3, _ = self.run_test("Get GRI Questions", "GET", "questions", 200,
                                   params={"standard": "GRI"})
        
        return success1 and success2 and success3, {}

    def test_get_questions_by_canvas_section(self):
        """Test getting questions by canvas section endpoint"""
        return self.run_test("Get Questions by Canvas Section", "GET", 
                           "questions/canvas-section/key_partnerships", 200)

    def test_create_question(self):
        """Test creating a new question"""
        question_data = {
            "question_text": "Test question for ESG assessment",
            "description": "This is a test question for API testing",
            "question_type": "text",
            "esg_category": "environmental",
            "canvas_section": "key_activities",
            "standard": "GRI",
            "reference_code": "TEST-001",
            "is_required": True
        }
        success, data = self.run_test("Create Question", "POST", "questions", 200, question_data)
        if success and 'id' in data:
            self.created_question_ids.append(data['id'])
            print(f"   Created question ID: {data['id']}")
        return success, data

    def test_create_assessment(self):
        """Test creating an assessment"""
        if not self.created_org_id:
            print("❌ Skipped - No organization ID available")
            return False, {}
            
        assessment_data = {
            "organization_id": self.created_org_id,
            "name": "Test ESG Assessment",
            "description": "Test assessment for API testing"
        }
        success, data = self.run_test("Create Assessment", "POST", "assessments", 200, assessment_data)
        if success and 'id' in data:
            self.created_assessment_id = data['id']
            print(f"   Created assessment ID: {self.created_assessment_id}")
        return success, data

    def test_get_assessments(self):
        """Test getting assessments"""
        success1, _ = self.run_test("Get All Assessments", "GET", "assessments", 200)
        
        if self.created_org_id:
            success2, _ = self.run_test("Get Assessments by Organization", "GET", "assessments", 200,
                                       params={"organization_id": self.created_org_id})
            return success1 and success2, {}
        return success1, {}

    def test_get_assessment_by_id(self):
        """Test getting a specific assessment"""
        if not self.created_assessment_id:
            print("❌ Skipped - No assessment ID available")
            return False, {}
        return self.run_test("Get Assessment by ID", "GET", f"assessments/{self.created_assessment_id}", 200)

    def test_create_answer(self):
        """Test creating/updating answers"""
        if not self.created_org_id or not self.created_question_ids:
            print("❌ Skipped - No organization or question ID available")
            return False, {}
            
        answer_data = {
            "question_id": self.created_question_ids[0],
            "organization_id": self.created_org_id,
            "answer_value": "This is a test answer for the ESG question",
            "comments": "Test comment"
        }
        return self.run_test("Create Answer", "POST", "answers", 200, answer_data)

    def test_get_answers(self):
        """Test getting answers"""
        success1, _ = self.run_test("Get All Answers", "GET", "answers", 200)
        
        if self.created_org_id:
            success2, _ = self.run_test("Get Answers by Organization", "GET", "answers", 200,
                                       params={"organization_id": self.created_org_id})
            return success1 and success2, {}
        return success1, {}

    def test_assessment_progress(self):
        """Test getting assessment progress"""
        if not self.created_assessment_id:
            print("❌ Skipped - No assessment ID available")
            return False, {}
        return self.run_test("Get Assessment Progress", "GET", 
                           f"assessments/{self.created_assessment_id}/progress", 200)

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting ESG API Testing...")
        print(f"Testing against: {self.base_url}")
        
        # Test sequence
        tests = [
            self.test_root_endpoint,
            self.test_initialize_sample_data,
            self.test_get_organizations,
            self.test_create_organization,
            self.test_get_organization_by_id,
            self.test_get_questions,
            self.test_get_questions_with_filters,
            self.test_get_questions_by_canvas_section,
            self.test_create_question,
            self.test_create_assessment,
            self.test_get_assessments,
            self.test_get_assessment_by_id,
            self.test_create_answer,
            self.test_get_answers,
            self.test_assessment_progress
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Print final results
        print(f"\n📊 Test Results:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed!")
            return 1

def main():
    tester = ESGAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())