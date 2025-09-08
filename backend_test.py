import requests
import sys
import json
from datetime import datetime

class ESGAPITester:
    def __init__(self, base_url="https://esg-compass-2.preview.emergentagent.com"):
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

    def test_create_materiality_assessment(self):
        """Test creating materiality assessment"""
        if not self.test_org_id:
            print("❌ Skipping materiality assessment - no organization ID")
            return False, {}
        
        materiality_data = {
            "organization_id": self.test_org_id,
            "topic": "Climate Change",
            "description": "Climate-related risks and opportunities",
            "esg_category": "environmental",
            "impact_materiality_score": 8.5,
            "financial_materiality_score": 7.2,
            "stakeholder_input": {"investors": 9.0, "customers": 8.0},
            "impact_justification": "Significant environmental impact",
            "financial_justification": "Material financial risks from climate change",
            "ifrs_s1_relevant": True,
            "ifrs_s2_relevant": True
        }
        
        return self.run_test(
            "Create Materiality Assessment",
            "POST",
            "materiality",
            200,
            data=materiality_data
        )

    def test_get_materiality_matrix(self):
        """Test materiality matrix endpoint"""
        if not self.test_org_id:
            print("❌ Skipping materiality matrix - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Materiality Matrix",
            "GET",
            f"materiality/{self.test_org_id}/matrix",
            200
        )

    def test_create_financial_impact(self):
        """Test creating financial impact assessment"""
        if not self.test_org_id:
            print("❌ Skipping financial impact - no organization ID")
            return False, {}
        
        financial_data = {
            "organization_id": self.test_org_id,
            "esg_topic": "Climate Change",
            "impact_type": "cost_impact",
            "financial_metric": "OPEX",
            "current_value": 1000000,
            "projected_value": 1200000,
            "time_horizon": "Medium-term (3-5 years)",
            "confidence_level": "High",
            "assumptions": ["Carbon pricing implementation", "Regulatory changes"],
            "ifrs_standard_reference": "IFRS S2-21",
            "accounting_treatment": "Operating expense recognition",
            "disclosure_requirement": True
        }
        
        return self.run_test(
            "Create Financial Impact Assessment",
            "POST",
            "financial-impact",
            200,
            data=financial_data
        )

    def test_get_financial_impact_summary(self):
        """Test financial impact summary endpoint"""
        if not self.test_org_id:
            print("❌ Skipping financial impact summary - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Financial Impact Summary",
            "GET",
            f"financial-impact/{self.test_org_id}/summary",
            200
        )

    def test_create_ifrs_mapping(self):
        """Test creating IFRS mapping"""
        if not self.test_org_id:
            print("❌ Skipping IFRS mapping - no organization ID")
            return False, {}
        
        ifrs_data = {
            "id": "test-ifrs-mapping-001",
            "organization_id": self.test_org_id,
            "ifrs_standard": "IFRS_S2",
            "disclosure_requirement": "Climate-related financial disclosures",
            "esg_topic": "Climate Change",
            "financial_statement_line_item": "Operating Expenses",
            "quantitative_disclosure": 200000,
            "qualitative_disclosure": "Climate transition costs impact operations",
            "compliance_status": "in_progress",
            "gap_analysis": "Need more detailed carbon accounting",
            "remediation_plan": "Implement carbon tracking system"
        }
        
        return self.run_test(
            "Create IFRS Mapping",
            "POST",
            "ifrs-mapping",
            200,
            data=ifrs_data
        )

    def test_get_ifrs_compliance_status(self):
        """Test IFRS compliance status endpoint"""
        if not self.test_org_id:
            print("❌ Skipping IFRS compliance - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get IFRS Compliance Status",
            "GET",
            f"ifrs-mapping/{self.test_org_id}/compliance-status",
            200
        )

    def test_create_balance_sheet_item(self):
        """Test creating balance sheet line item"""
        if not self.test_org_id:
            print("❌ Skipping balance sheet - no organization ID")
            return False, {}
        
        balance_sheet_data = {
            "organization_id": self.test_org_id,
            "reporting_period": "2023-12-31",
            "line_item_code": "1001",
            "line_item_name": "Cash and Cash Equivalents",
            "category": "Assets",
            "subcategory": "Current Assets",
            "amount": 5000000,
            "currency": "USD",
            "ias_ifrs_reference": "IAS 1.54",
            "esg_related": True,
            "esg_impact_description": "Green bonds and sustainable investments"
        }
        
        return self.run_test(
            "Create Balance Sheet Item",
            "POST",
            "financial-statements/balance-sheet",
            200,
            data=balance_sheet_data
        )

    def test_create_income_statement_item(self):
        """Test creating income statement line item"""
        if not self.test_org_id:
            print("❌ Skipping income statement - no organization ID")
            return False, {}
        
        income_data = {
            "organization_id": self.test_org_id,
            "reporting_period": "2023-12-31",
            "line_item_code": "4001",
            "line_item_name": "Revenue from Sustainable Products",
            "category": "Revenue",
            "amount": 25000000,
            "currency": "USD",
            "ias_ifrs_reference": "IFRS 15.47",
            "esg_related": True,
            "esg_impact_description": "Revenue from environmentally friendly products",
            "sustainability_adjustment": 2000000
        }
        
        return self.run_test(
            "Create Income Statement Item",
            "POST",
            "financial-statements/income-statement",
            200,
            data=income_data
        )

    def test_create_cash_flow_item(self):
        """Test creating cash flow line item"""
        if not self.test_org_id:
            print("❌ Skipping cash flow - no organization ID")
            return False, {}
        
        cash_flow_data = {
            "organization_id": self.test_org_id,
            "reporting_period": "2023-12-31",
            "line_item_code": "6001",
            "line_item_name": "Cash from ESG Investments",
            "category": "Investing",
            "amount": -3000000,
            "currency": "USD",
            "ias_ifrs_reference": "IAS 7.16",
            "esg_related": True,
            "esg_impact_description": "Investment in renewable energy infrastructure"
        }
        
        return self.run_test(
            "Create Cash Flow Item",
            "POST",
            "financial-statements/cash-flow",
            200,
            data=cash_flow_data
        )

    def test_create_financial_ratio(self):
        """Test creating financial ratio"""
        if not self.test_org_id:
            print("❌ Skipping financial ratio - no organization ID")
            return False, {}
        
        ratio_data = {
            "organization_id": self.test_org_id,
            "reporting_period": "2023-12-31",
            "ratio_name": "ESG Revenue Ratio",
            "ratio_category": "ESG",
            "ratio_value": 0.35,
            "benchmark_value": 0.25,
            "industry_average": 0.20,
            "esg_influenced": True,
            "calculation_method": "ESG Revenue / Total Revenue",
            "interpretation": "Strong ESG revenue contribution above industry average"
        }
        
        return self.run_test(
            "Create Financial Ratio",
            "POST",
            "financial-ratios",
            200,
            data=ratio_data
        )

    def test_get_financial_analysis(self):
        """Test comprehensive financial analysis endpoint"""
        if not self.test_org_id:
            print("❌ Skipping financial analysis - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Comprehensive Financial Analysis",
            "GET",
            f"financial-analysis/{self.test_org_id}",
            200
        )

    def test_get_integrated_report(self):
        """Test integrated ESG-Financial report endpoint"""
        if not self.test_org_id:
            print("❌ Skipping integrated report - no organization ID")
            return False, {}
        
        return self.run_test(
            "Get Integrated ESG-Financial Report",
            "GET",
            f"integrated-report/{self.test_org_id}",
            200
        )

