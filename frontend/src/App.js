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
import { BarChart, Building2, Users, Leaf, Scale, Target, ArrowRight, CheckCircle, AlertCircle, TrendingUp, Download, FileText, PieChart, Activity, Award, Calendar, Globe, DollarSign } from "lucide-react";
import { 
  ResponsiveContainer, 
  BarChart as RechartsBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  PieChart as RechartsPieChart,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced color palette for charts
const COLORS = {
  environmental: '#10b981',
  social: '#3b82f6', 
  governance: '#8b5cf6',
  primary: '#6366f1',
  secondary: '#ec4899',
  accent: '#f59e0b',
  success: '#22c55e',
  warning: '#eab308',
  danger: '#ef4444'
};

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444'];

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
    icon: <DollarSign className="h-5 w-5" />,
    color: "from-amber-500 to-orange-600"
  },
  revenue_streams: {
    title: "ESG Value & Benefits",
    description: "Revenue and benefits from ESG initiatives",
    icon: <TrendingUp className="h-5 w-5" />,
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
  const [dashboardData, setDashboardData] = useState(null);
  const [benchmarkingData, setBenchmarkingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedCanvasSection, setSelectedCanvasSection] = useState(null);

  // New organization form
  const [newOrgForm, setNewOrgForm] = useState({
    name: '',
    industry: '',
    size: '',
    country: '',
    headquarters: '',
    website: '',
    employee_count: '',
    annual_revenue: '',
    stock_symbol: ''
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      // Initialize comprehensive sample data
      await axios.post(`${API}/initialize-comprehensive-data`);
      
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
        await loadAssessments(response.data[0].id);
        await loadDashboardData(response.data[0].id);
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

  const loadDashboardData = async (orgId) => {
    try {
      const [dashboardResponse, benchmarkResponse] = await Promise.all([
        axios.get(`${API}/reports/dashboard/${orgId}`),
        axios.get(`${API}/reports/benchmarking/${orgId}`)
      ]);
      
      setDashboardData(dashboardResponse.data);
      setBenchmarkingData(benchmarkResponse.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
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
      const orgData = { ...newOrgForm };
      if (orgData.employee_count) {
        orgData.employee_count = parseInt(orgData.employee_count);
      }
      
      const response = await axios.post(`${API}/organizations`, orgData);
      setOrganizations([...organizations, response.data]);
      setSelectedOrg(response.data);
      setNewOrgForm({ 
        name: '', industry: '', size: '', country: '', headquarters: '', 
        website: '', employee_count: '', annual_revenue: '', stock_symbol: '' 
      });
      setCurrentView('dashboard');
      await loadAssessments(response.data.id);
      await loadDashboardData(response.data.id);
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
      
      // Reload answers, progress, and dashboard data
      await loadAnswers(selectedOrg.id);
      if (assessments.length > 0) {
        await loadCanvasProgress(assessments[0].id);
      }
      await loadDashboardData(selectedOrg.id);
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

  // Dashboard Components
  const ESGScoreCard = ({ title, score, icon, color, trend }) => (
    <Card className="relative overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`p-2 rounded-lg ${color}`}>
              {icon}
            </div>
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
          </div>
          {trend && (
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +{trend}%
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">
          {score.toFixed(1)}
        </div>
        <div className="text-xs text-gray-500">out of 100</div>
        <Progress value={score} className="mt-2 h-2" />
      </CardContent>
    </Card>
  );

  const KPICard = ({ title, value, subtitle, icon, trend }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900">{value}</p>
            <p className="text-xs text-gray-500">{subtitle}</p>
          </div>
          <div className="text-gray-400">
            {icon}
          </div>
        </div>
        {trend && (
          <div className="mt-4 flex items-center text-sm text-green-600">
            <TrendingUp className="h-4 w-4 mr-1" />
            {trend} from last assessment
          </div>
        )}
      </CardContent>
    </Card>
  );

  const renderAdvancedDashboard = () => {
    if (!dashboardData) {
      return (
        <div className="text-center py-12">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Loading Dashboard Data</h3>
          <p className="text-gray-500">Please wait while we load your ESG analytics...</p>
        </div>
      );
    }

    // Prepare chart data
    const esgScoreData = [
      { name: 'Environmental', score: dashboardData.esg_scores.environmental, fill: COLORS.environmental },
      { name: 'Social', score: dashboardData.esg_scores.social, fill: COLORS.social },
      { name: 'Governance', score: dashboardData.esg_scores.governance, fill: COLORS.governance }
    ];

    const canvasProgressData = Object.entries(dashboardData.canvas_completion).map(([key, value]) => ({
      name: CANVAS_SECTIONS[key]?.title || key,
      progress: value.percentage,
      answered: value.answered,
      total: value.total
    }));

    const comparisonData = benchmarkingData ? [
      { 
        category: 'Environmental', 
        organization: benchmarkingData.organization_scores.environmental,
        industry: benchmarkingData.industry_averages.environmental
      },
      { 
        category: 'Social', 
        organization: benchmarkingData.organization_scores.social,
        industry: benchmarkingData.industry_averages.social
      },
      { 
        category: 'Governance', 
        organization: benchmarkingData.organization_scores.governance,
        industry: benchmarkingData.industry_averages.governance
      }
    ] : [];

    return (
      <div className="space-y-8">
        {/* Header Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">ESG Analytics Dashboard</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Comprehensive sustainability performance metrics and insights for {selectedOrg?.name}
          </p>
        </div>

        {/* KPI Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Overall ESG Score"
            value={dashboardData.overall_score.toFixed(1)}
            subtitle="Out of 100"
            icon={<Award className="h-8 w-8" />}
            trend="+5.2 points"
          />
          <KPICard
            title="Assessment Progress"
            value={`${dashboardData.completion_percentage.toFixed(0)}%`}
            subtitle={`${dashboardData.answered_questions}/${dashboardData.total_questions} questions`}
            icon={<CheckCircle className="h-8 w-8" />}
            trend="+12% completed"
          />
          <KPICard
            title="Active Assessments"
            value={dashboardData.assessments_count}
            subtitle="Current evaluations"
            icon={<FileText className="h-8 w-8" />}
          />
          <KPICard
            title="Industry Ranking"
            value={benchmarkingData ? "Top 25%" : "N/A"}
            subtitle={benchmarkingData ? `vs ${benchmarkingData.peer_count} peers` : "Insufficient data"}
            icon={<TrendingUp className="h-8 w-8" />}
            trend="↑ 3 positions"
          />
        </div>

        {/* ESG Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ESGScoreCard
            title="Environmental Score"
            score={dashboardData.esg_scores.environmental}
            icon={<Leaf className="h-5 w-5 text-white" />}
            color="bg-gradient-to-r from-green-500 to-emerald-600 text-white"
            trend={2.3}
          />
          <ESGScoreCard
            title="Social Score"
            score={dashboardData.esg_scores.social}
            icon={<Users className="h-5 w-5 text-white" />}
            color="bg-gradient-to-r from-blue-500 to-cyan-600 text-white"
            trend={1.8}
          />
          <ESGScoreCard
            title="Governance Score"
            score={dashboardData.esg_scores.governance}
            icon={<Scale className="h-5 w-5 text-white" />}
            color="bg-gradient-to-r from-purple-500 to-indigo-600 text-white"
            trend={3.1}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* ESG Performance Radar Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                ESG Performance Overview
              </CardTitle>
              <CardDescription>Comprehensive view of your ESG scores across all categories</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={esgScoreData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name="ESG Score" dataKey="score" stroke={COLORS.primary} fill={COLORS.primary} fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Canvas Section Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart className="h-5 w-5 mr-2" />
                Canvas Section Progress
              </CardTitle>
              <CardDescription>Completion status across all business model canvas sections</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={canvasProgressData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="name" type="category" width={120} />
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Progress']} />
                  <Bar dataKey="progress" fill={COLORS.primary} />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Industry Comparison */}
          {benchmarkingData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Industry Benchmarking
                </CardTitle>
                <CardDescription>
                  Your performance vs {benchmarkingData.industry} industry average
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsBarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="organization" fill={COLORS.primary} name="Your Organization" />
                    <Bar dataKey="industry" fill={COLORS.secondary} name="Industry Average" />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* ESG Score Trend (Placeholder for future functionality) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                Score Trend Analysis
              </CardTitle>
              <CardDescription>Historical ESG performance trends</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-center justify-center bg-gray-50 rounded-lg">
                <div className="text-center">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 font-medium">Historical Data Coming Soon</p>
                  <p className="text-sm text-gray-500">Complete more assessments to see trends</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Canvas Sections Grid */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              Canvas Section Detailed View
            </CardTitle>
            <CardDescription>Click on any section to start or continue assessment</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(CANVAS_SECTIONS).map(([key, section]) => {
                const completion = dashboardData.canvas_completion[key];
                const progress = completion ? completion.percentage : 0;
                
                return (
                  <Card key={key} className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-gray-300" 
                        onClick={() => {setSelectedCanvasSection(key); setCurrentView('assessment');}}>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${section.color} text-white`}>
                          {section.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm truncate">{section.title}</h4>
                          <p className="text-xs text-gray-500 line-clamp-2">{section.description}</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Progress</span>
                          <span className="font-medium">{Math.round(progress)}%</span>
                        </div>
                        <Progress value={progress} className="h-1.5" />
                        {completion && (
                          <div className="text-xs text-gray-500">
                            {completion.answered} of {completion.total} questions completed
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Action Items */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              Recommended Actions
            </CardTitle>
            <CardDescription>Priority actions to improve your ESG performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800">Complete Environmental Assessment</h4>
                  <p className="text-sm text-yellow-700">
                    {100 - dashboardData.esg_completion.environmental.percentage}% of environmental questions remain unanswered
                  </p>
                </div>
                <Button size="sm" variant="outline" onClick={() => {setCurrentView('assessment')}}>
                  Start <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              
              <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-800">Improve Social Score</h4>
                  <p className="text-sm text-blue-700">
                    Your social score is {dashboardData.esg_scores.social.toFixed(1)} - focus on stakeholder engagement questions
                  </p>
                </div>
                <Button size="sm" variant="outline">
                  View Details <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              
              <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-green-800">Strong Governance Foundation</h4>
                  <p className="text-sm text-green-700">
                    Your governance score of {dashboardData.esg_scores.governance.toFixed(1)} is above industry average
                  </p>
                </div>
                <Button size="sm" variant="outline">
                  Maintain <CheckCircle className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

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
                <Badge variant="outline" className="text-xs">
                  Weight: {question.weight}
                </Badge>
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
                    const label = question.scale_labels?.[value.toString()] || value.toString();
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
                  <p className="text-sm text-gray-500">Advanced Sustainability Analytics Platform</p>
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
              
              <Select value={selectedOrg?.id || ''} onValueChange={async (value) => {
                const org = organizations.find(o => o.id === value);
                setSelectedOrg(org);
                if (org) {
                  await loadAssessments(org.id);
                  await loadDashboardData(org.id);
                }
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
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Create New Organization</DialogTitle>
                    <DialogDescription>Add a new organization to start comprehensive ESG reporting.</DialogDescription>
                  </DialogHeader>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="orgName">Organization Name *</Label>
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
                    <div>
                      <Label htmlFor="headquarters">Headquarters</Label>
                      <Input 
                        id="headquarters"
                        value={newOrgForm.headquarters}
                        onChange={(e) => setNewOrgForm({...newOrgForm, headquarters: e.target.value})}
                        placeholder="e.g., New York, NY"
                      />
                    </div>
                    <div>
                      <Label htmlFor="website">Website</Label>
                      <Input 
                        id="website"
                        value={newOrgForm.website}
                        onChange={(e) => setNewOrgForm({...newOrgForm, website: e.target.value})}
                        placeholder="https://company.com"
                      />
                    </div>
                    <div>
                      <Label htmlFor="employeeCount">Employee Count</Label>
                      <Input 
                        id="employeeCount"
                        type="number"
                        value={newOrgForm.employee_count}
                        onChange={(e) => setNewOrgForm({...newOrgForm, employee_count: e.target.value})}
                        placeholder="e.g., 1250"
                      />
                    </div>
                    <div>
                      <Label htmlFor="revenue">Annual Revenue</Label>
                      <Select value={newOrgForm.annual_revenue} onValueChange={(value) => setNewOrgForm({...newOrgForm, annual_revenue: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select revenue range" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Under $1M">Under $1M</SelectItem>
                          <SelectItem value="$1M - $10M">$1M - $10M</SelectItem>
                          <SelectItem value="$10M - $100M">$10M - $100M</SelectItem>
                          <SelectItem value="$100M - $500M">$100M - $500M</SelectItem>
                          <SelectItem value="$500M - $1B">$500M - $1B</SelectItem>
                          <SelectItem value="$1B+">$1B+</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="md:col-span-2">
                      <Label htmlFor="stockSymbol">Stock Symbol (if public)</Label>
                      <Input 
                        id="stockSymbol"
                        value={newOrgForm.stock_symbol}
                        onChange={(e) => setNewOrgForm({...newOrgForm, stock_symbol: e.target.value})}
                        placeholder="e.g., AAPL"
                      />
                    </div>
                  </div>
                  <div className="mt-6">
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
            <p className="text-gray-500 mb-4">Please select or create an organization to start comprehensive ESG reporting.</p>
          </div>
        ) : (
          <Tabs value={currentView} onValueChange={setCurrentView}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="dashboard">Analytics Dashboard</TabsTrigger>
              <TabsTrigger value="canvas">ESG Canvas</TabsTrigger>
              <TabsTrigger value="assessment">Assessment</TabsTrigger>
              <TabsTrigger value="reports">Reports & Export</TabsTrigger>
            </TabsList>
            
            <TabsContent value="dashboard" className="space-y-6">
              {renderAdvancedDashboard()}
            </TabsContent>
            
            <TabsContent value="canvas" className="space-y-6">
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
                  <p className="text-gray-500 mb-4">Choose a canvas section from the ESG Canvas to start the assessment.</p>
                  <Button onClick={() => setCurrentView('canvas')}>
                    Go to ESG Canvas
                  </Button>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="reports" className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Reports & Export</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Generate comprehensive ESG reports and export data for stakeholders
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="h-5 w-5 mr-2" />
                      Comprehensive ESG Report
                    </CardTitle>
                    <CardDescription>Full sustainability assessment report with all metrics and detailed analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/comprehensive`, '_blank')}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      View HTML Report
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        const printWindow = window.open(`${API}/reports/html/${selectedOrg.id}/comprehensive`, '_blank');
                        printWindow.addEventListener('load', () => {
                          printWindow.print();
                        });
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Print/Save as PDF
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <BarChart className="h-5 w-5 mr-2" />
                      Executive Summary
                    </CardTitle>
                    <CardDescription>High-level overview for stakeholders and board presentation</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/executive`, '_blank')}
                    >
                      <BarChart className="h-4 w-4 mr-2" />
                      View Executive Summary
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        const printWindow = window.open(`${API}/reports/html/${selectedOrg.id}/executive`, '_blank');
                        printWindow.addEventListener('load', () => {
                          printWindow.print();
                        });
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Print/Save Summary
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Globe className="h-5 w-5 mr-2" />
                      Data Export Options
                    </CardTitle>
                    <CardDescription>Export raw data and analytics for external analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        // Export dashboard data as JSON
                        if (dashboardData) {
                          const dataStr = JSON.stringify(dashboardData, null, 2);
                          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                          const exportFileDefaultName = `${selectedOrg.name}_ESG_Data.json`;
                          const linkElement = document.createElement('a');
                          linkElement.setAttribute('href', dataUri);
                          linkElement.setAttribute('download', exportFileDefaultName);
                          linkElement.click();
                        }
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export JSON Data
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      disabled
                    >
                      <Globe className="h-4 w-4 mr-2" />
                      GRI Format (Coming Soon)
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {dashboardData && (
                <Card className="mt-8">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Activity className="h-5 w-5 mr-2" />
                      Quick Report Preview
                    </CardTitle>
                    <CardDescription>Preview your ESG performance with sample report sections</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(canvasProgress).map(([section, progress]) => (
                        <Card key={section} className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="text-center">
                              <h4 className="font-medium text-gray-900 mb-2 text-sm">
                                {CANVAS_SECTIONS[section]?.title}
                              </h4>
                              <div className="text-xl font-bold text-blue-600 mb-2">
                                {Math.round(progress)}%
                              </div>
                              <Progress value={progress} className="h-1.5" />
                              <p className="text-xs text-gray-500 mt-2">
                                {dashboardData.canvas_completion[section]?.answered || 0} / {dashboardData.canvas_completion[section]?.total || 0} completed
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                    
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-blue-800">Reports Available</h4>
                          <p className="text-sm text-blue-700 mt-1">
                            Your HTML reports include comprehensive analysis, ESG scoring, canvas section breakdowns, 
                            and actionable recommendations based on {dashboardData.answered_questions} answered questions.
                          </p>
                          <div className="mt-3 flex space-x-2">
                            <Button 
                              size="sm" 
                              onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/comprehensive`, '_blank')}
                            >
                              View Full Report
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/executive`, '_blank')}
                            >
                              Executive Summary
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  );
}

export default App;