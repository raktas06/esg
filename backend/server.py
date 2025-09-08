from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import bcrypt
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)
JWT_SECRET = "esg-reporting-secret-key"  # In production, use environment variable

# Enums
class ESGCategory(str, Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    TEXT = "text"
    NUMERICAL = "numerical"
    BOOLEAN = "boolean"

class CanvasSection(str, Enum):
    KEY_PARTNERSHIPS = "key_partnerships"
    KEY_ACTIVITIES = "key_activities"
    KEY_RESOURCES = "key_resources"
    VALUE_PROPOSITIONS = "value_propositions"
    CUSTOMER_RELATIONSHIPS = "customer_relationships"
    CHANNELS = "channels"
    CUSTOMER_SEGMENTS = "customer_segments"
    COST_STRUCTURE = "cost_structure"
    REVENUE_STREAMS = "revenue_streams"

class Standard(str, Enum):
    GRI = "GRI"
    EFRAG = "EFRAG"
    IFRS = "IFRS"

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"

class AssessmentStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    APPROVED = "approved"

class ReportType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    EXECUTIVE_SUMMARY = "executive_summary"
    GRI_COMPLIANCE = "gri_compliance"
    CANVAS_OVERVIEW = "canvas_overview"

# Enhanced Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.CONTRIBUTOR
    organization_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    role: UserRole = UserRole.CONTRIBUTOR
    organization_id: str

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    description: Optional[str] = None
    question_type: QuestionType
    esg_category: ESGCategory
    canvas_section: CanvasSection
    standard: Standard
    reference_code: Optional[str] = None  # e.g., "GRI 102-1"
    options: Optional[List[str]] = None  # for multiple choice
    scale_min: Optional[int] = None  # for scale questions
    scale_max: Optional[int] = None
    scale_labels: Optional[Dict[str, str]] = None
    is_required: bool = True
    weight: float = 1.0  # For scoring calculations
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuestionCreate(BaseModel):
    question_text: str
    description: Optional[str] = None
    question_type: QuestionType
    esg_category: ESGCategory
    canvas_section: CanvasSection
    standard: Standard
    reference_code: Optional[str] = None
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_labels: Optional[Dict[str, str]] = None
    is_required: bool = True
    weight: float = 1.0

class Answer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    organization_id: str
    user_id: str
    answer_value: Any  # Can be string, number, boolean, list
    comments: Optional[str] = None
    status: str = "submitted"  # submitted, approved, needs_review
    score: Optional[float] = None  # Calculated score for this answer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnswerCreate(BaseModel):
    question_id: str
    organization_id: str
    answer_value: Any
    comments: Optional[str] = None

class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None  # Small, Medium, Large, Enterprise
    country: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    stock_symbol: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrganizationCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    country: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    stock_symbol: Optional[str] = None

class Assessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    status: AssessmentStatus = AssessmentStatus.DRAFT
    progress: Dict[CanvasSection, float] = {}  # percentage completion per section
    scores: Dict[str, float] = {}  # ESG scores by category
    overall_score: Optional[float] = None
    assigned_users: List[str] = []  # User IDs assigned to this assessment
    reviewer_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None

class AssessmentCreate(BaseModel):
    organization_id: str
    name: str
    description: Optional[str] = None
    assigned_users: List[str] = []
    reviewer_id: Optional[str] = None
    due_date: Optional[datetime] = None

class ESGReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str
    organization_id: str
    report_type: str = "comprehensive"  # comprehensive, summary, compliance
    generated_by: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    report_data: Dict[str, Any] = {}
    file_url: Optional[str] = None

# HTML Report Templates
def get_comprehensive_html_report_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG Comprehensive Report - {organization_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            margin: -20px -20px 40px -20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .report-meta {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .meta-item {{
            text-align: center;
        }}
        .meta-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .meta-value {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }}
        .esg-scores {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .score-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid;
        }}
        .score-card.environmental {{
            border-left-color: #10b981;
        }}
        .score-card.social {{
            border-left-color: #3b82f6;
        }}
        .score-card.governance {{
            border-left-color: #8b5cf6;
        }}
        .score-title {{
            font-size: 1.1em;
            color: #666;
            margin-bottom: 10px;
        }}
        .score-value {{
            font-size: 3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .score-bar {{
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        .score-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        .score-fill.environmental {{
            background: linear-gradient(90deg, #10b981, #34d399);
        }}
        .score-fill.social {{
            background: linear-gradient(90deg, #3b82f6, #60a5fa);
        }}
        .score-fill.governance {{
            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
        }}
        .canvas-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .canvas-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }}
        .progress-bar {{
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 3px;
        }}
        .question-item {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #e5e7eb;
        }}
        .question-item.answered {{
            border-left-color: #10b981;
        }}
        .question-text {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}
        .question-answer {{
            color: #666;
            font-style: italic;
        }}
        .question-meta {{
            margin-top: 10px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .badge.environmental {{
            background: #dcfce7;
            color: #166534;
        }}
        .badge.social {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .badge.governance {{
            background: #e9d5ff;
            color: #7c2d12;
        }}
        .badge.standard {{
            background: #f3f4f6;
            color: #374151;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #666;
        }}
        .recommendations {{
            background: #fef3c7;
            border-left: 5px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .recommendations h3 {{
            color: #92400e;
            margin-bottom: 15px;
        }}
        .recommendation-item {{
            margin-bottom: 10px;
            padding-left: 20px;
            position: relative;
        }}
        .recommendation-item:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #f59e0b;
            font-weight: bold;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
                margin: 0;
                padding: 0;
            }}
            .header {{
                margin: 0 0 40px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESG Sustainability Report</h1>
            <p>{organization_name} • {industry} • {report_date}</p>
        </div>

        <div class="report-meta">
            <div class="meta-item">
                <div class="meta-label">Overall ESG Score</div>
                <div class="meta-value">{overall_score}/100</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Assessment Progress</div>
                <div class="meta-value">{completion_percentage}%</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Questions Answered</div>
                <div class="meta-value">{answered_questions}/{total_questions}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Report Generated</div>
                <div class="meta-value">{report_date}</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">ESG Performance Overview</h2>
            <div class="esg-scores">
                <div class="score-card environmental">
                    <div class="score-title">Environmental Score</div>
                    <div class="score-value">{environmental_score}</div>
                    <div class="score-bar">
                        <div class="score-fill environmental" style="width: {environmental_score}%"></div>
                    </div>
                    <p>Sustainability & Environmental Impact</p>
                </div>
                <div class="score-card social">
                    <div class="score-title">Social Score</div>
                    <div class="score-value">{social_score}</div>
                    <div class="score-bar">
                        <div class="score-fill social" style="width: {social_score}%"></div>
                    </div>
                    <p>Social Responsibility & Community Impact</p>
                </div>
                <div class="score-card governance">
                    <div class="score-title">Governance Score</div>
                    <div class="score-value">{governance_score}</div>
                    <div class="score-bar">
                        <div class="score-fill governance" style="width: {governance_score}%"></div>
                    </div>
                    <p>Corporate Governance & Ethics</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Canvas Section Analysis</h2>
            {canvas_sections_html}
        </div>

        <div class="section">
            <h2 class="section-title">Detailed Assessment Responses</h2>
            {questions_html}
        </div>

        <div class="recommendations">
            <h3>Key Recommendations</h3>
            {recommendations_html}
        </div>

        <div class="footer">
            <p><strong>ESG Canvas Reporter</strong> - Advanced Sustainability Analytics Platform</p>
            <p>Report generated on {report_date} • Based on GRI, EFRAG, and IFRS standards</p>
        </div>
    </div>
</body>
</html>
"""

def get_executive_summary_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG Executive Summary - {organization_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background: white;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .executive-summary {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-score {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .summary-score.environmental {{ color: #10b981; }}
        .summary-score.social {{ color: #3b82f6; }}
        .summary-score.governance {{ color: #8b5cf6; }}
        .summary-score.overall {{ color: #667eea; }}
        .key-findings {{
            margin-bottom: 30px;
        }}
        .finding-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .priority-actions {{
            background: #fef3c7;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #f59e0b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESG Executive Summary</h1>
            <h2>{organization_name}</h2>
            <p>{report_date}</p>
        </div>

        <div class="executive-summary">
            <h3>Executive Overview</h3>
            <p>This executive summary provides a high-level overview of {organization_name}'s ESG performance based on our comprehensive sustainability assessment using business model canvas methodology and international standards (GRI, EFRAG, IFRS).</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-score overall">{overall_score}</div>
                <h4>Overall ESG Score</h4>
                <p>Out of 100</p>
            </div>
            <div class="summary-card">
                <div class="summary-score environmental">{environmental_score}</div>
                <h4>Environmental</h4>
                <p>Sustainability Impact</p>
            </div>
            <div class="summary-card">
                <div class="summary-score social">{social_score}</div>
                <h4>Social</h4>
                <p>Community & Stakeholders</p>
            </div>
            <div class="summary-card">
                <div class="summary-score governance">{governance_score}</div>
                <h4>Governance</h4>
                <p>Ethics & Management</p>
            </div>
        </div>

        <div class="key-findings">
            <h3>Key Findings</h3>
            {key_findings_html}
        </div>

        <div class="priority-actions">
            <h3>Priority Actions</h3>
            {priority_actions_html}
        </div>
    </div>
</body>
</html>
"""

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data and isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        if 'due_date' in data and isinstance(data['due_date'], datetime):
            data['due_date'] = data['due_date'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        if 'created_at' in item and isinstance(item['created_at'], str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
        if 'updated_at' in item and isinstance(item['updated_at'], str):
            item['updated_at'] = datetime.fromisoformat(item['updated_at'])
        if 'due_date' in item and isinstance(item['due_date'], str):
            item['due_date'] = datetime.fromisoformat(item['due_date'])
    return item

def calculate_esg_score(answers, questions):
    """Calculate ESG scores based on answers and question weights"""
    scores = {"environmental": 0, "social": 0, "governance": 0}
    weights = {"environmental": 0, "social": 0, "governance": 0}
    
    for answer in answers:
        question = next((q for q in questions if q["id"] == answer["question_id"]), None)
        if not question:
            continue
            
        category = question["esg_category"]
        weight = question.get("weight", 1.0)
        weights[category] += weight
        
        # Score calculation based on question type
        if question["question_type"] == "scale":
            max_score = question.get("scale_max", 5)
            score = (answer["answer_value"] / max_score) * weight
        elif question["question_type"] == "boolean":
            score = weight if answer["answer_value"] else 0
        elif question["question_type"] == "multiple_choice":
            # Assign scores based on option position (higher = better)
            options = question.get("options", [])
            if options and answer["answer_value"] in options:
                position = options.index(answer["answer_value"])
                score = (position / (len(options) - 1)) * weight if len(options) > 1 else weight
            else:
                score = 0
        else:
            # For text and numerical, assign a default score
            score = weight * 0.7  # 70% for completion
        
        scores[category] += score
    
    # Normalize scores to percentages
    for category in scores:
        if weights[category] > 0:
            scores[category] = (scores[category] / weights[category]) * 100
        else:
            scores[category] = 0
    
    return scores

# Canvas section definitions
CANVAS_SECTIONS = {
    "key_partnerships": {"title": "Key Partnerships", "description": "Sustainability partnerships and supplier relationships"},
    "key_activities": {"title": "Key Activities", "description": "Core ESG activities and environmental practices"},
    "key_resources": {"title": "Key Resources", "description": "ESG governance, policies, and sustainable resources"},
    "value_propositions": {"title": "Value Propositions", "description": "ESG value creation and sustainability benefits"},
    "customer_relationships": {"title": "Stakeholder Relationships", "description": "Community engagement and stakeholder management"},
    "channels": {"title": "ESG Communication", "description": "Sustainability reporting and communication channels"},
    "customer_segments": {"title": "Stakeholder Groups", "description": "Different stakeholder segments and their ESG interests"},
    "cost_structure": {"title": "ESG Costs", "description": "Sustainability investments and ESG-related costs"},
    "revenue_streams": {"title": "ESG Value & Benefits", "description": "Revenue and benefits from ESG initiatives"}
}

# Routes
@api_router.get("/")
async def root():
    return {"message": "ESG Reporting API v2.0 - Enhanced with HTML Reports"}

# User management routes
@api_router.post("/users", response_model=User)
async def create_user(input: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": input.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Hash password
    hashed_password = bcrypt.hashpw(input.password.encode('utf-8'), bcrypt.gensalt())
    
    user_dict = input.dict()
    del user_dict["password"]
    user_obj = User(**user_dict)
    
    # Store user with hashed password
    user_data = prepare_for_mongo(user_obj.dict())
    user_data["password_hash"] = hashed_password.decode('utf-8')
    
    await db.users.insert_one(user_data)
    return user_obj

@api_router.get("/users", response_model=List[User])
async def get_users(organization_id: Optional[str] = None):
    filter_dict = {}
    if organization_id:
        filter_dict["organization_id"] = organization_id
    
    users = await db.users.find(filter_dict).to_list(1000)
    return [User(**parse_from_mongo(user)) for user in users]

# Enhanced Organization routes
@api_router.post("/organizations", response_model=Organization)
async def create_organization(input: OrganizationCreate):
    org_dict = input.dict()
    org_obj = Organization(**org_dict)
    org_data = prepare_for_mongo(org_obj.dict())
    await db.organizations.insert_one(org_data)
    return org_obj

@api_router.get("/organizations", response_model=List[Organization])
async def get_organizations():
    orgs = await db.organizations.find().to_list(1000)
    return [Organization(**parse_from_mongo(org)) for org in orgs]

@api_router.get("/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: str):
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**parse_from_mongo(org))

@api_router.put("/organizations/{org_id}", response_model=Organization)
async def update_organization(org_id: str, input: OrganizationCreate):
    update_data = prepare_for_mongo(input.dict())
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.organizations.update_one(
        {"id": org_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    updated_org = await db.organizations.find_one({"id": org_id})
    return Organization(**parse_from_mongo(updated_org))

# Question routes
@api_router.post("/questions", response_model=Question)
async def create_question(input: QuestionCreate):
    question_dict = input.dict()
    question_obj = Question(**question_dict)
    question_data = prepare_for_mongo(question_obj.dict())
    await db.questions.insert_one(question_data)
    return question_obj

@api_router.get("/questions", response_model=List[Question])
async def get_questions(
    esg_category: Optional[ESGCategory] = None,
    canvas_section: Optional[CanvasSection] = None,
    standard: Optional[Standard] = None
):
    filter_dict = {}
    if esg_category:
        filter_dict["esg_category"] = esg_category
    if canvas_section:
        filter_dict["canvas_section"] = canvas_section
    if standard:
        filter_dict["standard"] = standard
    
    questions = await db.questions.find(filter_dict).to_list(1000)
    return [Question(**parse_from_mongo(q)) for q in questions]

@api_router.get("/questions/canvas-section/{canvas_section}", response_model=List[Question])
async def get_questions_by_canvas_section(canvas_section: CanvasSection):
    questions = await db.questions.find({"canvas_section": canvas_section}).to_list(1000)
    return [Question(**parse_from_mongo(q)) for q in questions]

# Enhanced Assessment routes
@api_router.post("/assessments", response_model=Assessment)
async def create_assessment(input: AssessmentCreate):
    assessment_dict = input.dict()
    assessment_dict["created_by"] = "default_user"  # TODO: Get from auth
    assessment_obj = Assessment(**assessment_dict)
    assessment_data = prepare_for_mongo(assessment_obj.dict())
    await db.assessments.insert_one(assessment_data)
    return assessment_obj

@api_router.get("/assessments", response_model=List[Assessment])
async def get_assessments(organization_id: Optional[str] = None):
    filter_dict = {}
    if organization_id:
        filter_dict["organization_id"] = organization_id
    
    assessments = await db.assessments.find(filter_dict).to_list(1000)
    return [Assessment(**parse_from_mongo(a)) for a in assessments]

@api_router.get("/assessments/{assessment_id}", response_model=Assessment)
async def get_assessment(assessment_id: str):
    assessment = await db.assessments.find_one({"id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return Assessment(**parse_from_mongo(assessment))

@api_router.put("/assessments/{assessment_id}/status")
async def update_assessment_status(assessment_id: str, status: AssessmentStatus):
    result = await db.assessments.update_one(
        {"id": assessment_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {"message": f"Assessment status updated to {status}"}

# Enhanced Answer routes
@api_router.post("/answers", response_model=Answer)
async def create_or_update_answer(input: AnswerCreate):
    # Check if answer already exists
    existing_answer = await db.answers.find_one({
        "question_id": input.question_id,
        "organization_id": input.organization_id
    })
    
    if existing_answer:
        # Update existing answer
        update_data = {
            "answer_value": input.answer_value,
            "comments": input.comments,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.answers.update_one(
            {"id": existing_answer["id"]},
            {"$set": update_data}
        )
        updated_answer = await db.answers.find_one({"id": existing_answer["id"]})
        return Answer(**parse_from_mongo(updated_answer))
    else:
        # Create new answer
        answer_dict = input.dict()
        answer_dict["user_id"] = "default_user"  # TODO: Add proper user management
        answer_obj = Answer(**answer_dict)
        answer_data = prepare_for_mongo(answer_obj.dict())
        await db.answers.insert_one(answer_data)
        return answer_obj

@api_router.get("/answers", response_model=List[Answer])
async def get_answers(
    organization_id: Optional[str] = None,
    question_id: Optional[str] = None
):
    filter_dict = {}
    if organization_id:
        filter_dict["organization_id"] = organization_id
    if question_id:
        filter_dict["question_id"] = question_id
    
    answers = await db.answers.find(filter_dict).to_list(1000)
    return [Answer(**parse_from_mongo(a)) for a in answers]

# Enhanced progress and scoring routes
@api_router.get("/assessments/{assessment_id}/progress")
async def get_assessment_progress(assessment_id: str):
    # Get assessment
    assessment = await db.assessments.find_one({"id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get all questions and answers
    questions = await db.questions.find().to_list(1000)
    answers = await db.answers.find({"organization_id": assessment["organization_id"]}).to_list(1000)
    
    # Calculate progress for each canvas section
    progress = {}
    for section in CanvasSection:
        section_questions = [q for q in questions if q["canvas_section"] == section.value]
        total_questions = len(section_questions)
        
        if total_questions == 0:
            progress[section.value] = 0
        else:
            question_ids = [q["id"] for q in section_questions]
            answered = [a for a in answers if a["question_id"] in question_ids]
            progress[section.value] = (len(answered) / total_questions) * 100
    
    # Calculate ESG scores
    scores = calculate_esg_score(answers, questions)
    overall_score = sum(scores.values()) / len(scores) if scores else 0
    
    return {
        "assessment_id": assessment_id,
        "progress": progress,
        "esg_scores": scores,
        "overall_score": overall_score,
        "total_questions": len(questions),
        "answered_questions": len(answers)
    }

# Advanced reporting routes
@api_router.get("/reports/dashboard/{organization_id}")
async def get_dashboard_data(organization_id: str):
    """Get comprehensive dashboard data for an organization"""
    
    # Get organization
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get assessments
    assessments = await db.assessments.find({"organization_id": organization_id}).to_list(100)
    
    # Get questions and answers
    questions = await db.questions.find().to_list(1000)
    answers = await db.answers.find({"organization_id": organization_id}).to_list(1000)
    
    # Calculate scores
    scores = calculate_esg_score(answers, questions)
    overall_score = sum(scores.values()) / len(scores) if scores else 0
    
    # Calculate completion by canvas section
    canvas_completion = {}
    for section in CanvasSection:
        section_questions = [q for q in questions if q["canvas_section"] == section.value]
        total = len(section_questions)
        answered = len([a for a in answers if any(q["id"] == a["question_id"] for q in section_questions)])
        canvas_completion[section.value] = {
            "total": total,
            "answered": answered,
            "percentage": (answered / total * 100) if total > 0 else 0
        }
    
    # Calculate completion by ESG category
    esg_completion = {}
    for category in ESGCategory:
        category_questions = [q for q in questions if q["esg_category"] == category.value]
        total = len(category_questions)
        answered = len([a for a in answers if any(q["id"] == a["question_id"] for q in category_questions)])
        esg_completion[category.value] = {
            "total": total,
            "answered": answered,
            "percentage": (answered / total * 100) if total > 0 else 0
        }
    
    return {
        "organization": Organization(**parse_from_mongo(org)),
        "assessments_count": len(assessments),
        "overall_score": overall_score,
        "esg_scores": scores,
        "canvas_completion": canvas_completion,
        "esg_completion": esg_completion,
        "total_questions": len(questions),
        "answered_questions": len(answers),
        "completion_percentage": (len(answers) / len(questions) * 100) if len(questions) > 0 else 0
    }

@api_router.get("/reports/benchmarking/{organization_id}")
async def get_benchmarking_data(organization_id: str):
    """Get benchmarking data comparing organization to industry averages"""
    
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get organization answers
    org_answers = await db.answers.find({"organization_id": organization_id}).to_list(1000)
    questions = await db.questions.find().to_list(1000)
    
    # Calculate organization scores
    org_scores = calculate_esg_score(org_answers, questions)
    
    # Get industry peers (same industry)
    industry_orgs = await db.organizations.find({"industry": org.get("industry")}).to_list(100)
    industry_org_ids = [o["id"] for o in industry_orgs if o["id"] != organization_id]
    
    # Calculate industry averages
    industry_scores = {"environmental": [], "social": [], "governance": []}
    
    for org_id in industry_org_ids:
        org_answers_peer = await db.answers.find({"organization_id": org_id}).to_list(1000)
        if org_answers_peer:  # Only include if they have answers
            peer_scores = calculate_esg_score(org_answers_peer, questions)
            for category in industry_scores:
                industry_scores[category].append(peer_scores[category])
    
    # Calculate averages
    industry_averages = {}
    for category in industry_scores:
        if industry_scores[category]:
            industry_averages[category] = sum(industry_scores[category]) / len(industry_scores[category])
        else:
            industry_averages[category] = 0
    
    return {
        "organization_scores": org_scores,
        "industry_averages": industry_averages,
        "industry": org.get("industry"),
        "peer_count": len(industry_org_ids),
        "comparison": {
            category: {
                "organization": org_scores[category],
                "industry": industry_averages[category],
                "difference": org_scores[category] - industry_averages[category]
            }
            for category in org_scores
        }
    }

# HTML Report Generation Routes
@api_router.get("/reports/html/{organization_id}/comprehensive", response_class=HTMLResponse)
async def generate_comprehensive_html_report(organization_id: str):
    """Generate comprehensive HTML report for an organization"""
    
    # Get organization data
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get dashboard data
    dashboard_data = await get_dashboard_data(organization_id)
    questions = await db.questions.find().to_list(1000)
    answers = await db.answers.find({"organization_id": organization_id}).to_list(1000)
    
    # Create answer lookup
    answer_lookup = {a["question_id"]: a for a in answers}
    
    # Generate canvas sections HTML
    canvas_sections_html = ""
    for section_key, section_info in CANVAS_SECTIONS.items():
        completion = dashboard_data["canvas_completion"].get(section_key, {"percentage": 0, "answered": 0, "total": 0})
        section_questions = [q for q in questions if q["canvas_section"] == section_key]
        
        canvas_sections_html += f"""
        <div class="canvas-section">
            <div class="canvas-title">{section_info['title']}</div>
            <p>{section_info['description']}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {completion['percentage']}%"></div>
            </div>
            <div style="text-align: right; margin-top: 5px; color: #666; font-size: 0.9em;">
                {completion['answered']} of {completion['total']} questions completed ({completion['percentage']:.1f}%)
            </div>
        </div>
        """
    
    # Generate questions HTML
    questions_html = ""
    for question in questions:
        answer = answer_lookup.get(question["id"])
        answered_class = "answered" if answer else ""
        answer_text = str(answer["answer_value"]) if answer else "Not answered"
        
        # Format answer based on question type
        if answer and question["question_type"] == "boolean":
            answer_text = "Yes" if answer["answer_value"] else "No"
        elif answer and question["question_type"] == "scale":
            scale_label = question.get("scale_labels", {}).get(str(answer["answer_value"]), "")
            answer_text = f"{answer['answer_value']} - {scale_label}" if scale_label else str(answer["answer_value"])
        
        questions_html += f"""
        <div class="question-item {answered_class}">
            <div class="question-text">{question['question_text']}</div>
            <div class="question-answer">{answer_text}</div>
            <div class="question-meta">
                <span class="badge {question['esg_category']}">{question['esg_category'].title()}</span>
                <span class="badge standard">{question['standard']}</span>
                {f'<span class="badge standard">{question["reference_code"]}</span>' if question.get("reference_code") else ''}
                <span class="badge standard">Weight: {question['weight']}</span>
            </div>
        </div>
        """
    
    # Generate recommendations HTML
    recommendations = []
    if dashboard_data["esg_scores"]["environmental"] < 70:
        recommendations.append("Focus on environmental sustainability initiatives and partnerships")
    if dashboard_data["esg_scores"]["social"] < 70:
        recommendations.append("Enhance social responsibility programs and community engagement")
    if dashboard_data["esg_scores"]["governance"] < 70:
        recommendations.append("Strengthen governance frameworks and transparency measures")
    if dashboard_data["completion_percentage"] < 100:
        recommendations.append(f"Complete remaining {dashboard_data['total_questions'] - dashboard_data['answered_questions']} questions for comprehensive assessment")
    
    recommendations_html = ""
    for rec in recommendations:
        recommendations_html += f'<div class="recommendation-item">{rec}</div>'
    
    # Format template
    template = get_comprehensive_html_report_template()
    html_report = template.format(
        organization_name=org["name"],
        industry=org.get("industry", "Various"),
        report_date=datetime.now().strftime("%B %d, %Y"),
        overall_score=f"{dashboard_data['overall_score']:.1f}",
        completion_percentage=f"{dashboard_data['completion_percentage']:.0f}",
        answered_questions=dashboard_data["answered_questions"],
        total_questions=dashboard_data["total_questions"],
        environmental_score=f"{dashboard_data['esg_scores']['environmental']:.1f}",
        social_score=f"{dashboard_data['esg_scores']['social']:.1f}",
        governance_score=f"{dashboard_data['esg_scores']['governance']:.1f}",
        canvas_sections_html=canvas_sections_html,
        questions_html=questions_html,
        recommendations_html=recommendations_html
    )
    
    return HTMLResponse(content=html_report)

@api_router.get("/reports/html/{organization_id}/executive", response_class=HTMLResponse)
async def generate_executive_summary_html(organization_id: str):
    """Generate executive summary HTML report for an organization"""
    
    # Get organization data
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get dashboard data
    dashboard_data = await get_dashboard_data(organization_id)
    
    # Generate key findings
    key_findings = []
    if dashboard_data["esg_scores"]["environmental"] >= 80:
        key_findings.append("Strong environmental performance with comprehensive sustainability practices")
    elif dashboard_data["esg_scores"]["environmental"] >= 60:
        key_findings.append("Moderate environmental performance with room for improvement in sustainability initiatives")
    else:
        key_findings.append("Environmental performance requires significant attention and investment")
    
    if dashboard_data["overall_score"] >= 75:
        key_findings.append("Above-average overall ESG performance demonstrates commitment to sustainability")
    else:
        key_findings.append("ESG performance is below industry standards and requires strategic improvement")
    
    key_findings_html = ""
    for finding in key_findings:
        key_findings_html += f'<div class="finding-item">{finding}</div>'
    
    # Generate priority actions
    priority_actions = []
    lowest_score = min(dashboard_data["esg_scores"], key=dashboard_data["esg_scores"].get)
    priority_actions.append(f"Prioritize improvements in {lowest_score} performance")
    priority_actions.append("Complete comprehensive ESG assessment for detailed insights")
    priority_actions.append("Develop ESG strategy aligned with business objectives")
    
    priority_actions_html = ""
    for action in priority_actions:
        priority_actions_html += f'<div class="recommendation-item">{action}</div>'
    
    # Format template
    template = get_executive_summary_template()
    html_report = template.format(
        organization_name=org["name"],
        report_date=datetime.now().strftime("%B %d, %Y"),
        overall_score=f"{dashboard_data['overall_score']:.1f}",
        environmental_score=f"{dashboard_data['esg_scores']['environmental']:.1f}",
        social_score=f"{dashboard_data['esg_scores']['social']:.1f}",
        governance_score=f"{dashboard_data['esg_scores']['governance']:.1f}",
        key_findings_html=key_findings_html,
        priority_actions_html=priority_actions_html
    )
    
    return HTMLResponse(content=html_report)

# Initialize comprehensive sample data route
@api_router.post("/initialize-comprehensive-data")
async def initialize_comprehensive_sample_data():
    """Initialize comprehensive sample data with questions for all canvas sections"""
    
    # Check if comprehensive data already exists
    existing_questions = await db.questions.count_documents({})
    if existing_questions >= 27:  # 3 questions per canvas section (9 sections)
        return {"message": "Comprehensive sample data already exists"}
    
    # Clear existing questions and add comprehensive set
    await db.questions.delete_many({})
    
    comprehensive_questions = [
        # KEY PARTNERSHIPS
        {
            "question_text": "How do you evaluate and select suppliers based on environmental sustainability criteria?",
            "description": "Assess your supplier selection process including environmental impact assessments, certifications, and sustainability commitments.",
            "question_type": "multiple_choice",
            "esg_category": "environmental",
            "canvas_section": "key_partnerships",
            "standard": "GRI",
            "reference_code": "GRI 308-1",
            "options": ["No evaluation process", "Basic environmental checklist", "Comprehensive sustainability assessment", "Third-party certified evaluation", "Integrated ESG partnership strategy"],
            "weight": 1.5
        },
        {
            "question_text": "Do you have partnerships with NGOs or community organizations for social impact initiatives?",
            "description": "Evaluate your collaboration with non-governmental organizations and community groups for social development programs.",
            "question_type": "scale",
            "esg_category": "social",
            "canvas_section": "key_partnerships",
            "standard": "GRI",
            "reference_code": "GRI 413-1",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "No partnerships", "2": "Occasional collaboration", "3": "Regular partnerships", "4": "Strategic alliances", "5": "Integrated partnership ecosystem"},
            "weight": 1.2
        },
        {
            "question_text": "How does your board governance structure incorporate ESG oversight in key partnerships?",
            "description": "Assess the role of board committees in overseeing ESG aspects of strategic partnerships and supplier relationships.",
            "question_type": "text",
            "esg_category": "governance",
            "canvas_section": "key_partnerships",
            "standard": "EFRAG",
            "reference_code": "EFRAG-GOV-3",
            "weight": 1.3
        },
        
        # KEY ACTIVITIES
        {
            "question_text": "What percentage of your core business activities have been assessed for environmental impact?",
            "description": "Quantify the scope of environmental impact assessment across your key business operations and activities.",
            "question_type": "numerical",
            "esg_category": "environmental",
            "canvas_section": "key_activities",
            "standard": "GRI",
            "reference_code": "GRI 103-2",
            "weight": 1.4
        },
        {
            "question_text": "How do you ensure fair labor practices across all key business activities?",
            "description": "Describe your approach to maintaining ethical labor standards, worker rights, and fair employment practices.",
            "question_type": "text",
            "esg_category": "social",
            "canvas_section": "key_activities",
            "standard": "GRI",
            "reference_code": "GRI 401-2",
            "weight": 1.3
        },
        {
            "question_text": "Does your organization have a formal ESG risk management process integrated into key activities?",
            "description": "Evaluate the integration of ESG risk assessment and management into core business operations.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "key_activities",
            "standard": "IFRS",
            "reference_code": "IFRS-RISK-1",
            "weight": 1.6
        },
        
        # KEY RESOURCES
        {
            "question_text": "What is your organization's renewable energy usage as a percentage of total energy consumption?",
            "description": "Measure your progress toward sustainable energy resources and renewable energy adoption.",
            "question_type": "numerical",
            "esg_category": "environmental",
            "canvas_section": "key_resources",
            "standard": "GRI",
            "reference_code": "GRI 302-1",
            "weight": 1.5
        },
        {
            "question_text": "How do you invest in employee development and human capital resources?",
            "description": "Assess your commitment to workforce development, training programs, and human resource investment.",
            "question_type": "multiple_choice",
            "esg_category": "social",
            "canvas_section": "key_resources",
            "standard": "GRI",
            "reference_code": "GRI 404-1",
            "options": ["Minimal training programs", "Basic skills development", "Comprehensive learning initiatives", "Leadership development programs", "Integrated talent management ecosystem"],
            "weight": 1.2
        },
        {
            "question_text": "Rate the effectiveness of your ESG governance infrastructure and resources.",
            "description": "Evaluate the adequacy of governance systems, policies, and resources dedicated to ESG management.",
            "question_type": "scale",
            "esg_category": "governance",
            "canvas_section": "key_resources",
            "standard": "EFRAG",
            "reference_code": "EFRAG-GOV-2",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "Basic compliance only", "2": "Developing infrastructure", "3": "Established systems", "4": "Advanced governance", "5": "Best-in-class ESG infrastructure"},
            "weight": 1.7
        },
        
        # VALUE PROPOSITIONS
        {
            "question_text": "How does your core value proposition contribute to environmental sustainability?",
            "description": "Assess how your products, services, or solutions directly contribute to environmental protection and sustainability goals.",
            "question_type": "multiple_choice",
            "esg_category": "environmental",
            "canvas_section": "value_propositions",
            "standard": "IFRS",
            "reference_code": "IFRS-ENV-3",
            "options": ["No environmental contribution", "Minimal environmental benefits", "Moderate sustainability features", "Significant environmental impact", "Core mission is environmental sustainability"],
            "weight": 1.8
        },
        {
            "question_text": "What social value does your organization create for communities and society?",
            "description": "Describe the positive social impact your organization generates through its core value proposition.",
            "question_type": "text",
            "esg_category": "social",
            "canvas_section": "value_propositions",
            "standard": "GRI",
            "reference_code": "GRI 203-1",
            "weight": 1.4
        },
        {
            "question_text": "Is sustainability integrated as a core component of your business value proposition?",
            "description": "Evaluate whether ESG considerations are fundamental to your business model and value creation.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "value_propositions",
            "standard": "EFRAG",
            "reference_code": "EFRAG-STR-1",
            "weight": 1.6
        },
        
        # CUSTOMER RELATIONSHIPS (Stakeholder Relationships)
        {
            "question_text": "How do you engage stakeholders on environmental concerns and initiatives?",
            "description": "Assess your stakeholder engagement processes regarding environmental issues, concerns, and collaborative initiatives.",
            "question_type": "scale",
            "esg_category": "environmental",
            "canvas_section": "customer_relationships",
            "standard": "GRI",
            "reference_code": "GRI 102-43",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "No engagement", "2": "Reactive communication", "3": "Regular updates", "4": "Active collaboration", "5": "Co-creation partnerships"},
            "weight": 1.3
        },
        {
            "question_text": "Describe your approach to building inclusive customer relationships and community engagement.",
            "description": "Evaluate how you ensure diverse, equitable, and inclusive practices in customer and community relationships.",
            "question_type": "text",
            "esg_category": "social",
            "canvas_section": "customer_relationships",
            "standard": "GRI",
            "reference_code": "GRI 413-2",
            "weight": 1.2
        },
        {
            "question_text": "Do you have transparent reporting mechanisms for stakeholder concerns and grievances?",
            "description": "Assess the availability and effectiveness of channels for stakeholders to raise concerns and provide feedback.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "customer_relationships",
            "standard": "GRI",
            "reference_code": "GRI 102-17",
            "weight": 1.4
        },
        
        # CHANNELS (ESG Communication)
        {
            "question_text": "How effectively do you communicate your environmental performance and initiatives?",
            "description": "Evaluate the quality, frequency, and transparency of your environmental reporting and communication.",
            "question_type": "multiple_choice",
            "esg_category": "environmental",
            "canvas_section": "channels",
            "standard": "GRI",
            "reference_code": "GRI 102-45",
            "options": ["No environmental reporting", "Basic annual disclosure", "Regular sustainability updates", "Comprehensive ESG reporting", "Real-time transparency platform"],
            "weight": 1.1
        },
        {
            "question_text": "What channels do you use to communicate social impact and community engagement?",
            "description": "Assess your communication strategies for sharing social impact stories, community engagement, and stakeholder benefits.",
            "question_type": "text",
            "esg_category": "social",
            "canvas_section": "channels",
            "standard": "GRI",
            "reference_code": "GRI 102-46",
            "weight": 1.0
        },
        {
            "question_text": "Rate the quality and accessibility of your ESG governance communication to stakeholders.",
            "description": "Evaluate how well you communicate governance structures, policies, and decision-making processes to stakeholders.",
            "question_type": "scale",
            "esg_category": "governance",
            "canvas_section": "channels",
            "standard": "EFRAG",
            "reference_code": "EFRAG-COM-1",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "Limited disclosure", "2": "Basic reporting", "3": "Standard communication", "4": "Comprehensive transparency", "5": "Industry-leading disclosure"},
            "weight": 1.2
        },
        
        # CUSTOMER SEGMENTS (Stakeholder Groups)
        {
            "question_text": "How do different stakeholder groups benefit from your environmental initiatives?",
            "description": "Analyze the environmental value and benefits your organization provides to various stakeholder segments.",
            "question_type": "text",
            "esg_category": "environmental",
            "canvas_section": "customer_segments",
            "standard": "GRI",
            "reference_code": "GRI 102-40",
            "weight": 1.1
        },
        {
            "question_text": "What is your approach to identifying and engaging diverse stakeholder groups?",
            "description": "Assess your stakeholder mapping process and engagement strategies for different demographic and interest groups.",
            "question_type": "multiple_choice",
            "esg_category": "social",
            "canvas_section": "customer_segments",
            "standard": "GRI",
            "reference_code": "GRI 102-42",
            "options": ["No formal stakeholder identification", "Basic stakeholder mapping", "Regular stakeholder analysis", "Dynamic stakeholder engagement", "Comprehensive stakeholder ecosystem management"],
            "weight": 1.2
        },
        {
            "question_text": "Do you have different governance communication strategies for different stakeholder segments?",
            "description": "Evaluate whether you tailor governance communication and engagement based on different stakeholder needs and interests.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "customer_segments",
            "standard": "EFRAG",
            "reference_code": "EFRAG-STK-1",
            "weight": 1.0
        },
        
        # COST STRUCTURE (ESG Costs)
        {
            "question_text": "What percentage of your annual budget is allocated to environmental sustainability initiatives?",
            "description": "Quantify your financial commitment to environmental protection, sustainability projects, and green investments.",
            "question_type": "numerical",
            "esg_category": "environmental",
            "canvas_section": "cost_structure",
            "standard": "IFRS",
            "reference_code": "IFRS-INV-1",
            "weight": 1.3
        },
        {
            "question_text": "How do you invest in social programs and community development?",
            "description": "Describe your financial commitments to social initiatives, community programs, and employee welfare investments.",
            "question_type": "scale",
            "esg_category": "social",
            "canvas_section": "cost_structure",
            "standard": "GRI",
            "reference_code": "GRI 201-1",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "Minimal social investment", "2": "Basic compliance costs", "3": "Moderate social programs", "4": "Significant community investment", "5": "Comprehensive social impact budget"},
            "weight": 1.2
        },
        {
            "question_text": "Are ESG-related costs integrated into your strategic financial planning and governance?",
            "description": "Assess whether ESG investments and costs are considered in strategic planning, budgeting, and governance decisions.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "cost_structure",
            "standard": "EFRAG",
            "reference_code": "EFRAG-FIN-1",
            "weight": 1.4
        },
        
        # REVENUE STREAMS (ESG Value & Benefits)
        {
            "question_text": "What percentage of your revenue comes from environmentally sustainable products or services?",
            "description": "Quantify the proportion of your business revenue that is directly tied to environmental sustainability and green solutions.",
            "question_type": "numerical",
            "esg_category": "environmental",
            "canvas_section": "revenue_streams",
            "standard": "IFRS",
            "reference_code": "IFRS-REV-1",
            "weight": 1.6
        },
        {
            "question_text": "How do your social impact initiatives contribute to business value and revenue?",
            "description": "Assess the business case and revenue implications of your social responsibility and community engagement programs.",
            "question_type": "multiple_choice",
            "esg_category": "social",
            "canvas_section": "revenue_streams",
            "standard": "GRI",
            "reference_code": "GRI 203-2",
            "options": ["No measurable business value", "Indirect brand benefits", "Customer loyalty and retention", "New market opportunities", "Direct revenue from social impact products/services"],
            "weight": 1.3
        },
        {
            "question_text": "Do you measure and report the financial returns on ESG investments and governance improvements?",
            "description": "Evaluate your ability to quantify and communicate the financial benefits of ESG initiatives and governance enhancements.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "revenue_streams",
            "standard": "EFRAG",
            "reference_code": "EFRAG-ROI-1",
            "weight": 1.5
        }
    ]
    
    # Insert comprehensive questions
    for q_data in comprehensive_questions:
        question_obj = Question(**q_data)
        question_data = prepare_for_mongo(question_obj.dict())
        await db.questions.insert_one(question_data)
    
    # Create sample organizations with more detail
    sample_orgs = [
        {
            "name": "GreenTech Innovations Corp",
            "industry": "Technology", 
            "size": "Large",
            "country": "United States",
            "headquarters": "San Francisco, CA",
            "website": "https://greentech-innovations.com",
            "employee_count": 2500,
            "annual_revenue": "$500M - $1B",
            "stock_symbol": "GTIC"
        },
        {
            "name": "Sustainable Manufacturing Ltd",
            "industry": "Manufacturing",
            "size": "Medium", 
            "country": "Germany",
            "headquarters": "Munich, Germany",
            "website": "https://sustainable-mfg.de",
            "employee_count": 850,
            "annual_revenue": "$100M - $500M"
        },
        {
            "name": "EcoFinance Solutions",
            "industry": "Financial Services",
            "size": "Enterprise",
            "country": "United Kingdom", 
            "headquarters": "London, UK",
            "website": "https://ecofinance.co.uk",
            "employee_count": 5200,
            "annual_revenue": "$1B+",
            "stock_symbol": "ECFS"
        }
    ]
    
    created_orgs = []
    for org_data in sample_orgs:
        org_obj = Organization(**org_data)
        org_mongo_data = prepare_for_mongo(org_obj.dict())
        await db.organizations.insert_one(org_mongo_data)
        created_orgs.append(org_obj)
    
    return {
        "message": f"Initialized {len(comprehensive_questions)} comprehensive questions across all canvas sections and {len(sample_orgs)} sample organizations with HTML report generation enabled",
        "questions_per_section": 3,
        "total_canvas_sections": 9,
        "organizations_created": len(sample_orgs),
        "esg_categories": ["Environmental", "Social", "Governance"],
        "standards_covered": ["GRI", "EFRAG", "IFRS"],
        "html_reports_available": ["Comprehensive Report", "Executive Summary"]
    }

# HTML Report Generation Routes
@api_router.get("/reports/html/{organization_id}/comprehensive", response_class=HTMLResponse)
async def generate_comprehensive_html_report(organization_id: str):
    """Generate comprehensive HTML report for an organization"""
    
    # Get organization data
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get dashboard data
    dashboard_response = await get_dashboard_data(organization_id)
    questions = await db.questions.find().to_list(1000)
    answers = await db.answers.find({"organization_id": organization_id}).to_list(1000)
    
    # Create answer lookup
    answer_lookup = {a["question_id"]: a for a in answers}
    
    # Generate canvas sections HTML
    canvas_sections_html = ""
    for section_key, section_info in CANVAS_SECTIONS.items():
        completion = dashboard_response["canvas_completion"].get(section_key, {"percentage": 0, "answered": 0, "total": 0})
        
        canvas_sections_html += f"""
        <div class="canvas-section">
            <div class="canvas-title">{section_info['title']}</div>
            <p>{section_info['description']}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {completion['percentage']}%"></div>
            </div>
            <div style="text-align: right; margin-top: 5px; color: #666; font-size: 0.9em;">
                {completion['answered']} of {completion['total']} questions completed ({completion['percentage']:.1f}%)
            </div>
        </div>
        """
    
    # Generate questions HTML
    questions_html = ""
    for question in questions:
        answer = answer_lookup.get(question["id"])
        answered_class = "answered" if answer else ""
        answer_text = str(answer["answer_value"]) if answer else "Not answered"
        
        # Format answer based on question type
        if answer and question["question_type"] == "boolean":
            answer_text = "Yes" if answer["answer_value"] else "No"
        elif answer and question["question_type"] == "scale":
            scale_label = question.get("scale_labels", {}).get(str(answer["answer_value"]), "")
            answer_text = f"{answer['answer_value']} - {scale_label}" if scale_label else str(answer["answer_value"])
        
        questions_html += f"""
        <div class="question-item {answered_class}">
            <div class="question-text">{question['question_text']}</div>
            <div class="question-answer">{answer_text}</div>
            <div class="question-meta">
                <span class="badge {question['esg_category']}">{question['esg_category'].title()}</span>
                <span class="badge standard">{question['standard']}</span>
                {f'<span class="badge standard">{question.get("reference_code", "")}</span>' if question.get("reference_code") else ''}
                <span class="badge standard">Weight: {question['weight']}</span>
            </div>
        </div>
        """
    
    # Generate recommendations HTML
    recommendations = []
    if dashboard_response["esg_scores"]["environmental"] < 70:
        recommendations.append("Focus on environmental sustainability initiatives and partnerships")
    if dashboard_response["esg_scores"]["social"] < 70:
        recommendations.append("Enhance social responsibility programs and community engagement")
    if dashboard_response["esg_scores"]["governance"] < 70:
        recommendations.append("Strengthen governance frameworks and transparency measures")
    if dashboard_response["completion_percentage"] < 100:
        remaining = dashboard_response['total_questions'] - dashboard_response['answered_questions']
        recommendations.append(f"Complete remaining {remaining} questions for comprehensive assessment")
    
    recommendations_html = ""
    for rec in recommendations:
        recommendations_html += f'<div class="recommendation-item">{rec}</div>'
    
    # HTML Template
    html_template = get_comprehensive_html_template()
    
    # Format template
    html_report = html_template.format(
        organization_name=org["name"],
        industry=org.get("industry", "Various"),
        report_date=datetime.now().strftime("%B %d, %Y"),
        overall_score=f"{dashboard_response['overall_score']:.1f}",
        completion_percentage=f"{dashboard_response['completion_percentage']:.0f}",
        answered_questions=dashboard_response["answered_questions"],
        total_questions=dashboard_response["total_questions"],
        environmental_score=f"{dashboard_response['esg_scores']['environmental']:.1f}",
        social_score=f"{dashboard_response['esg_scores']['social']:.1f}",
        governance_score=f"{dashboard_response['esg_scores']['governance']:.1f}",
        canvas_sections_html=canvas_sections_html,
        questions_html=questions_html,
        recommendations_html=recommendations_html
    )
    
    return HTMLResponse(content=html_report)

@api_router.get("/reports/html/{organization_id}/executive", response_class=HTMLResponse)
async def generate_executive_summary_html(organization_id: str):
    """Generate executive summary HTML report for an organization"""
    
    # Get organization data
    org = await db.organizations.find_one({"id": organization_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get dashboard data
    dashboard_response = await get_dashboard_data(organization_id)
    
    # Generate key findings
    key_findings = []
    if dashboard_response["esg_scores"]["environmental"] >= 80:
        key_findings.append("Strong environmental performance with comprehensive sustainability practices")
    elif dashboard_response["esg_scores"]["environmental"] >= 60:
        key_findings.append("Moderate environmental performance with room for improvement in sustainability initiatives")
    else:
        key_findings.append("Environmental performance requires significant attention and investment")
    
    if dashboard_response["overall_score"] >= 75:
        key_findings.append("Above-average overall ESG performance demonstrates commitment to sustainability")
    else:
        key_findings.append("ESG performance is below industry standards and requires strategic improvement")
    
    key_findings_html = ""
    for finding in key_findings:
        key_findings_html += f'<div class="finding-item">{finding}</div>'
    
    # Generate priority actions
    priority_actions = []
    esg_scores = dashboard_response["esg_scores"]
    lowest_score = min(esg_scores, key=esg_scores.get)
    priority_actions.append(f"Prioritize improvements in {lowest_score} performance")
    priority_actions.append("Complete comprehensive ESG assessment for detailed insights")
    priority_actions.append("Develop ESG strategy aligned with business objectives")
    
    priority_actions_html = ""
    for action in priority_actions:
        priority_actions_html += f'<div class="recommendation-item">{action}</div>'
    
    # HTML Template
    html_template = get_executive_summary_template()
    
    # Format template
    html_report = html_template.format(
        organization_name=org["name"],
        report_date=datetime.now().strftime("%B %d, %Y"),
        overall_score=f"{dashboard_response['overall_score']:.1f}",
        environmental_score=f"{dashboard_response['esg_scores']['environmental']:.1f}",
        social_score=f"{dashboard_response['esg_scores']['social']:.1f}",
        governance_score=f"{dashboard_response['esg_scores']['governance']:.1f}",
        key_findings_html=key_findings_html,
        priority_actions_html=priority_actions_html
    )
    
    return HTMLResponse(content=html_report)

# HTML Template Functions
def get_comprehensive_html_template():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG Comprehensive Report - {organization_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px; margin: 0 auto; padding: 20px; background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; text-align: center; margin: -20px -20px 40px -20px;
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 0; font-size: 1.2em; opacity: 0.9; }}
        .report-meta {{
            background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;
        }}
        .meta-item {{ text-align: center; }}
        .meta-label {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
        .meta-value {{ font-size: 1.4em; font-weight: bold; color: #333; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 1.8em; color: #333; border-bottom: 3px solid #667eea;
            padding-bottom: 10px; margin-bottom: 25px;
        }}
        .esg-scores {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }}
        .score-card {{
            background: white; border-radius: 12px; padding: 25px; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid;
        }}
        .score-card.environmental {{ border-left-color: #10b981; }}
        .score-card.social {{ border-left-color: #3b82f6; }}
        .score-card.governance {{ border-left-color: #8b5cf6; }}
        .score-title {{ font-size: 1.1em; color: #666; margin-bottom: 10px; }}
        .score-value {{ font-size: 3em; font-weight: bold; color: #333; margin-bottom: 10px; }}
        .score-bar {{ height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }}
        .score-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s ease; }}
        .score-fill.environmental {{ background: linear-gradient(90deg, #10b981, #34d399); }}
        .score-fill.social {{ background: linear-gradient(90deg, #3b82f6, #60a5fa); }}
        .score-fill.governance {{ background: linear-gradient(90deg, #8b5cf6, #a78bfa); }}
        .canvas-section {{
            background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;
        }}
        .canvas-title {{ font-size: 1.3em; font-weight: bold; color: #333; margin-bottom: 15px; }}
        .progress-bar {{ height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; margin-bottom: 10px; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 3px; }}
        .question-item {{
            background: white; border-radius: 8px; padding: 15px; margin-bottom: 15px;
            border-left: 4px solid #e5e7eb;
        }}
        .question-item.answered {{ border-left-color: #10b981; }}
        .question-text {{ font-weight: 600; color: #333; margin-bottom: 8px; }}
        .question-answer {{ color: #666; font-style: italic; }}
        .question-meta {{ margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 500; }}
        .badge.environmental {{ background: #dcfce7; color: #166534; }}
        .badge.social {{ background: #dbeafe; color: #1e40af; }}
        .badge.governance {{ background: #e9d5ff; color: #7c2d12; }}
        .badge.standard {{ background: #f3f4f6; color: #374151; }}
        .recommendations {{
            background: #fef3c7; border-left: 5px solid #f59e0b; padding: 20px;
            border-radius: 8px; margin-bottom: 30px;
        }}
        .recommendations h3 {{ color: #92400e; margin-bottom: 15px; }}
        .recommendation-item {{ margin-bottom: 10px; padding-left: 20px; position: relative; }}
        .recommendation-item:before {{ content: "•"; position: absolute; left: 0; color: #f59e0b; font-weight: bold; }}
        .footer {{
            margin-top: 50px; padding-top: 30px; border-top: 2px solid #e5e7eb;
            text-align: center; color: #666;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; margin: 0; padding: 0; }}
            .header {{ margin: 0 0 40px 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESG Sustainability Report</h1>
            <p>{organization_name} • {industry} • {report_date}</p>
        </div>
        <div class="report-meta">
            <div class="meta-item">
                <div class="meta-label">Overall ESG Score</div>
                <div class="meta-value">{overall_score}/100</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Assessment Progress</div>
                <div class="meta-value">{completion_percentage}%</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Questions Answered</div>
                <div class="meta-value">{answered_questions}/{total_questions}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Report Generated</div>
                <div class="meta-value">{report_date}</div>
            </div>
        </div>
        <div class="section">
            <h2 class="section-title">ESG Performance Overview</h2>
            <div class="esg-scores">
                <div class="score-card environmental">
                    <div class="score-title">Environmental Score</div>
                    <div class="score-value">{environmental_score}</div>
                    <div class="score-bar">
                        <div class="score-fill environmental" style="width: {environmental_score}%"></div>
                    </div>
                    <p>Sustainability & Environmental Impact</p>
                </div>
                <div class="score-card social">
                    <div class="score-title">Social Score</div>
                    <div class="score-value">{social_score}</div>
                    <div class="score-bar">
                        <div class="score-fill social" style="width: {social_score}%"></div>
                    </div>
                    <p>Social Responsibility & Community Impact</p>
                </div>
                <div class="score-card governance">
                    <div class="score-title">Governance Score</div>
                    <div class="score-value">{governance_score}</div>
                    <div class="score-bar">
                        <div class="score-fill governance" style="width: {governance_score}%"></div>
                    </div>
                    <p>Corporate Governance & Ethics</p>
                </div>
            </div>
        </div>
        <div class="section">
            <h2 class="section-title">Canvas Section Analysis</h2>
            {canvas_sections_html}
        </div>
        <div class="section">
            <h2 class="section-title">Detailed Assessment Responses</h2>
            {questions_html}
        </div>
        <div class="recommendations">
            <h3>Key Recommendations</h3>
            {recommendations_html}
        </div>
        <div class="footer">
            <p><strong>ESG Canvas Reporter</strong> - Advanced Sustainability Analytics Platform</p>
            <p>Report generated on {report_date} • Based on GRI, EFRAG, and IFRS standards</p>
        </div>
    </div>
</body>
</html>"""

def get_executive_summary_template():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG Executive Summary - {organization_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333; margin: 0; padding: 20px; background: white;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            text-align: center; margin-bottom: 40px; padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        .header h1 {{ color: #667eea; margin-bottom: 10px; }}
        .executive-summary {{
            background: #f8f9fa; padding: 30px; border-radius: 12px; margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }}
        .summary-card {{
            background: white; padding: 20px; border-radius: 8px; text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-score {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .summary-score.environmental {{ color: #10b981; }}
        .summary-score.social {{ color: #3b82f6; }}
        .summary-score.governance {{ color: #8b5cf6; }}
        .summary-score.overall {{ color: #667eea; }}
        .key-findings {{ margin-bottom: 30px; }}
        .finding-item {{
            margin-bottom: 15px; padding: 15px; background: #f8f9fa;
            border-radius: 8px; border-left: 4px solid #667eea;
        }}
        .priority-actions {{
            background: #fef3c7; padding: 20px; border-radius: 8px; border-left: 5px solid #f59e0b;
        }}
        .recommendation-item {{ margin-bottom: 10px; padding-left: 20px; position: relative; }}
        .recommendation-item:before {{ content: "•"; position: absolute; left: 0; color: #f59e0b; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESG Executive Summary</h1>
            <h2>{organization_name}</h2>
            <p>{report_date}</p>
        </div>
        <div class="executive-summary">
            <h3>Executive Overview</h3>
            <p>This executive summary provides a high-level overview of {organization_name}'s ESG performance based on our comprehensive sustainability assessment using business model canvas methodology and international standards (GRI, EFRAG, IFRS).</p>
        </div>
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-score overall">{overall_score}</div>
                <h4>Overall ESG Score</h4>
                <p>Out of 100</p>
            </div>
            <div class="summary-card">
                <div class="summary-score environmental">{environmental_score}</div>
                <h4>Environmental</h4>
                <p>Sustainability Impact</p>
            </div>
            <div class="summary-card">
                <div class="summary-score social">{social_score}</div>
                <h4>Social</h4>
                <p>Community & Stakeholders</p>
            </div>
            <div class="summary-card">
                <div class="summary-score governance">{governance_score}</div>
                <h4>Governance</h4>
                <p>Ethics & Management</p>
            </div>
        </div>
        <div class="key-findings">
            <h3>Key Findings</h3>
            {key_findings_html}
        </div>
        <div class="priority-actions">
            <h3>Priority Actions</h3>
            {priority_actions_html}
        </div>
    </div>
</body>
</html>"""

# Canvas section definitions
CANVAS_SECTIONS = {
    "key_partnerships": {"title": "Key Partnerships", "description": "Sustainability partnerships and supplier relationships"},
    "key_activities": {"title": "Key Activities", "description": "Core ESG activities and environmental practices"},
    "key_resources": {"title": "Key Resources", "description": "ESG governance, policies, and sustainable resources"},
    "value_propositions": {"title": "Value Propositions", "description": "ESG value creation and sustainability benefits"},
    "customer_relationships": {"title": "Stakeholder Relationships", "description": "Community engagement and stakeholder management"},
    "channels": {"title": "ESG Communication", "description": "Sustainability reporting and communication channels"},
    "customer_segments": {"title": "Stakeholder Groups", "description": "Different stakeholder segments and their ESG interests"},
    "cost_structure": {"title": "ESG Costs", "description": "Sustainability investments and ESG-related costs"},
    "revenue_streams": {"title": "ESG Value & Benefits", "description": "Revenue and benefits from ESG initiatives"}
}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()