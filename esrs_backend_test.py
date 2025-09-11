import requests
import sys
import json
from datetime import datetime

class ESRSAPITester:
    def __init__(self, base_url="https://esg-compass-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_org_id = None
        self.test_assessment_id = None
        self.failed_tests = []

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
                response = requests.post(url, json=data, headers=headers, params=params)
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
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'url': url,
                    'method': method
                })
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")

            return success, response.json() if success and response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e),
                'url': url,
                'method': method
            })
            return False, {}

    def setup_test_organization(self):
        """Create or get a test organization"""
        print("\n🏢 Setting up test organization...")
        
        # Try to get existing organizations first
        success, orgs = self.run_test("Get Organizations", "GET", "organizations", 200)
        if success and orgs and len(orgs) > 0:
            self.test_org_id = orgs[0]['id']
            print(f"   Using existing organization: {orgs[0]['name']} (ID: {self.test_org_id})")
            return True
        
        # Create a new organization if none exist
        org_data = {
            "name": "ESRS Test Şirketi",
            "industry": "Teknoloji",
            "size": "Büyük",
            "country": "Türkiye",
            "headquarters": "İstanbul",
            "website": "https://esrs-test.com",
            "employee_count": 1000,
            "annual_revenue": "€50M - €100M"
        }
        success, response = self.run_test(
            "Create Test Organization",
            "POST",
            "organizations",
            200,
            data=org_data
        )
        if success and response:
            self.test_org_id = response['id']
            print(f"   Created test organization with ID: {self.test_org_id}")
            return True
        
        print("❌ Failed to setup test organization")
        return False

    def test_esrs_load_questions(self):
        """Test ESRS questions loading from Excel file"""
        print("\n📊 Testing ESRS Questions Loading...")
        success, response = self.run_test(
            "ESRS Load Questions from Excel",
            "POST",
            "esrs/load-questions",
            200
        )
        
        if success and response:
            print(f"   ✅ Questions loaded: {response.get('questions_loaded', 0)}")
            print(f"   ✅ Answer options loaded: {response.get('answer_options_loaded', 0)}")
            print(f"   ✅ Total data points: {response.get('total_data_points', 0)}")
            
            # Validate expected numbers
            questions_loaded = response.get('questions_loaded', 0)
            answer_options = response.get('answer_options_loaded', 0)
            
            if questions_loaded >= 140:  # Should be around 146
                print(f"   ✅ Question count validation passed: {questions_loaded} questions")
            else:
                print(f"   ⚠️  Question count lower than expected: {questions_loaded} (expected ~146)")
            
            if answer_options >= 700:  # Should be around 730
                print(f"   ✅ Answer options validation passed: {answer_options} options")
            else:
                print(f"   ⚠️  Answer options count lower than expected: {answer_options} (expected ~730)")
        
        return success, response

    def test_esrs_start_assessment(self):
        """Test ESRS assessment start"""
        if not self.test_org_id:
            print("❌ Skipping ESRS assessment start - no organization ID")
            return False, {}
        
        print(f"\n🚀 Testing ESRS Assessment Start for org: {self.test_org_id}...")
        success, response = self.run_test(
            "ESRS Start Assessment",
            "POST",
            "esrs/start-assessment",
            200,
            params={"organization_id": self.test_org_id}
        )
        
        if success and response:
            self.test_assessment_id = response.get('assessment_id')
            print(f"   ✅ Assessment started with ID: {self.test_assessment_id}")
            print(f"   ✅ Total questions: {response.get('total_questions', 0)}")
            print(f"   ✅ Assessment name: {response.get('assessment_name', 'N/A')}")
            
            # Validate assessment data
            total_questions = response.get('total_questions', 0)
            if total_questions >= 140:
                print(f"   ✅ Assessment question count validation passed: {total_questions}")
            else:
                print(f"   ⚠️  Assessment question count lower than expected: {total_questions}")
        
        return success, response

    def test_esrs_get_questions(self):
        """Test ESRS questions retrieval"""
        if not self.test_org_id:
            print("❌ Skipping ESRS questions retrieval - no organization ID")
            return False, {}
        
        print(f"\n📋 Testing ESRS Questions Retrieval for org: {self.test_org_id}...")
        success, response = self.run_test(
            "ESRS Get Questions",
            "GET",
            f"esrs/questions/{self.test_org_id}",
            200,
            params={"limit": 10, "offset": 0}
        )
        
        if success and response:
            questions = response.get('questions', [])
            print(f"   ✅ Retrieved {len(questions)} questions")
            print(f"   ✅ Total available: {response.get('total_questions', 0)}")
            print(f"   ✅ Has more: {response.get('has_more', False)}")
            
            # Validate question structure
            if questions and len(questions) > 0:
                sample_q = questions[0]
                print(f"   ✅ Sample question ID: {sample_q.get('id', 'N/A')}")
                print(f"   ✅ Sample DP ID: {sample_q.get('dp_id', 'N/A')}")
                print(f"   ✅ Sample ESRS standard: {sample_q.get('esrs_standard', 'N/A')}")
                print(f"   ✅ Sample question text: {sample_q.get('question_text', 'N/A')[:50]}...")
                
                # Check answer options
                answer_options = sample_q.get('answer_options', [])
                print(f"   ✅ Sample question has {len(answer_options)} answer options")
                
                if len(answer_options) > 0:
                    option_text = answer_options[0].get('option_text', 'N/A') or 'N/A'
                    print(f"   ✅ Sample answer option: {option_text[:30]}...")
        
        return success, response

    def test_esrs_submit_answer(self):
        """Test ESRS answer submission"""
        if not self.test_org_id or not self.test_assessment_id:
            print("❌ Skipping ESRS answer submission - missing org ID or assessment ID")
            return False, {}
        
        # First get a question to answer
        success, questions_response = self.run_test(
            "Get ESRS Question for Answer",
            "GET",
            f"esrs/questions/{self.test_org_id}",
            200,
            params={"limit": 1}
        )
        
        if not success or not questions_response.get('questions'):
            print("❌ Cannot submit answer - no questions available")
            return False, {}
        
        question = questions_response['questions'][0]
        answer_options = question.get('answer_options', [])
        
        if not answer_options:
            print("❌ Cannot submit answer - no answer options available")
            return False, {}
        
        print(f"\n✍️  Testing ESRS Answer Submission...")
        answer_data = {
            "assessment_id": self.test_assessment_id,
            "question_id": question['id'],
            "organization_id": self.test_org_id,
            "selected_option_id": answer_options[0]['id'],
            "comments": "Test cevabı - ESRS değerlendirmesi"
        }
        
        success, response = self.run_test(
            "ESRS Submit Answer",
            "POST",
            "esrs/submit-answer",
            200,
            data=answer_data
        )
        
        if success and response:
            print(f"   ✅ Answer submitted successfully")
            print(f"   ✅ Response ID: {response.get('response_id', 'N/A')}")
            print(f"   ✅ Score calculated: {response.get('score_calculated', False)}")
            print(f"   ✅ Assessment updated: {response.get('assessment_updated', False)}")
        
        return success, response

    def test_esrs_assessment_results(self):
        """Test ESRS assessment results retrieval"""
        if not self.test_org_id:
            print("❌ Skipping ESRS assessment results - no organization ID")
            return False, {}
        
        print(f"\n📊 Testing ESRS Assessment Results for org: {self.test_org_id}...")
        success, response = self.run_test(
            "ESRS Assessment Results",
            "GET",
            f"esrs/assessment-results/{self.test_org_id}",
            200
        )
        
        if success and response:
            print(f"   ✅ Overall score: {response.get('overall_score', 0)}%")
            print(f"   ✅ Maturity level: {response.get('maturity_level', 'N/A')}")
            print(f"   ✅ Answered questions: {response.get('answered_questions', 0)}")
            print(f"   ✅ Total questions: {response.get('total_questions', 0)}")
            print(f"   ✅ Completion: {response.get('completion_percentage', 0)}%")
            
            recommendations = response.get('recommendations', [])
            print(f"   ✅ Recommendations count: {len(recommendations)}")
            
            if recommendations:
                print(f"   ✅ Sample recommendation: {recommendations[0][:50]}...")
        
        return success, response

    def test_database_collections(self):
        """Test database collections by checking data existence"""
        print(f"\n🗄️  Testing Database Collections...")
        
        # Test esrs_questions collection by getting questions
        success1, _ = self.run_test(
            "Check ESRS Questions Collection",
            "GET",
            f"esrs/questions/{self.test_org_id or 'test'}",
            200,
            params={"limit": 1}
        )
        
        # Test esrs_assessments collection by trying to get results
        success2, _ = self.run_test(
            "Check ESRS Assessments Collection",
            "GET",
            f"esrs/assessment-results/{self.test_org_id or 'test'}",
            200
        )
        
        print(f"   {'✅' if success1 else '❌'} esrs_questions collection accessible")
        print(f"   {'✅' if success2 else '❌'} esrs_assessments collection accessible")
        
        return success1 and success2, {}

    def run_comprehensive_esrs_tests(self):
        """Run all ESRS-specific tests"""
        print("🚀 Starting Comprehensive ESRS Backend API Testing...")
        print(f"   Base URL: {self.base_url}")
        print(f"   API URL: {self.api_url}")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_organization():
            print("❌ Cannot proceed without test organization")
            return
        
        # Core ESRS Tests
        print("\n" + "=" * 60)
        print("🎯 PRIORITY ESRS TESTS")
        print("=" * 60)
        
        # 1. Test ESRS Questions Loading
        self.test_esrs_load_questions()
        
        # 2. Test ESRS Assessment Start
        self.test_esrs_start_assessment()
        
        # 3. Test ESRS Questions Retrieval
        self.test_esrs_get_questions()
        
        # 4. Test Database Collections
        self.test_database_collections()
        
        # Optional: Test answer submission if assessment was created
        if self.test_assessment_id:
            self.test_esrs_submit_answer()
            self.test_esrs_assessment_results()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 ESRS TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['name']}")
                if 'error' in test:
                    print(f"     Error: {test['error']}")
                else:
                    print(f"     Expected: {test['expected']}, Got: {test['actual']}")
        
        return self.tests_passed, self.tests_run, self.failed_tests

if __name__ == "__main__":
    tester = ESRSAPITester()
    passed, total, failed = tester.run_comprehensive_esrs_tests()
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)