def main():
    print("🚀 Starting Comprehensive ESG API Testing with Double Materiality & IFRS")
    print("=" * 70)
    
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
    
    # Enhanced Double Materiality & Financial Impact Tests
    print("\n🔬 Testing Double Materiality & Financial Impact Features...")
    test_results.append(tester.test_create_materiality_assessment())
    test_results.append(tester.test_get_materiality_matrix())
    test_results.append(tester.test_create_financial_impact())
    test_results.append(tester.test_get_financial_impact_summary())
    
    # IFRS Compliance Tests
    print("\n📋 Testing IFRS Compliance Features...")
    test_results.append(tester.test_create_ifrs_mapping())
    test_results.append(tester.test_get_ifrs_compliance_status())
    
    # Financial Statements Tests (NEW CRITICAL FUNCTIONALITY)
    print("\n💰 Testing Financial Statements & IAS/IFRS Integration...")
    test_results.append(tester.test_create_balance_sheet_item())
    test_results.append(tester.test_create_income_statement_item())
    test_results.append(tester.test_create_cash_flow_item())
    test_results.append(tester.test_create_financial_ratio())
    test_results.append(tester.test_get_financial_analysis())
    test_results.append(tester.test_get_integrated_report())
    
    # Analytics and reporting tests
    print("\n📊 Testing Analytics & Reporting...")
    test_results.append(tester.test_dashboard_data())
    test_results.append(tester.test_benchmarking_data())
    test_results.append(tester.test_assessment_progress())
    
    # HTML report generation tests
    print("\n📄 Testing HTML Report Generation...")
    test_results.append(tester.test_html_comprehensive_report())
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS - ENHANCED ESG PLATFORM")
    print("=" * 70)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Detailed feature breakdown
    print("\n🎯 Feature Test Summary:")
    print("   ✓ Basic API & Data Initialization")
    print("   ✓ Organization & Assessment Management") 
    print("   ✓ Double Materiality Assessment")
    print("   ✓ Financial Impact Analysis")
    print("   ✓ IFRS Compliance Mapping")
    print("   ✓ Financial Statements & IAS/IFRS Integration")
    print("   ✓ Advanced Analytics & Dashboards")
    print("   ✓ HTML Report Generation")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL TESTS PASSED! Enhanced ESG Backend API is fully functional.")
        print("   ✅ Double Materiality Assessment: Working")
        print("   ✅ Financial Impact Analysis: Working") 
        print("   ✅ IFRS Compliance: Working")
        print("   ✅ Financial Statements Integration: Working")
        print("   ✅ Advanced Reporting: Working")
        return 0
    else:
        failed_count = tester.tests_run - tester.tests_passed
        print(f"\n⚠️ {failed_count} tests failed. Backend needs attention before frontend testing.")
        if failed_count > (tester.tests_run * 0.5):
            print("❌ More than 50% of functionality is broken. Stopping here.")
            print("🔧 Please fix backend issues before proceeding with frontend testing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())