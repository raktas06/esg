import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { BarChart, Building2, Users, Leaf, Scale, Target, ArrowRight, CheckCircle, AlertCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Canvas section definitions for ESG
const CANVAS_SECTIONS = {
  key_partnerships: {
    title: "Key Partnerships",
    description: "Sustainability partnerships and supplier relationships",
    icon: <Users className="h-5 w-5" />,
    color: "from-emerald-500 to-teal-600"
  },
  key_activities: {
    title: "Key Activities", 
    description: "Core ESG activities and environmental practices",
    icon: <Target className="h-5 w-5" />,
    color: "from-blue-500 to-cyan-600"
  },
  key_resources: {
    title: "Key Resources",
    description: "ESG governance, policies, and sustainable resources",
    icon: <Building2 className="h-5 w-5" />,
    color: "from-purple-500 to-indigo-600"
  },
  value_propositions: {
    title: "Value Propositions",
    description: "ESG value creation and sustainability benefits",
    icon: <Scale className="h-5 w-5" />,
    color: "from-orange-500 to-red-500"
  },
  customer_relationships: {
    title: "Stakeholder Relationships",
    description: "Community engagement and stakeholder management",
    icon: <Users className="h-5 w-5" />,
    color: "from-green-500 to-emerald-600"
  },
  channels: {
    title: "ESG Communication",
    description: "Sustainability reporting and communication channels",
    icon: <BarChart className="h-5 w-5" />,
    color: "from-pink-500 to-rose-600"
  },
  customer_segments: {
    title: "Stakeholder Groups",
    description: "Different stakeholder segments and their ESG interests",
    icon: <Users className="h-5 w-5" />,
    color: "from-violet-500 to-purple-600"
  },
  cost_structure: {
    title: "ESG Costs",
    description: "Sustainability investments and ESG-related costs",
    icon: <BarChart className="h-5 w-5" />,
    color: "from-amber-500 to-orange-600"
  },
  revenue_streams: {
    title: "ESG Value & Benefits",
    description: "Revenue and benefits from ESG initiatives",
    icon: <Target className="h-5 w-5" />,
    color: "from-teal-500 to-cyan-600"
  }
};

const ESG_CATEGORIES = {
  environmental: { label: "Environmental", color: "bg-green-100 text-green-800", icon: <Leaf className="h-4 w-4" /> },
  social: { label: "Social", color: "bg-blue-100 text-blue-800", icon: <Users className="h-4 w-4" /> },
  governance: { label: "Governance", color: "bg-purple-100 text-purple-800", icon: <Scale className="h-4 w-4" /> }
};

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [organizations, setOrganizations] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [assessments, setAssessments] = useState([]);
  const [canvasProgress, setCanvasProgress] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedCanvasSection, setSelectedCanvasSection] = useState(null);

  // New organization form
  const [newOrgForm, setNewOrgForm] = useState({
    name: '',
    industry: '',
    size: '',
    country: ''
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      // Initialize sample data
      await axios.post(`${API}/initialize-sample-data`);
      
      // Load organizations
      await loadOrganizations();
      
      // Load questions
      await loadQuestions();
    } catch (error) {
      console.error('Error initializing app:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOrganizations = async () => {
    try {
      const response = await axios.get(`${API}/organizations`);
      setOrganizations(response.data);
      if (response.data.length > 0 && !selectedOrg) {
        setSelectedOrg(response.data[0]);
        loadAssessments(response.data[0].id);
      }
    } catch (error) {
      console.error('Error loading organizations:', error);
    }
  };

  const loadQuestions = async () => {
    try {
      const response = await axios.get(`${API}/questions`);
      setQuestions(response.data);
    } catch (error) {
      console.error('Error loading questions:', error);
    }
  };

  const loadAssessments = async (orgId) => {
    try {
      const response = await axios.get(`${API}/assessments?organization_id=${orgId}`);
      setAssessments(response.data);
      
      if (response.data.length === 0) {
        // Create a default assessment
        await createAssessment(orgId, "ESG Canvas Assessment", "Comprehensive ESG assessment using business model canvas approach");
      }
    } catch (error) {
      console.error('Error loading assessments:', error);
    }
  };

  const createAssessment = async (orgId, name, description) => {
    try {
      const response = await axios.post(`${API}/assessments`, {
        organization_id: orgId,
        name,
        description
      });
      setAssessments([response.data]);
      return response.data;
    } catch (error) {
      console.error('Error creating assessment:', error);
    }
  };

  const loadCanvasProgress = async (assessmentId) => {
    try {
      const response = await axios.get(`${API}/assessments/${assessmentId}/progress`);
      setCanvasProgress(response.data.progress);
    } catch (error) {
      console.error('Error loading canvas progress:', error);
    }
  };

  const loadAnswers = async (orgId) => {
    try {
      const response = await axios.get(`${API}/answers?organization_id=${orgId}`);
      const answersMap = {};
      response.data.forEach(answer => {
        answersMap[answer.question_id] = answer;
      });
      setAnswers(answersMap);
    } catch (error) {
      console.error('Error loading answers:', error);
    }
  };

  const createOrganization = async () => {
    try {
      const response = await axios.post(`${API}/organizations`, newOrgForm);
      setOrganizations([...organizations, response.data]);
      setSelectedOrg(response.data);
      setNewOrgForm({ name: '', industry: '', size: '', country: '' });
      setCurrentView('dashboard');
      await loadAssessments(response.data.id);
    } catch (error) {
      console.error('Error creating organization:', error);
    }
  };

  const saveAnswer = async (questionId, value, comments = '') => {
    if (!selectedOrg) return;
    
    try {
      await axios.post(`${API}/answers`, {
        question_id: questionId,
        organization_id: selectedOrg.id,
        answer_value: value,
        comments
      });
      
      // Reload answers and progress
      await loadAnswers(selectedOrg.id);
      if (assessments.length > 0) {
        await loadCanvasProgress(assessments[0].id);
      }
    } catch (error) {
      console.error('Error saving answer:', error);
    }
  };

  useEffect(() => {
    if (selectedOrg) {
      loadAnswers(selectedOrg.id);
      if (assessments.length > 0) {
        loadCanvasProgress(assessments[0].id);
      }
    }
  }, [selectedOrg, assessments]);

  const renderCanvasSection = (sectionKey) => {
    const section = CANVAS_SECTIONS[sectionKey];
    const sectionQuestions = questions.filter(q => q.canvas_section === sectionKey);
    const progress = canvasProgress[sectionKey] || 0;
    
    return (
      <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-gray-300" 
            onClick={() => setSelectedCanvasSection(sectionKey)}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`p-2 rounded-lg bg-gradient-to-r ${section.color} text-white`}>
                {section.icon}
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">{section.title}</CardTitle>
                <CardDescription className="text-sm">{section.description}</CardDescription>
              </div>
            </div>
            <Badge variant="outline" className="text-xs">
              {sectionQuestions.length} questions
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span className="font-medium">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
            {progress === 100 && (
              <div className="flex items-center text-green-600 text-sm">
                <CheckCircle className="h-4 w-4 mr-1" />
                Complete
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderQuestion = (question) => {
    const answer = answers[question.id];
    const esgCategory = ESG_CATEGORIES[question.esg_category];
    
    return (
      <Card key={question.id} className="mb-4">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-base mb-2">{question.question_text}</CardTitle>
              {question.description && (
                <CardDescription className="mb-3">{question.description}</CardDescription>
              )}
              <div className="flex items-center space-x-2">
                <Badge className={esgCategory.color}>
                  {esgCategory.icon}
                  <span className="ml-1">{esgCategory.label}</span>
                </Badge>
                <Badge variant="outline">{question.standard}</Badge>
                {question.reference_code && (
                  <Badge variant="secondary">{question.reference_code}</Badge>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {question.question_type === 'text' && (
            <Textarea 
              placeholder="Enter your response..."
              value={answer?.answer_value || ''}
              onChange={(e) => saveAnswer(question.id, e.target.value)}
              className="min-h-[100px]"
            />
          )}
          
          {question.question_type === 'numerical' && (
            <Input 
              type="number"
              placeholder="Enter numerical value"
              value={answer?.answer_value || ''}
              onChange={(e) => saveAnswer(question.id, parseFloat(e.target.value) || 0)}
            />
          )}
          
          {question.question_type === 'boolean' && (
            <Select value={answer?.answer_value?.toString() || ''} onValueChange={(value) => saveAnswer(question.id, value === 'true')}>
              <SelectTrigger>
                <SelectValue placeholder="Select Yes/No" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="true">Yes</SelectItem>
                <SelectItem value="false">No</SelectItem>
              </SelectContent>
            </Select>
          )}
          
          {question.question_type === 'multiple_choice' && question.options && (
            <Select value={answer?.answer_value || ''} onValueChange={(value) => saveAnswer(question.id, value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                {question.options.map((option, index) => (
                  <SelectItem key={index} value={option}>{option}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          
          {question.question_type === 'scale' && (
            <div className="space-y-3">
              <Select value={answer?.answer_value?.toString() || ''} onValueChange={(value) => saveAnswer(question.id, parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder={`Select scale (${question.scale_min}-${question.scale_max})`} />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({length: question.scale_max - question.scale_min + 1}, (_, i) => {
                    const value = question.scale_min + i;
                    const label = question.scale_labels?.[value] || value.toString();
                    return (
                      <SelectItem key={value} value={value.toString()}>
                        {value} - {label}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
          )}
          
          {answer && (
            <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center text-green-700 text-sm">
                <CheckCircle className="h-4 w-4 mr-1" />
                Answer saved
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ESG Reporting System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                  <BarChart className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">ESG Canvas Reporter</h1>
                  <p className="text-sm text-gray-500">Sustainability Reporting Platform</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {selectedOrg && (
                <div className="flex items-center space-x-2">
                  <Building2 className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">{selectedOrg.name}</span>
                </div>
              )}
              
              <Select value={selectedOrg?.id || ''} onValueChange={(value) => {
                const org = organizations.find(o => o.id === value);
                setSelectedOrg(org);
                if (org) loadAssessments(org.id);
              }}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select Organization" />
                </SelectTrigger>
                <SelectContent>
                  {organizations.map(org => (
                    <SelectItem key={org.id} value={org.id}>{org.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Add Organization</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create New Organization</DialogTitle>
                    <DialogDescription>Add a new organization to start ESG reporting.</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="orgName">Organization Name</Label>
                      <Input 
                        id="orgName"
                        value={newOrgForm.name}
                        onChange={(e) => setNewOrgForm({...newOrgForm, name: e.target.value})}
                        placeholder="Enter organization name"
                      />
                    </div>
                    <div>
                      <Label htmlFor="industry">Industry</Label>
                      <Input 
                        id="industry"
                        value={newOrgForm.industry}
                        onChange={(e) => setNewOrgForm({...newOrgForm, industry: e.target.value})}
                        placeholder="e.g., Technology, Manufacturing"
                      />
                    </div>
                    <div>
                      <Label htmlFor="size">Organization Size</Label>
                      <Select value={newOrgForm.size} onValueChange={(value) => setNewOrgForm({...newOrgForm, size: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select size" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Small">Small (1-50 employees)</SelectItem>
                          <SelectItem value="Medium">Medium (51-250 employees)</SelectItem>
                          <SelectItem value="Large">Large (251-1000 employees)</SelectItem>
                          <SelectItem value="Enterprise">Enterprise (1000+ employees)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="country">Country</Label>
                      <Input 
                        id="country"
                        value={newOrgForm.country}
                        onChange={(e) => setNewOrgForm({...newOrgForm, country: e.target.value})}
                        placeholder="e.g., United States"
                      />
                    </div>
                    <Button onClick={createOrganization} className="w-full">Create Organization</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!selectedOrg ? (
          <div className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Organization Selected</h3>
            <p className="text-gray-500 mb-4">Please select or create an organization to start ESG reporting.</p>
          </div>
        ) : (
          <Tabs value={currentView} onValueChange={setCurrentView}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="dashboard">ESG Canvas</TabsTrigger>
              <TabsTrigger value="assessment">Assessment</TabsTrigger>
              <TabsTrigger value="reports">Reports</TabsTrigger>
            </TabsList>
            
            <TabsContent value="dashboard" className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">ESG Business Model Canvas</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Comprehensive sustainability assessment using business model canvas approach with GRI, EFRAG, and IFRS standards
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.keys(CANVAS_SECTIONS).map(sectionKey => renderCanvasSection(sectionKey))}
              </div>
            </TabsContent>
            
            <TabsContent value="assessment" className="space-y-6">
              {selectedCanvasSection ? (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <Button variant="outline" onClick={() => setSelectedCanvasSection(null)}>
                        ← Back to Canvas
                      </Button>
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                          {CANVAS_SECTIONS[selectedCanvasSection].title}
                        </h2>
                        <p className="text-gray-600">
                          {CANVAS_SECTIONS[selectedCanvasSection].description}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {questions
                      .filter(q => q.canvas_section === selectedCanvasSection)
                      .map(question => renderQuestion(question))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Canvas Section</h3>
                  <p className="text-gray-500 mb-4">Choose a canvas section from the dashboard to start the assessment.</p>
                  <Button onClick={() => setCurrentView('dashboard')}>
                    Go to ESG Canvas
                  </Button>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="reports" className="space-y-6">
              <div className="text-center py-12">
                <BarChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Reports & Analytics</h3>
                <p className="text-gray-500 mb-4">Comprehensive ESG reporting and analytics (Coming Soon)</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
                  {Object.entries(canvasProgress).map(([section, progress]) => (
                    <Card key={section}>
                      <CardContent className="p-4">
                        <div className="text-center">
                          <h4 className="font-medium text-gray-900 mb-2">
                            {CANVAS_SECTIONS[section]?.title}
                          </h4>
                          <div className="text-2xl font-bold text-blue-600 mb-2">
                            {Math.round(progress)}%
                          </div>
                          <Progress value={progress} className="h-2" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  );
}

export default App;