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
import { BarChart, Building2, Users, Leaf, Scale, Target, ArrowRight, CheckCircle, AlertCircle, TrendingUp, Download, FileText, PieChart, Activity, Award, Calendar, Globe, DollarSign, Zap, Shield, Calculator } from "lucide-react";
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
  AreaChart,
  ScatterChart,
  Scatter
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
  const [materialityData, setMaterialityData] = useState(null);
  const [financialImpactData, setFinancialImpactData] = useState(null);
  const [ifrsComplianceData, setIFRSComplianceData] = useState(null);
  const [financialStatementsData, setFinancialStatementsData] = useState(null);
  const [integratedReportData, setIntegratedReportData] = useState(null);
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
      const [dashboardResponse, benchmarkResponse, materialityResponse, financialResponse, ifrsResponse, financialStatementsResponse, integratedResponse] = await Promise.all([
        axios.get(`${API}/reports/dashboard/${orgId}`),
        axios.get(`${API}/reports/benchmarking/${orgId}`),
        axios.get(`${API}/materiality/${orgId}/matrix`),
        axios.get(`${API}/financial-impact/${orgId}/summary`),
        axios.get(`${API}/ifrs-mapping/${orgId}/compliance-status`),
        axios.get(`${API}/financial-analysis/${orgId}`),
        axios.get(`${API}/integrated-report/${orgId}`)
      ]);
      
      setDashboardData(dashboardResponse.data);
      setBenchmarkingData(benchmarkResponse.data);
      setMaterialityData(materialityResponse.data);
      setFinancialImpactData(financialResponse.data);
      setIFRSComplianceData(ifrsResponse.data);
      setFinancialStatementsData(financialStatementsResponse.data);
      setIntegratedReportData(integratedResponse.data);
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
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="dashboard">Analytics Dashboard</TabsTrigger>
              <TabsTrigger value="materiality">Double Materiality</TabsTrigger>
              <TabsTrigger value="financial">Financial Impact</TabsTrigger>
              <TabsTrigger value="canvas">ESG Canvas</TabsTrigger>
              <TabsTrigger value="assessment">Assessment</TabsTrigger>
              <TabsTrigger value="reports">Reports & IFRS</TabsTrigger>
            </TabsList>
            
            <TabsContent value="materiality" className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Double Materiality Assessment</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Comprehensive analysis of impact materiality and financial materiality across ESG topics, aligned with IFRS S1 and S2 requirements
                </p>
              </div>

              {materialityData ? (
                <div className="space-y-8">
                  {/* Materiality Matrix Visualization */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Activity className="h-5 w-5 mr-2" />
                        Materiality Matrix
                      </CardTitle>
                      <CardDescription>
                        Impact vs Financial Materiality for {materialityData.matrix_data.length} ESG topics
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={400}>
                        <ScatterChart>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            type="number" 
                            dataKey="impact_materiality" 
                            name="Impact Materiality" 
                            domain={[0, 10]}
                            label={{ value: 'Impact Materiality →', position: 'insideBottom', offset: -5 }}
                          />
                          <YAxis 
                            type="number" 
                            dataKey="financial_materiality" 
                            name="Financial Materiality" 
                            domain={[0, 10]}
                            label={{ value: 'Financial Materiality ↑', angle: -90, position: 'insideLeft' }}
                          />
                          <Tooltip 
                            cursor={{ strokeDasharray: '3 3' }}
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <div className="bg-white p-3 border rounded-lg shadow-lg">
                                    <p className="font-semibold">{data.topic}</p>
                                    <p className="text-sm">Impact: {data.impact_materiality}/10</p>
                                    <p className="text-sm">Financial: {data.financial_materiality}/10</p>
                                    <p className="text-sm">Double: {data.double_materiality.toFixed(1)}/10</p>
                                    {data.ifrs_s1_relevant && <Badge className="mt-1 mr-1">IFRS S1</Badge>}
                                    {data.ifrs_s2_relevant && <Badge className="mt-1">IFRS S2</Badge>}
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Scatter 
                            data={materialityData.matrix_data} 
                            fill="#8884d8"
                          />
                          {/* High priority zone */}
                          <Scatter 
                            data={materialityData.high_priority_topics} 
                            fill="#ef4444"
                          />
                        </ScatterChart>
                      </ResponsiveContainer>
                      <div className="mt-4 flex justify-center space-x-6 text-sm">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                          <span>Standard Topics</span>
                        </div>
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                          <span>High Priority (7.0+)</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* High Priority Topics */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <AlertCircle className="h-5 w-5 mr-2" />
                        High Priority Topics
                      </CardTitle>
                      <CardDescription>Topics with double materiality score ≥ 7.0 requiring immediate attention</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {materialityData.high_priority_topics.map((topic, index) => (
                          <Card key={index} className="border-l-4 border-l-red-500">
                            <CardContent className="p-4">
                              <h4 className="font-semibold text-gray-900 mb-2">{topic.topic}</h4>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span>Impact:</span>
                                  <span className="font-medium">{topic.impact_materiality}/10</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span>Financial:</span>
                                  <span className="font-medium">{topic.financial_materiality}/10</span>
                                </div>
                                <div className="flex justify-between text-sm font-bold border-t pt-2">
                                  <span>Double Materiality:</span>
                                  <span className="text-red-600">{topic.double_materiality.toFixed(1)}/10</span>
                                </div>
                                <div className="flex flex-wrap gap-1 mt-2">
                                  <Badge className={`text-xs ${
                                    topic.esg_category === 'environmental' ? 'bg-green-100 text-green-800' :
                                    topic.esg_category === 'social' ? 'bg-blue-100 text-blue-800' :
                                    'bg-purple-100 text-purple-800'
                                  }`}>
                                    {topic.esg_category.charAt(0).toUpperCase() + topic.esg_category.slice(1)}
                                  </Badge>
                                  {topic.ifrs_s1_relevant && <Badge variant="secondary">IFRS S1</Badge>}
                                  {topic.ifrs_s2_relevant && <Badge variant="secondary">IFRS S2</Badge>}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* IFRS Relevant Topics */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Shield className="h-5 w-5 mr-2" />
                        IFRS Disclosure Requirements
                      </CardTitle>
                      <CardDescription>Topics requiring IFRS S1 or S2 disclosures</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {materialityData.ifrs_relevant_topics.map((topic, index) => (
                          <div key={index} className="p-4 border rounded-lg bg-blue-50">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold text-gray-900">{topic.topic}</h4>
                              <div className="flex gap-1">
                                {topic.ifrs_s1_relevant && (
                                  <Badge className="bg-blue-600 text-white text-xs">IFRS S1</Badge>
                                )}
                                {topic.ifrs_s2_relevant && (
                                  <Badge className="bg-green-600 text-white text-xs">IFRS S2</Badge>
                                )}
                              </div>
                            </div>
                            <div className="text-sm text-gray-600">
                              Double Materiality Score: <span className="font-medium">{topic.double_materiality.toFixed(1)}/10</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Materiality Data Available</h3>
                  <p className="text-gray-500 mb-4">Initialize comprehensive data to view double materiality assessment.</p>
                  <Button onClick={() => axios.post(`${API}/initialize-comprehensive-data`).then(() => loadDashboardData(selectedOrg.id))}>
                    Initialize Sample Data
                  </Button>
                </div>
              )}
            </TabsContent>

            <TabsContent value="financial" className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Financial Impact Analysis</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Quantitative assessment of ESG-related financial impacts, risks, and opportunities with IFRS disclosure requirements
                </p>
              </div>

              {financialImpactData ? (
                <div className="space-y-8">
                  {/* Financial Impact Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-600">Total Projected Impact</p>
                            <p className="text-3xl font-bold text-gray-900">
                              ${Math.abs(financialImpactData.total_projected_impact).toLocaleString()}
                            </p>
                            <p className="text-xs text-gray-500">Net financial effect</p>
                          </div>
                          <div className="text-gray-400">
                            <Calculator className="h-8 w-8" />
                          </div>
                        </div>
                        <div className="mt-4 flex items-center text-sm">
                          <span className={`${financialImpactData.total_projected_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {financialImpactData.total_projected_impact >= 0 ? '+' : ''}
                            {((financialImpactData.total_projected_impact / 1000000) * 100).toFixed(1)}%
                          </span>
                          <span className="text-gray-500 ml-1">impact on business</span>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-600">High Confidence</p>
                            <p className="text-3xl font-bold text-gray-900">{financialImpactData.high_confidence_impacts.length}</p>
                            <p className="text-xs text-gray-500">Reliable estimates</p>
                          </div>
                          <div className="text-gray-400">
                            <CheckCircle className="h-8 w-8" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-600">IFRS Disclosures</p>
                            <p className="text-3xl font-bold text-gray-900">{financialImpactData.ifrs_disclosures_required.length}</p>
                            <p className="text-xs text-gray-500">Required by standards</p>
                          </div>
                          <div className="text-gray-400">
                            <Shield className="h-8 w-8" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-600">Total Impacts</p>
                            <p className="text-3xl font-bold text-gray-900">{financialImpactData.total_impacts}</p>
                            <p className="text-xs text-gray-500">Identified impacts</p>
                          </div>
                          <div className="text-gray-400">
                            <BarChart className="h-8 w-8" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Impact by Type */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <PieChart className="h-5 w-5 mr-2" />
                        Financial Impact by Type
                      </CardTitle>
                      <CardDescription>Breakdown of ESG financial impacts by category</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <RechartsBarChart data={Object.entries(financialImpactData.by_type).map(([key, value]) => ({
                          name: key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
                          count: value.count,
                          value: value.total_value
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip formatter={(value, name) => [
                            name === 'value' ? `$${value.toLocaleString()}` : value,
                            name === 'value' ? 'Total Impact' : 'Count'
                          ]} />
                          <Legend />
                          <Bar dataKey="count" fill="#8884d8" name="Count" />
                          <Bar dataKey="value" fill="#82ca9d" name="Total Impact ($)" />
                        </RechartsBarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* High Confidence Impacts */}
                  {financialImpactData.high_confidence_impacts.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <CheckCircle className="h-5 w-5 mr-2" />
                          High Confidence Financial Impacts
                        </CardTitle>
                        <CardDescription>ESG impacts with high confidence in financial estimates</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {financialImpactData.high_confidence_impacts.map((impact, index) => (
                            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                              <div>
                                <h4 className="font-semibold text-gray-900">{impact.esg_topic}</h4>
                                <p className="text-sm text-gray-600">{impact.impact_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                              </div>
                              <div className="text-right">
                                <p className={`text-lg font-bold ${impact.impact_value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  ${Math.abs(impact.impact_value).toLocaleString()}
                                </p>
                                <Badge variant="outline" className="text-xs">High Confidence</Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* IFRS Disclosure Requirements */}
                  {financialImpactData.ifrs_disclosures_required.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <Shield className="h-5 w-5 mr-2" />
                          IFRS Disclosure Requirements
                        </CardTitle>
                        <CardDescription>Financial impacts requiring IFRS disclosures</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {financialImpactData.ifrs_disclosures_required.map((disclosure, index) => (
                            <div key={index} className="p-4 border rounded-lg bg-red-50 border-red-200">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-semibold text-gray-900">{disclosure.esg_topic}</h4>
                                <Badge className="bg-red-600 text-white">IFRS Required</Badge>
                              </div>
                              <div className="flex justify-between items-center">
                                <p className="text-sm text-gray-600">
                                  Standard: {disclosure.ifrs_reference || 'IFRS S1/S2'}
                                </p>
                                <p className="text-lg font-bold text-red-600">
                                  ${Math.abs(disclosure.impact_value).toLocaleString()}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Calculator className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Financial Impact Data Available</h3>
                  <p className="text-gray-500 mb-4">Initialize comprehensive data to view financial impact analysis.</p>
                  <Button onClick={() => axios.post(`${API}/initialize-comprehensive-data`).then(() => loadDashboardData(selectedOrg.id))}>
                    Initialize Sample Data
                  </Button>
                </div>
              )}
            </TabsContent>
            
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
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Reports & IFRS Compliance</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Generate comprehensive ESG reports with double materiality assessment and IFRS S1/S2 compliance
                </p>
              </div>

              {/* IFRS Compliance Status */}
              {ifrsComplianceData && (
                <Card className="mb-8">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Shield className="h-5 w-5 mr-2" />
                      IFRS Compliance Status
                    </CardTitle>
                    <CardDescription>
                      Current compliance with IFRS S1 and S2 sustainability disclosure requirements
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{ifrsComplianceData.compliance_percentage.toFixed(0)}%</div>
                        <div className="text-sm text-gray-600">Overall Compliance</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{ifrsComplianceData.compliant}</div>
                        <div className="text-sm text-gray-600">Compliant</div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">{ifrsComplianceData.in_progress}</div>
                        <div className="text-sm text-gray-600">In Progress</div>
                      </div>
                      <div className="text-center p-4 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">{ifrsComplianceData.non_compliant}</div>
                        <div className="text-sm text-gray-600">Non-Compliant</div>
                      </div>
                    </div>
                    
                    {ifrsComplianceData.gaps_identified && ifrsComplianceData.gaps_identified.length > 0 && (
                      <div className="mt-6">
                        <h4 className="font-semibold mb-4">Compliance Gaps Identified</h4>
                        <div className="space-y-3">
                          {ifrsComplianceData.gaps_identified.slice(0, 3).map((gap, index) => (
                            <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-medium text-red-800">{gap.ifrs_standard}</h5>
                                <Badge variant="destructive">Gap</Badge>
                              </div>
                              <p className="text-sm text-red-700 mb-1">{gap.requirement}</p>
                              <p className="text-xs text-red-600">{gap.gap}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="h-5 w-5 mr-2" />
                      Comprehensive ESG Report
                    </CardTitle>
                    <CardDescription>Full sustainability assessment with double materiality and financial impact analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/comprehensive`, '_blank')}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      View Enhanced HTML Report
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
                      <Shield className="h-5 w-5 mr-2" />
                      IFRS S1/S2 Compliance
                    </CardTitle>
                    <CardDescription>Sustainability disclosure compliance report</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      disabled
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      IFRS Report (Coming Soon)
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        if (ifrsComplianceData) {
                          const dataStr = JSON.stringify(ifrsComplianceData, null, 2);
                          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                          const exportFileDefaultName = `${selectedOrg.name}_IFRS_Compliance.json`;
                          const linkElement = document.createElement('a');
                          linkElement.setAttribute('href', dataUri);
                          linkElement.setAttribute('download', exportFileDefaultName);
                          linkElement.click();
                        }
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export IFRS Data
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Activity className="h-5 w-5 mr-2" />
                      Double Materiality Report
                    </CardTitle>
                    <CardDescription>Materiality assessment with impact and financial analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      disabled
                    >
                      <Activity className="h-4 w-4 mr-2" />
                      Materiality Report (Coming Soon)
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        if (materialityData) {
                          const dataStr = JSON.stringify(materialityData, null, 2);
                          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                          const exportFileDefaultName = `${selectedOrg.name}_Double_Materiality.json`;
                          const linkElement = document.createElement('a');
                          linkElement.setAttribute('href', dataUri);
                          linkElement.setAttribute('download', exportFileDefaultName);
                          linkElement.click();
                        }
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export Materiality Data
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Calculator className="h-5 w-5 mr-2" />
                      Financial Impact Report
                    </CardTitle>
                    <CardDescription>Quantitative ESG financial impact analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      disabled
                    >
                      <Calculator className="h-4 w-4 mr-2" />
                      Financial Report (Coming Soon)
                    </Button>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        if (financialImpactData) {
                          const dataStr = JSON.stringify(financialImpactData, null, 2);
                          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                          const exportFileDefaultName = `${selectedOrg.name}_Financial_Impact.json`;
                          const linkElement = document.createElement('a');
                          linkElement.setAttribute('href', dataUri);
                          linkElement.setAttribute('download', exportFileDefaultName);
                          linkElement.click();
                        }
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export Financial Data
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Globe className="h-5 w-5 mr-2" />
                      Data Export Options
                    </CardTitle>
                    <CardDescription>Export comprehensive data for external analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => {
                        // Export comprehensive dashboard data as JSON
                        if (dashboardData) {
                          const comprehensiveData = {
                            organization: dashboardData.organization,
                            esg_scores: dashboardData.esg_scores,
                            materiality_summary: dashboardData.materiality_summary,
                            financial_summary: dashboardData.financial_summary,
                            ifrs_compliance: dashboardData.ifrs_compliance,
                            generated_at: new Date().toISOString()
                          };
                          const dataStr = JSON.stringify(comprehensiveData, null, 2);
                          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                          const exportFileDefaultName = `${selectedOrg.name}_Comprehensive_ESG_Data.json`;
                          const linkElement = document.createElement('a');
                          linkElement.setAttribute('href', dataUri);
                          linkElement.setAttribute('download', exportFileDefaultName);
                          linkElement.click();
                        }
                      }}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export All ESG Data
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
                      <Zap className="h-5 w-5 mr-2" />
                      Enhanced Report Preview
                    </CardTitle>
                    <CardDescription>Preview of enhanced ESG performance with double materiality and financial impact</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                        <div className="text-2xl font-bold text-green-600">{dashboardData.esg_scores.environmental.toFixed(1)}</div>
                        <div className="text-sm text-gray-600">Environmental Score</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                        <div className="text-2xl font-bold text-blue-600">{dashboardData.esg_scores.social.toFixed(1)}</div>
                        <div className="text-sm text-gray-600">Social Score</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                        <div className="text-2xl font-bold text-purple-600">{dashboardData.esg_scores.governance.toFixed(1)}</div>
                        <div className="text-sm text-gray-600">Governance Score</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg border border-gray-200">
                        <div className="text-2xl font-bold text-gray-600">{dashboardData.overall_score.toFixed(1)}</div>
                        <div className="text-sm text-gray-600">Overall Score</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                        <h4 className="font-semibold text-yellow-800 mb-2">Materiality Assessment</h4>
                        <p className="text-sm text-yellow-700">
                          {dashboardData.materiality_summary?.high_priority || 0} high-priority topics identified for immediate attention
                        </p>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <h4 className="font-semibold text-green-800 mb-2">Financial Impact</h4>
                        <p className="text-sm text-green-700">
                          ${Math.abs(dashboardData.financial_summary?.total_projected_impact || 0).toLocaleString()} total projected impact
                        </p>
                      </div>
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <h4 className="font-semibold text-blue-800 mb-2">IFRS Compliance</h4>
                        <p className="text-sm text-blue-700">
                          {dashboardData.ifrs_compliance?.compliance_percentage.toFixed(0) || 0}% compliance with sustainability disclosure requirements
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-6 flex justify-center space-x-4">
                      <Button 
                        onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/comprehensive`, '_blank')}
                      >
                        View Complete Report
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => window.open(`${API}/reports/html/${selectedOrg.id}/executive`, '_blank')}
                      >
                        View Executive Summary
                      </Button>
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