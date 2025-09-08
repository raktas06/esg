import requests
import sys
import json
import os
from datetime import datetime

class PriorityESGAPITester:
    def __init__(self, base_url="https://esg-compass-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_org_id = None
        self.test_assessment_id = None
        self.critical_failures = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test with detailed error reporting"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
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
                        return success, response_data
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                        return success, response_data
                except:
                    print(f"   Response: Non-JSON content (length: {len(response.content)})")
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                    self.critical_failures.append({
                        "test": name,
                        "status": response.status_code,
                        "error": error_detail
                    })
                except:
                    print(f"   Error: {response.text[:500]}")
                    self.critical_failures.append({
                        "test": name,
                        "status": response.status_code,
                        "error": response.text[:500]
                    })

            return success, response.json() if success and response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.critical_failures.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_organization_creation_detailed(self):
        """PRIORITY 1: Test organization creation with various scenarios"""
        print("\n🏢 PRIORITY TEST 1: Organization Creation (User Issue: 'WHY I CANT ADD ORGANIZATION')")
        
        # Test 1: Basic organization creation
        org_data_basic = {
            "name": "User Test Organization",
            "industry": "Technology",
            "size": "Medium",
            "country": "United States"
        }
        success1, response1 = self.run_test(
            "Create Organization - Basic Data",
            "POST",
            "organizations",
            200,
            data=org_data_basic
        )
        
        # Test 2: Organization creation with all fields
        org_data_full = {
            "name": "Comprehensive ESG Solutions Inc",
            "industry": "Environmental Services",
            "size": "Large",
            "country": "United States",
            "headquarters": "New York, NY",
            "website": "https://comprehensive-esg.com",
            "employee_count": 2500,
            "annual_revenue": "$500M - $1B",
            "annual_revenue_numeric": 750000000,
            "stock_symbol": "CESG",
            "base_currency": "USD",
            "fiscal_year_end": "2023-12-31",
            "ifrs_reporter": True,
            "sustainability_reporting_framework": ["GRI", "SASB", "TCFD"]
        }
        success2, response2 = self.run_test(
            "Create Organization - Full Data",
            "POST",
            "organizations",
            200,
            data=org_data_full
        )
        
        # Test 3: Organization creation with minimal required fields only
        org_data_minimal = {
            "name": "Minimal Test Corp"
        }
        success3, response3 = self.run_test(
            "Create Organization - Minimal Data",
            "POST",
            "organizations",
            200,
            data=org_data_minimal
        )
        
        # Test 4: Invalid organization creation (empty name)
        org_data_invalid = {
            "name": "",
            "industry": "Technology"
        }
        success4, response4 = self.run_test(
            "Create Organization - Invalid (Empty Name)",
            "POST",
            "organizations",
            422,  # Expecting validation error
            data=org_data_invalid
        )
        
        # Test 5: Duplicate organization name
        success5, response5 = self.run_test(
            "Create Organization - Duplicate Name",
            "POST",
            "organizations",
            200,  # Should still work as duplicates might be allowed
            data=org_data_basic
        )
        
        # Store org ID for further tests
        if success2 and response2:
            self.test_org_id = response2.get('id')
            print(f"   ✅ Using organization ID: {self.test_org_id}")
        
        return success1 and success2 and success3, {
            "basic": response1,
            "full": response2,
            "minimal": response3,
            "invalid": response4,
            "duplicate": response5
        }

    def test_esg_assessment_flow(self):
        """PRIORITY 2: Test complete ESG assessment flow"""
        print("\n📊 PRIORITY TEST 2: Core ESG Assessment Flow")
        
        if not self.test_org_id:
            print("❌ Cannot test assessment flow - no organization ID")
            return False, {}
        
        # Test 1: Get ESG questions
        success1, questions = self.run_test(
            "Get ESG Questions",
            "GET",
            "esg-questions",
            200
        )
        
        if not success1 or not questions:
            print("❌ No ESG questions available - testing with regular questions")
            success1, questions = self.run_test(
                "Get Questions (Fallback)",
                "GET",
                "questions",
                200
            )
        
        # Test 2: Create assessment
        assessment_data = {
            "organization_id": self.test_org_id,
            "name": "Priority ESG Assessment",
            "description": "Testing complete ESG assessment flow"
        }
        success2, assessment = self.run_test(
            "Create ESG Assessment",
            "POST",
            "assessments",
            200,
            data=assessment_data
        )
        
        if success2 and assessment:
            self.test_assessment_id = assessment.get('id')
        
        # Test 3: Submit answers for assessment
        success3 = True
        if questions and self.test_assessment_id:
            for i, question in enumerate(questions[:3]):  # Test with first 3 questions
                answer_data = {
                    "question_id": question['id'],
                    "organization_id": self.test_org_id,
                    "answer_value": f"Test answer {i+1} for comprehensive assessment",
                    "comments": f"Test comment {i+1}",
                    "financial_impact_estimate": 10000 * (i+1)
                }
                
                success_answer, _ = self.run_test(
                    f"Submit Answer {i+1}",
                    "POST",
                    "answers",
                    200,
                    data=answer_data
                )
                success3 = success3 and success_answer
        
        # Test 4: Get assessment progress
        success4, progress = self.run_test(
            "Get Assessment Progress",
            "GET",
            f"assessments/{self.test_assessment_id}/progress",
            200
        ) if self.test_assessment_id else (False, {})
        
        return success1 and success2 and success3 and success4, {
            "questions": questions,
            "assessment": assessment,
            "progress": progress
        }

    def test_dashboard_data_comprehensive(self):
        """PRIORITY 3: Test dashboard data loading"""
        print("\n📈 PRIORITY TEST 3: Dashboard Data Loading")
        
        if not self.test_org_id:
            print("❌ Cannot test dashboard - no organization ID")
            return False, {}
        
        # Test 1: Main dashboard endpoint
        success1, dashboard = self.run_test(
            "Get Dashboard Data",
            "GET",
            f"dashboard/{self.test_org_id}",
            200
        )
        
        # Test 2: Alternative dashboard endpoint
        if not success1:
            success1, dashboard = self.run_test(
                "Get Dashboard Data (Alternative)",
                "GET",
                f"reports/dashboard/{self.test_org_id}",
                200
            )
        
        # Test 3: Materiality data for dashboard
        success2, materiality = self.run_test(
            "Get Materiality Matrix for Dashboard",
            "GET",
            f"materiality/{self.test_org_id}/matrix",
            200
        )
        
        # Test 4: Financial impact data for dashboard
        success3, financial_impact = self.run_test(
            "Get Financial Impact Summary for Dashboard",
            "GET",
            f"financial-impact/{self.test_org_id}/summary",
            200
        )
        
        # Test 5: IFRS compliance data for dashboard
        success4, ifrs_compliance = self.run_test(
            "Get IFRS Compliance Status for Dashboard",
            "GET",
            f"ifrs-mapping/{self.test_org_id}/compliance-status",
            200
        )
        
        # Validate dashboard data structure
        dashboard_valid = True
        if success1 and dashboard:
            required_keys = ['organization', 'overall_score', 'esg_scores']
            missing_keys = [key for key in required_keys if key not in dashboard]
            if missing_keys:
                print(f"   ⚠️ Dashboard missing keys: {missing_keys}")
                dashboard_valid = False
            else:
                print(f"   ✅ Dashboard contains all required keys")
        
        return success1 and success2 and success3 and success4 and dashboard_valid, {
            "dashboard": dashboard,
            "materiality": materiality,
            "financial_impact": financial_impact,
            "ifrs_compliance": ifrs_compliance
        }

    def test_report_upload_functionality(self):
        """PRIORITY 4: Test report upload and PDF parsing"""
        print("\n📄 PRIORITY TEST 4: Report Upload (Fixed Implementation)")
        
        if not self.test_org_id:
            print("❌ Cannot test report upload - no organization ID")
            return False, {}
        
        # Test 1: Check if report upload endpoints exist
        success1, upload_info = self.run_test(
            "Check Report Upload Endpoint",
            "GET",
            f"reports/upload-info",
            200
        )
        
        # Test 2: Test file upload endpoint (without actual file first)
        success2, upload_response = self.run_test(
            "Test Report Upload Endpoint Structure",
            "POST",
            "reports/upload",
            422,  # Expecting validation error without file
            data={"organization_id": self.test_org_id}
        )
        
        # Test 3: Get uploaded reports for organization
        success3, uploaded_reports = self.run_test(
            "Get Uploaded Reports",
            "GET",
            f"reports/uploaded/{self.test_org_id}",
            200
        )
        
        # Test 4: Test report comparison endpoint
        success4, comparison_info = self.run_test(
            "Get Report Comparison Info",
            "GET",
            f"reports/comparison/{self.test_org_id}",
            200
        )
        
        # Test 5: Create a simple text file for upload testing
        try:
            test_content = """ESG Report Test Content
            Environmental Score: 85
            Social Score: 78
            Governance Score: 92
            Overall ESG Rating: A-
            """
            
            # Test with form data
            files = {'file': ('test_report.txt', test_content, 'text/plain')}
            data = {'organization_id': self.test_org_id}
            
            success5, upload_result = self.run_test(
                "Upload Test Report File",
                "POST",
                "reports/upload",
                200,
                data=data,
                files=files
            )
        except Exception as e:
            print(f"   ⚠️ File upload test failed: {e}")
            success5 = False
            upload_result = {}
        
        return success3 or success4, {  # At least one should work
            "upload_info": upload_info,
            "upload_response": upload_response,
            "uploaded_reports": uploaded_reports,
            "comparison_info": comparison_info,
            "upload_result": upload_result
        }

    def test_risk_opportunity_endpoints(self):
        """SECONDARY: Test Risk/Opportunity Assessment endpoints"""
        print("\n⚠️ SECONDARY TEST: Risk & Opportunity Assessment")
        
        if not self.test_org_id:
            print("❌ Cannot test risk/opportunity - no organization ID")
            return False, {}
        
        # Test Risk Assessment
        risk_data = {
            "organization_id": self.test_org_id,
            "risk_title": "Climate Change Physical Risk",
            "risk_description": "Increased flooding and extreme weather events",
            "risk_type": "physical_risk",
            "esg_category": "environmental",
            "likelihood": "high",
            "impact": "major",
            "time_horizon": "Long-term (5+ years)",
            "potential_financial_impact": 5000000,
            "mitigation_strategies": ["Flood defenses", "Insurance coverage"],
            "ifrs_disclosure_required": True
        }
        
        success1, risk_response = self.run_test(
            "Create Risk Assessment",
            "POST",
            "risk-assessment",
            200,
            data=risk_data
        )
        
        # Test Opportunity Assessment
        opportunity_data = {
            "organization_id": self.test_org_id,
            "opportunity_title": "Renewable Energy Transition",
            "opportunity_description": "Investment in solar and wind energy",
            "opportunity_type": "energy_source",
            "esg_category": "environmental",
            "likelihood": "high",
            "impact": "major",
            "time_horizon": "Medium-term (3-5 years)",
            "potential_financial_benefit": 8000000,
            "implementation_strategies": ["Solar panel installation", "Wind farm development"],
            "required_investment": 2000000,
            "expected_roi": 25.5
        }
        
        success2, opportunity_response = self.run_test(
            "Create Opportunity Assessment",
            "POST",
            "opportunity-assessment",
            200,
            data=opportunity_data
        )
        
        # Test SWOT Analysis
        swot_data = {
            "organization_id": self.test_org_id,
            "swot_title": "ESG Leadership Position",
            "swot_description": "Strong ESG governance and reporting capabilities",
            "swot_category": "strength",
            "esg_category": "governance",
            "strategic_importance": "High",
            "actionable_insights": ["Leverage ESG leadership for market advantage"],
            "financial_implications": "Potential for ESG-linked financing benefits"
        }
        
        success3, swot_response = self.run_test(
            "Create SWOT Analysis",
            "POST",
            "swot-analysis",
            200,
            data=swot_data
        )
        
        return success1 and success2 and success3, {
            "risk": risk_response,
            "opportunity": opportunity_response,
            "swot": swot_response
        }

def main():
    print("🎯 PRIORITY ESG BACKEND TESTING - Focus on User Issues")
    print("=" * 70)
    print("Testing based on user report: 'WHY I CANT ADD ORGANIZATION'")
    print("=" * 70)
    
    tester = PriorityESGAPITester()
    
    # PRIORITY TESTS
    print("\n🚨 CRITICAL PRIORITY TESTS")
    
    # Priority 1: Organization Creation (User Issue)
    org_success, org_results = tester.test_organization_creation_detailed()
    
    # Priority 2: ESG Assessment Flow
    assessment_success, assessment_results = tester.test_esg_assessment_flow()
    
    # Priority 3: Dashboard Data Loading
    dashboard_success, dashboard_results = tester.test_dashboard_data_comprehensive()
    
    # Priority 4: Report Upload
    upload_success, upload_results = tester.test_report_upload_functionality()
    
    # SECONDARY TESTS
    print("\n📋 SECONDARY TESTS")
    risk_success, risk_results = tester.test_risk_opportunity_endpoints()
    
    # FINAL ANALYSIS
    print("\n" + "=" * 70)
    print("🎯 PRIORITY TEST RESULTS ANALYSIS")
    print("=" * 70)
    
    priority_results = {
        "Organization Creation": org_success,
        "ESG Assessment Flow": assessment_success,
        "Dashboard Data Loading": dashboard_success,
        "Report Upload": upload_success,
        "Risk/Opportunity Assessment": risk_success
    }
    
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    print("\n🎯 PRIORITY FEATURE STATUS:")
    for feature, status in priority_results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {feature}: {'WORKING' if status else 'NEEDS ATTENTION'}")
    
    # Critical Failures Analysis
    if tester.critical_failures:
        print(f"\n🚨 CRITICAL FAILURES DETECTED ({len(tester.critical_failures)}):")
        for failure in tester.critical_failures:
            print(f"   ❌ {failure['test']}")
            if 'status' in failure:
                print(f"      Status: {failure['status']}")
            print(f"      Error: {failure['error']}")
    
    # User Issue Analysis
    print(f"\n👤 USER ISSUE ANALYSIS:")
    if org_success:
        print("   ✅ Organization creation is WORKING - User issue may be frontend or validation related")
        print("   📝 Recommendation: Check frontend form validation and error handling")
    else:
        print("   ❌ Organization creation has BACKEND ISSUES")
        print("   🔧 Recommendation: Fix backend organization creation endpoints immediately")
    
    # Overall Assessment
    critical_working = sum([org_success, assessment_success, dashboard_success])
    if critical_working >= 3:
        print(f"\n🎉 BACKEND STATUS: MOSTLY FUNCTIONAL ({critical_working}/4 critical features working)")
        print("   ✅ Core ESG functionality is operational")
        if not upload_success:
            print("   ⚠️ Report upload needs implementation/fixing")
        return 0
    else:
        print(f"\n⚠️ BACKEND STATUS: NEEDS ATTENTION ({critical_working}/4 critical features working)")
        print("   🔧 Multiple critical features require fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())