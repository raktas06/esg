from fastapi import FastAPI, APIRouter, HTTPException
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

# Models
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
    scale_labels: Optional[Dict[int, str]] = None
    is_required: bool = True

class Answer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    organization_id: str
    user_id: str
    answer_value: Any  # Can be string, number, boolean, list
    comments: Optional[str] = None
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrganizationCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    country: Optional[str] = None

class Assessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, draft
    progress: Dict[CanvasSection, float] = {}  # percentage completion per section
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssessmentCreate(BaseModel):
    organization_id: str
    name: str
    description: Optional[str] = None

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data, dict):
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data and isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        if 'created_at' in item and isinstance(item['created_at'], str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
        if 'updated_at' in item and isinstance(item['updated_at'], str):
            item['updated_at'] = datetime.fromisoformat(item['updated_at'])
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "ESG Reporting API"}

# Organization routes
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

# Assessment routes
@api_router.post("/assessments", response_model=Assessment)
async def create_assessment(input: AssessmentCreate):
    assessment_dict = input.dict()
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

# Answer routes
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

# Canvas progress route
@api_router.get("/assessments/{assessment_id}/progress")
async def get_assessment_progress(assessment_id: str):
    # Get assessment
    assessment = await db.assessments.find_one({"id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Calculate progress for each canvas section
    progress = {}
    for section in CanvasSection:
        # Get questions for this canvas section
        questions = await db.questions.find({"canvas_section": section}).to_list(1000)
        total_questions = len(questions)
        
        if total_questions == 0:
            progress[section.value] = 0
        else:
            # Get answered questions for this organization and canvas section
            question_ids = [q["id"] for q in questions]
            answered = await db.answers.find({
                "organization_id": assessment["organization_id"],
                "question_id": {"$in": question_ids}
            }).to_list(1000)
            
            progress[section.value] = (len(answered) / total_questions) * 100
    
    return {"assessment_id": assessment_id, "progress": progress}

# Initialize sample data route
@api_router.post("/initialize-sample-data")
async def initialize_sample_data():
    # Check if we have all sample questions (should be 5)
    existing_questions = await db.questions.count_documents({})
    if existing_questions >= 5:
        return {"message": "Sample data already exists"}
    
    # Sample questions based on GRI, EFRAG, IFRS standards
    sample_questions = [
        # Environmental - Key Partnerships
        {
            "question_text": "Does your organization have partnerships with suppliers that demonstrate environmental sustainability commitments?",
            "description": "Evaluate partnerships with suppliers regarding environmental criteria and sustainability commitments.",
            "question_type": "scale",
            "esg_category": "environmental",
            "canvas_section": "key_partnerships",
            "standard": "GRI",
            "reference_code": "GRI 308-1",
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {"1": "No partnerships", "2": "Few partnerships", "3": "Some partnerships", "4": "Most partnerships", "5": "All partnerships"}
        },
        # Environmental - Key Activities
        {
            "question_text": "What percentage of your organization's activities are designed to minimize environmental impact?",
            "description": "Assess the proportion of business activities that incorporate environmental considerations.",
            "question_type": "numerical",
            "esg_category": "environmental",
            "canvas_section": "key_activities",
            "standard": "GRI",
            "reference_code": "GRI 103-2"
        },
        # Social - Customer Relationships
        {
            "question_text": "How does your organization engage with local communities affected by your operations?",
            "description": "Describe community engagement practices and stakeholder relationship management.",
            "question_type": "text",
            "esg_category": "social",
            "canvas_section": "customer_relationships",
            "standard": "GRI",
            "reference_code": "GRI 413-1"
        },
        # Governance - Key Resources
        {
            "question_text": "Does your organization have a dedicated sustainability or ESG governance structure?",
            "description": "Evaluate the presence and effectiveness of ESG governance mechanisms.",
            "question_type": "boolean",
            "esg_category": "governance",
            "canvas_section": "key_resources",
            "standard": "EFRAG",
            "reference_code": "EFRAG-GOV-1"
        },
        # Environmental - Value Propositions
        {
            "question_text": "How does your organization's value proposition incorporate environmental benefits?",
            "description": "Assess how environmental considerations are integrated into the core value proposition.",
            "question_type": "multiple_choice",
            "esg_category": "environmental",
            "canvas_section": "value_propositions",
            "standard": "IFRS",
            "reference_code": "IFRS-ENV-2",
            "options": ["No environmental benefits", "Minimal environmental benefits", "Moderate environmental benefits", "Significant environmental benefits", "Core environmental focus"]
        }
    ]
    
    # Insert sample questions
    for q_data in sample_questions:
        question_obj = Question(**q_data)
        question_data = prepare_for_mongo(question_obj.dict())
        await db.questions.insert_one(question_data)
    
    # Create a sample organization
    sample_org = Organization(name="Sample Corporation", industry="Technology", size="Medium", country="United States")
    org_data = prepare_for_mongo(sample_org.dict())
    await db.organizations.insert_one(org_data)
    
    return {"message": f"Initialized {len(sample_questions)} sample questions and 1 sample organization"}

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