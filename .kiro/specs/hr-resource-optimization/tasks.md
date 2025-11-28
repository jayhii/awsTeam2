# Implementation Plan

- [x] 1. Set up project structure and development environment





  - Create directory structure for Lambda functions, tests, and infrastructure code
  - Set up Python virtual environment with required dependencies
  - Configure AWS CLI and Terraform
  - Initialize Git repository with .gitignore
  - _Requirements: All_

- [x] 2. Implement core data models and utilities



  - _Requirements: 1.2, 2.1, 3.1_


- [x] 2.1 Create Python data models for Employee, Project, Affinity



  - Define Pydantic models with validation
  - Implement serialization/deserialization methods
  - _Requirements: 1.2, 2.1_

- [x]* 2.2 Write property test for data model round trip
  - **Property 5: Project Data Round Trip**
  - **Validates: Requirements 2.1**


- [x] 2.3 Implement skill normalization utility

  - Create skill name mapping dictionary
  - Implement normalization function
  - _Requirements: 1.2, 10.4_

- [x]* 2.4 Write property test for skill normalization consistency
  - **Property 2: Skill Normalization Consistency**
  - **Validates: Requirements 1.2**


- [x] 3. Set up AWS infrastructure with Terraform


  - _Requirements: 9.1, 9.2, 9-1.1_



- [x] 3.1 Deploy DynamoDB tables

  - Create Terraform configuration for 6 tables
  - Apply Team2 tags

  - Enable streams on Employees table
  - _Requirements: 7.1, 9-1.1_

- [x] 3.2 Deploy S3 buckets

  - Create 4 buckets with lifecycle policies
  - Configure encryption and versioning
  - Apply Team2 tags
  - _Requirements: 9.4, 9-1.1_


- [x] 3.3 Create IAM roles and policies

  - Implement LambdaExecutionRole-Team2
  - Implement tag-based access control policies
  - _Requirements: 9-1.2, 9-1.3, 9-1.4, 9-1.6_

- [x] 3.4 Write property test for resource tagging






  - **Property 41: Resource Tagging Enforcement**
  - **Validates: Requirements 9-1.1**

- [x] 3.5 Write property test for tag-based access control






  - **Property 42-45: Tag-Based Access Control**
  - **Validates: Requirements 9-1.2, 9-1.3, 9-1.4, 9-1.5**

- [x] 4. Implement DynamoDB data access layer





  - _Requirements: 2.1, 2.3, 7.1_

- [x] 4.1 Create DynamoDB client wrapper


  - Implement connection management
  - Add retry logic and error handling
  - _Requirements: 7.1_

- [x] 4.2 Implement Employee repository


  - CRUD operations for employee profiles
  - Query by skills
  - _Requirements: 1.1, 1.2_

- [ ]* 4.3 Write property test for skill query completeness
  - **Property 1: Skill Query Completeness**
  - **Validates: Requirements 1.1**

- [x] 4.3 Implement Project repository

  - CRUD operations for projects
  - Query by industry
  - _Requirements: 2.1_

- [x] 4.4 Implement Affinity repository

  - CRUD operations for affinity scores
  - Query by employee pair
  - _Requirements: 2.3, 2-1.7**

- [x] 4.5 Write property test for affinity score persistence





  - **Property 7: Affinity Score Persistence**
  - **Validates: Requirements 2.3**

- [x] 5. Implement Resume Parser Lambda function

  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 5.1 Create Lambda handler for S3 trigger
  - Parse S3 event
  - Download PDF from S3
  - _Requirements: 10.1_

- [ ]* 5.2 Write property test for resume upload pipeline trigger
  - **Property 47: Resume Upload Pipeline Trigger**
  - **Validates: Requirements 10.1**

- [x] 5.3 Integrate Textract for text extraction
  - Call Textract API
  - Handle extraction results
  - _Requirements: 10.1, 10.2_

- [ ]* 5.4 Write property test for Textract to Lambda pipeline
  - **Property 48: Textract to Lambda Pipeline**
  - **Validates: Requirements 10.2**

- [x] 5.5 Integrate Bedrock Claude for structured extraction
  - Create prompt template for resume parsing
  - Call Bedrock API
  - Parse Claude response into structured data
  - _Requirements: 10.3_

- [ ]* 5.6 Write property test for resume field extraction completeness
  - **Property 49: Resume Field Extraction Completeness**
  - **Validates: Requirements 10.3**

- [x] 5.7 Store parsed data to DynamoDB
  - Normalize skills
  - Save to Employees table
  - _Requirements: 10.4_

- [ ]* 5.8 Write property test for skill normalization and storage
  - **Property 50: Skill Normalization and Storage**
  - **Validates: Requirements 10.4**

- [x] 6. Implement Vector Embedding Generator Lambda function

  - _Requirements: 11.1, 11.2_

- [x] 6.1 Create Lambda handler for DynamoDB Stream
  - Parse stream events
  - Extract employee profile data
  - _Requirements: 11.1_

- [x] 6.2 Integrate Bedrock Titan for embedding generation
  - Call Titan Embeddings API
  - Handle embedding response
  - _Requirements: 11.1_

- [ ]* 6.3 Write property test for profile vector embedding generation
  - **Property 52: Profile Vector Embedding Generation**
  - **Validates: Requirements 11.1**

- [x] 6.4 Index embeddings in OpenSearch
  - Create OpenSearch client
  - Index vector with metadata
  - _Requirements: 11.2_

- [ ]* 6.5 Write property test for vector embedding indexing
  - **Property 53: Vector Embedding Indexing**
  - **Validates: Requirements 11.2**

- [x] 7. Deploy OpenSearch domain



  - _Requirements: 11.2, 11.3_

- [x] 7.1 Create Terraform configuration for OpenSearch

  - Configure cluster with 2 nodes
  - Enable encryption
  - Apply Team2 tags
  - _Requirements: 9-1.1, 9-1.4_


- [x] 7.2 Create OpenSearch indices

  - Define mappings for employee_profiles
  - Define mappings for project_requirements
  - Configure knn_vector fields
  - _Requirements: 11.2_

- [x] 8. Implement Affinity Score Calculator Lambda function

  - _Requirements: 2-1.1, 2-1.2, 2-1.3, 2-1.4, 2-1.5, 2-1.6, 2-1.7_

- [x] 8.1 Create Lambda handler for EventBridge trigger
  - Set up daily schedule
  - Fetch all employee pairs
  - _Requirements: 2-1.7_

- [x] 8.2 Implement project collaboration analysis
  - Calculate overlap periods
  - Compute collaboration score
  - _Requirements: 2-1.1_

- [ ]* 8.3 Write property test for project overlap calculation
  - **Property 10: Project Overlap Calculation**
  - **Validates: Requirements 2-1.1**

- [x] 8.4 Implement messenger communication analysis
  - Anonymize PII
  - Calculate message frequency
  - Compute response time metrics
  - _Requirements: 2-1.2, 2-1.3_

- [ ]* 8.5 Write property test for messenger data anonymization
  - **Property 11: Messenger Data Anonymization**
  - **Validates: Requirements 2-1.2**

- [ ]* 8.6 Write property test for communication score multi-factor
  - **Property 12: Communication Score Multi-Factor**
  - **Validates: Requirements 2-1.3**

- [x] 8.7 Implement event participation analysis
  - Find shared events
  - Calculate social score
  - _Requirements: 2-1.4_

- [ ]* 8.8 Write property test for event participation scoring
  - **Property 13: Event Participation Scoring**
  - **Validates: Requirements 2-1.4**

- [x] 8.9 Implement special day contact analysis
  - Identify paydays and vacation days
  - Calculate contact frequency
  - _Requirements: 2-1.5_

- [ ]* 8.10 Write property test for special day contact analysis
  - **Property 14: Special Day Contact Analysis**
  - **Validates: Requirements 2-1.5**

- [x] 8.11 Implement weighted average calculation
  - Combine all component scores
  - Apply weights
  - _Requirements: 2-1.6_

- [ ]* 8.12 Write property test for affinity score weighted average
  - **Property 15: Affinity Score Weighted Average**
  - **Validates: Requirements 2-1.6**

- [x] 8.13 Store affinity scores to DynamoDB


  - Save to EmployeeAffinity table
  - _Requirements: 2-1.7_

- [ ]* 8.14 Write property test for affinity score update persistence
  - **Property 16: Affinity Score Update Persistence**
  - **Validates: Requirements 2-1.7**

- [-] 9. Implement Project Recommendation Engine Lambda function

  - _Requirements: 2.2, 2.4, 2.5_


- [x] 9.1 Create Lambda handler for API Gateway

  - Parse request body
  - Validate input
  - _Requirements: 2.2_


- [x] 9.2 Implement skill matching algorithm

  - Query employees by skills
  - Calculate skill match scores
  - _Requirements: 1.3, 2.2_

- [ ]* 9.3 Write property test for skill match score ordering
  - **Property 3: Skill Match Score Ordering**
  - **Validates: Requirements 1.3**



- [x] 9.4 Implement vector similarity search

  - Query OpenSearch with project requirements
  - Retrieve similar employee profiles
  - _Requirements: 11.3, 11.4_

- [ ]* 9.5 Write property test for vector similarity search
  - **Property 54: Vector Similarity Search**
  - **Validates: Requirements 11.3**

- [ ]* 9.6 Write property test for similarity score inclusion
  - **Property 55: Similarity Score Inclusion**

  - **Validates: Requirements 11.4**



- [x] 9.7 Fetch affinity scores from DynamoDB
  - Query EmployeeAffinity table

  - _Requirements: 2.2_



- [x] 9.8 Implement multi-factor scoring algorithm
  - Combine skill, history, and affinity scores
  - Rank candidates
  - _Requirements: 2.2, 2.4_

- [x]* 9.9 Write property test for recommendation multi-factor scoring

  - **Property 6: Recommendation Multi-Factor Scoring**


  - **Validates: Requirements 2.2**

- [x] 9.10 Check employee availability
  - Query current project assignments
  - Include availability in results
  - _Requirements: 2.5_


- [x]* 9.11 Write property test for availability information inclusion

  - **Property 9: Availability Information Inclusion**
  - **Validates: Requirements 2.5**


- [x] 9.12 Generate recommendation reasoning with Claude
  - Create prompt with candidate details
  - Call Bedrock API
  - Parse reasoning
  - _Requirements: 2.4_



- [ ]* 9.13 Write property test for recommendation reasoning completeness
  - **Property 8: Recommendation Reasoning Completeness**

  - **Validates: Requirements 2.4**

- [x] 9.14 Format and return response
  - Include all required fields
  - _Requirements: 1.4, 2.4_

- [ ]* 9.15 Write property test for recommendation output completeness
  - **Property 4: Recommendation Output Completeness**
  - **Validates: Requirements 1.4**

- [-] 10. Implement Domain Analysis Engine Lambda function

  - _Requirements: 4.1, 4.2, 4.3, 4.4_


- [x] 10.1 Create Lambda handler for API Gateway

  - Parse request
  - Fetch all project history
  - _Requirements: 4.1_


- [x] 10.2 Implement domain classification with Claude
  - Create prompt for domain analysis
  - Call Bedrock API
  - Parse classification results
  - _Requirements: 4.1_

- [ ]* 10.3 Write property test for domain classification completeness
  - **Property 22: Domain Classification Completeness**
  - **Validates: Requirements 4.1**


- [x] 10.4 Implement gap identification
  - Compare current vs potential domains
  - Identify missing domains
  - _Requirements: 4.2_

- [ ]* 10.5 Write property test for domain gap identification
  - **Property 23: Domain Gap Identification**
  - **Validates: Requirements 4.2**


- [x] 10.6 Analyze skill gaps and transition feasibility
  - Identify required skills for new domains
  - Assess current employee skills
  - _Requirements: 4.3_

- [ ]* 10.7 Write property test for domain entry analysis
  - **Property 24: Domain Entry Analysis**

  - **Validates: Requirements 4.3**

- [x] 10.8 Update domain portfolio on new hire
  - Trigger on new employee creation
  - Add domains to portfolio
  - _Requirements: 4.4_

- [ ]* 10.9 Write property test for portfolio update on new hire
  - **Property 25: Portfolio Update on New Hire**
  - **Validates: Requirements 4.4**


- [ ] 11. Implement Quantitative Analysis Lambda function
  - _Requirements: 3.2, 3.3_

- [x] 11.1 Create Lambda handler for API Gateway

  - Parse employee ID from request
  - Fetch employee data
  - _Requirements: 3.2_


- [x] 11.2 Calculate experience metrics
  - Years of experience
  - Project count
  - Skill diversity
  - _Requirements: 3.2_


- [x] 11.3 Integrate tech trend data
  - Fetch from TechTrends table
  - Assess skill recency and demand
  - _Requirements: 3.2, 12.3_

- [ ]* 11.4 Write property test for tech stack evaluation factors
  - **Property 18: Tech Stack Evaluation Factors**

  - **Validates: Requirements 3.2**

- [x] 11.5 Calculate project experience scores
  - Evaluate scale, role, performance
  - _Requirements: 3.3_

- [x]* 11.6 Write property test for project experience multi-factor evaluation

  - **Property 19: Project Experience Multi-Factor Evaluation**
  - **Validates: Requirements 3.3**

- [x] 11.7 Return quantitative evaluation
  - Format response with all scores
  - _Requirements: 3.2, 3.3_

- [-] 12. Implement Qualitative Analysis Lambda function

  - _Requirements: 3.1, 3.4, 3.5_

- [x] 12.1 Create Lambda handler for API Gateway

  - Parse employee ID
  - Fetch employee profile
  - _Requirements: 3.1_


- [x] 12.2 Analyze resume with Claude
  - Create evaluation prompt
  - Call Bedrock API
  - Parse strengths, weaknesses, recommendations
  - _Requirements: 3.1, 3.4_

- [ ]* 12.3 Write property test for resume extraction completeness
  - **Property 17: Resume Extraction Completeness**
  - **Validates: Requirements 3.1**

- [ ]* 12.4 Write property test for evaluation output completeness
  - **Property 20: Evaluation Output Completeness**
  - **Validates: Requirements 3.4**


- [x] 12.5 Implement suspicious content detection
  - Identify questionable claims
  - Flag for verification
  - _Requirements: 3.5_

- [ ]* 12.6 Write property test for suspicious content flagging
  - **Property 21: Suspicious Content Flagging**
  - **Validates: Requirements 3.5**

- [-] 13. Implement Tech Trend Collector Lambda function

  - _Requirements: 12.1, 12.2, 12.4, 12.5_

- [x] 13.1 Create Lambda handler for EventBridge trigger

  - Set up weekly schedule
  - _Requirements: 12.1_

- [ ]* 13.2 Write property test for scheduled trend collection
  - **Property 57: Scheduled Trend Collection**
  - **Validates: Requirements 12.1**


- [x] 13.3 Call external API for tech trends
  - Implement API client
  - Handle authentication
  - _Requirements: 12.1_


- [x] 13.4 Parse and store trend data
  - Extract relevant fields
  - Save to TechTrends table
  - _Requirements: 12.2_

- [ ]* 13.5 Write property test for trend data persistence
  - **Property 58: Trend Data Persistence**

  - **Validates: Requirements 12.2**

- [x] 13.6 Implement fallback for API failures
  - Use cached data
  - Implement retry logic
  - _Requirements: 12.4_

- [ ]* 13.7 Write property test for API failure fallback
  - **Property 60: API Failure Fallback**

  - **Validates: Requirements 12.4**

- [x] 13.8 Trigger score recalculation on update
  - Invoke quantitative analysis for all employees
  - _Requirements: 12.5_

- [ ]* 13.9 Write property test for cascading score recalculation
  - **Property 61: Cascading Score Recalculation**
  - **Validates: Requirements 12.5**

- [x] 14. Set up API Gateway
  - _Requirements: 9.2, 9-1.1_


- [x] 14.1 Create REST API with Terraform
  - Define API Gateway resource
  - Apply Team2 tags
  - _Requirements: 9.2, 9-1.1_


- [x] 14.2 Create API endpoints
  - /recommendations (POST)
  - /domain-analysis (POST)
  - /quantitative-analysis (POST)
  - /qualitative-analysis (POST)

  - _Requirements: 9.2_

- [x] 14.3 Configure IAM authentication
  - Set authorization type to AWS_IAM
  - _Requirements: 9.2_

- [x]* 14.4 Write property test for API authentication enforcement

  - **Property 39: API Authentication Enforcement**
  - **Validates: Requirements 9.2**

- [x] 14.5 Configure CORS
  - Add OPTIONS methods
  - Set CORS headers

  - _Requirements: 9.2_

- [x] 14.6 Deploy API stage

  - Create prod stage
  - _Requirements: 9.2_

- [x] 15. Implement data encryption and access control
  - _Requirements: 7.1, 7.5_

- [x] 15.1 Enable DynamoDB encryption
  - Configure server-side encryption
  - _Requirements: 7.1_

- [ ]* 15.2 Write property test for data encryption at rest
  - **Property 33: Data Encryption at Rest**
  - **Validates: Requirements 7.1**

- [x] 15.3 Implement role-based access control
  - Define user roles
  - Implement permission checks
  - _Requirements: 7.5_

- [ ]* 15.4 Write property test for role-based access control
  - **Property 34: Role-Based Access Control**
  - **Validates: Requirements 7.5**

- [x] 16. Implement visualization and reporting features





  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 16.1 Create data aggregation functions


  - Aggregate skill distribution
  - Calculate domain coverage
  - Summarize team composition
  - _Requirements: 8.1_

- [ ]* 16.2 Write property test for visualization data completeness
  - **Property 35: Visualization Data Completeness**
  - **Validates: Requirements 8.1**

- [x] 16.3 Implement dashboard metrics endpoint

  - Return availability, project status, pending recommendations
  - _Requirements: 8.2_

- [ ]* 16.4 Write property test for dashboard metrics completeness
  - **Property 36: Dashboard Metrics Completeness**
  - **Validates: Requirements 8.2**

- [x] 16.5 Implement date range filtering

  - Add query parameters for date range
  - Filter results by date
  - _Requirements: 8.3_

- [ ]* 16.6 Write property test for date range filtering accuracy
  - **Property 37: Date Range Filtering Accuracy**
  - **Validates: Requirements 8.3**

- [x] 16.7 Implement report export

  - Generate PDF reports
  - Generate Excel reports
  - _Requirements: 8.4_

- [ ]* 16.8 Write property test for export format support
  - **Property 38: Export Format Support**
  - **Validates: Requirements 8.4**

- [x] 17. Load test data into DynamoDB
  - _Requirements: All_

- [x] 17.1 Create data loading script
  - Read test data files
  - Batch write to DynamoDB
  - _Requirements: All_

- [x] 17.2 Load employee test data
  - Load from employees_extended.json
  - _Requirements: 1.1, 1.2_

- [x] 17.3 Load project test data
  - Load from project_example.txt
  - _Requirements: 2.1_

- [x] 17.4 Load affinity test data
  - Load from employee_affinity_data.json
  - _Requirements: 2.3_

- [x] 17.5 Load messenger logs
  - Load from messenger_logs_anonymized.json
  - _Requirements: 2-1.2_

- [x] 17.6 Load company events
  - Load from company_events.json
  - _Requirements: 2-1.4_

- [x] 18. Create deployment automation scripts
  - _Requirements: 9.1_

- [x] 18.1 Create Lambda packaging script
  - Package Python code with dependencies
  - Create ZIP files
  - _Requirements: 9.1_

- [x] 18.2 Create deployment script
  - Automate terraform init, plan, apply
  - Handle AWS credentials
  - _Requirements: 9.1_

- [x] 18.3 Create data loading script
  - Automate test data upload
  - Create OpenSearch indices
  - _Requirements: 9.1_

- [x] 19. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 20. Create monitoring and alerting





  - _Requirements: 9.5_

- [x] 20.1 Set up CloudWatch dashboards


  - Create dashboard for Lambda metrics
  - Create dashboard for API Gateway metrics
  - Create dashboard for DynamoDB metrics
  - _Requirements: 9.5_

- [x] 20.2 Configure CloudWatch alarms

  - Lambda error rate alarm
  - API Gateway latency alarm
  - DynamoDB throttling alarm
  - _Requirements: 9.5_

- [x] 20.3 Set up SNS notifications

  - Create SNS topic
  - Subscribe email addresses
  - _Requirements: 9.5_

- [x] 21. Create documentation





  - _Requirements: All_

- [x] 21.1 Write API documentation


  - Document all endpoints
  - Include request/response examples
  - _Requirements: 9.2_

- [x] 21.2 Write deployment guide


  - Step-by-step deployment instructions
  - Troubleshooting section
  - _Requirements: 9.1_

- [x] 21.3 Write operations runbook


  - Common issues and solutions
  - Monitoring and alerting guide
  - _Requirements: 9.5_

- [x] 22. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: UI Enhancement and Feature Completion

- [x] 23. Dashboard - Remove hardcoded data and integrate DynamoDB




  - _Requirements: 8.1, 8.2_

- [x] 23.1 Update Dashboard component to fetch real-time data


  - Remove all hardcoded statistics
  - Implement API calls to fetch employee count, project count, and metrics
  - Display loading states during data fetch
  - _Requirements: 8.1, 8.2_

- [x] 23.2 Implement dashboard metrics aggregation Lambda


  - Create endpoint to return aggregated dashboard statistics
  - Calculate total employees, active projects, pending evaluations
  - Return skill distribution and domain coverage data
  - _Requirements: 8.1, 8.2_

- [x] 23.3 Update dashboard UI to match design specifications


  - Adjust card layouts and styling based on provided screenshots
  - Implement responsive design for metric cards
  - Add visual indicators for trends (up/down arrows)
  - _Requirements: 8.1_

- [ ] 24. Personnel Management - Add new employee registration
  - _Requirements: 1.1, 1.2_

- [ ] 24.1 Create employee registration modal component
  - Design popup form with all required fields from DynamoDB schema
  - Include fields: name, email, skills, experience, department, position
  - Add form validation for required fields
  - _Requirements: 1.1, 1.2_

- [ ] 24.2 Implement employee creation Lambda function
  - Create API endpoint POST /employees
  - Validate input data
  - Store new employee to DynamoDB Employees table
  - Return created employee data
  - _Requirements: 1.1, 1.2_

- [ ] 24.3 Connect modal to API and update employee list
  - Implement form submission handler
  - Call employee creation API
  - Refresh employee list after successful creation
  - Show success/error notifications
  - _Requirements: 1.1_

- [ ] 25. Project Management - Add new project registration and AI recommendation
  - _Requirements: 2.1, 2.2_

- [ ] 25.1 Create project registration modal component
  - Design popup form with all required fields from DynamoDB schema
  - Include fields: project name, industry, required skills, duration, team size
  - Add form validation
  - _Requirements: 2.1_

- [ ] 25.2 Implement project creation Lambda function
  - Create API endpoint POST /projects
  - Validate input data
  - Store new project to DynamoDB Projects table
  - Return created project data
  - _Requirements: 2.1_

- [ ] 25.3 Add "AI 인력 추천 받기" button to project management
  - Add button to each project card
  - Trigger recommendation engine when clicked
  - Navigate to recommendation results page
  - _Requirements: 2.2_

- [ ] 25.4 Connect modal to API and update project list
  - Implement form submission handler
  - Call project creation API
  - Refresh project list after successful creation
  - Show success/error notifications
  - _Requirements: 2.1_

- [ ] 26. Personnel Recommendation - Remove hardcoded data and add assignment feature
  - _Requirements: 2.2, 2.4, 2.5_

- [ ] 26.1 Update recommendation results to use real API data
  - Remove all hardcoded recommendation results
  - Fetch recommendations from recommendation engine API
  - Display loading states during API calls
  - _Requirements: 2.2, 2.4_

- [ ] 26.2 Update recommendation UI to match design specifications
  - Adjust layout based on provided screenshots
  - Display employee cards with match scores, skills, and reasoning
  - Show availability status clearly
  - _Requirements: 2.4, 2.5_

- [ ] 26.3 Implement project assignment functionality
  - Add "프로젝트에 투입" button to each recommended employee
  - Create modal to confirm assignment details
  - Update employee's current project assignment
  - _Requirements: 2.5_

- [ ] 26.4 Create project assignment Lambda function
  - Create API endpoint POST /projects/{projectId}/assign
  - Update employee's assignment in DynamoDB
  - Update project's team members list
  - Check for assignment conflicts
  - _Requirements: 2.5_

- [ ] 26.5 Add detailed information view for recommendations
  - Implement expandable detail section for each candidate
  - Show complete project history, skill breakdown, affinity scores
  - Display AI-generated reasoning in detail
  - _Requirements: 2.4_

- [ ] 27. Domain Analysis - Update results display
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 27.1 Redesign domain analysis results UI
  - Update layout to match provided screenshots
  - Display domain cards with progress indicators
  - Show current domains vs potential domains clearly
  - _Requirements: 4.1, 4.2_

- [ ] 27.2 Enhance domain gap visualization
  - Add visual indicators for domain gaps
  - Display skill requirements for new domains
  - Show feasibility scores with color coding
  - _Requirements: 4.2, 4.3_

- [ ] 27.3 Add domain expansion recommendations section
  - Display prioritized list of recommended domains
  - Show required skills and current skill gaps
  - Include transition feasibility analysis
  - _Requirements: 4.3_

- [ ] 28. Employee Analysis - Add resume upload and evaluation workflow
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.1, 10.2, 10.3_

- [ ] 28.1 Implement resume upload functionality
  - Add file upload component to employee analysis page
  - Support PDF file format
  - Upload to S3 bucket
  - Trigger resume parser Lambda automatically
  - _Requirements: 10.1_

- [ ] 28.2 Create evaluation status dashboard
  - Display list of pending evaluations
  - Show evaluation progress (대기, 승인됨, 검토중, 반려됨)
  - Update UI to match provided screenshots
  - _Requirements: 3.1_

- [ ] 28.3 Implement evaluation approval workflow
  - Add "승인" (Approve) button to evaluation cards
  - Create API endpoint PUT /evaluations/{id}/approve
  - Update evaluation status in DynamoDB
  - Send notification on status change
  - _Requirements: 3.1_

- [ ] 28.4 Implement evaluation review workflow
  - Add "검토" (Review) button to evaluation cards
  - Create modal for review comments
  - Create API endpoint PUT /evaluations/{id}/review
  - Store review comments and update status
  - _Requirements: 3.1_

- [ ] 28.5 Implement evaluation rejection workflow
  - Add "반려" (Reject) button to evaluation cards
  - Create modal for rejection reason
  - Create API endpoint PUT /evaluations/{id}/reject
  - Store rejection reason and update status
  - _Requirements: 3.1_

- [ ] 28.6 Update evaluation display to match design
  - Redesign evaluation cards based on screenshots
  - Show evaluation scores with progress bars
  - Display strengths, weaknesses, and AI recommendations clearly
  - Add status badges (대기중, 승인됨, 검토중, 반려됨)
  - _Requirements: 3.1, 3.4_

- [ ] 29. Create evaluation workflow Lambda functions
  - _Requirements: 3.1_

- [ ] 29.1 Implement evaluation status update Lambda
  - Create unified endpoint for status updates
  - Handle approve, review, reject actions
  - Update EmployeeEvaluations table
  - Send notifications via SNS
  - _Requirements: 3.1_

- [ ] 29.2 Implement evaluation list Lambda
  - Create endpoint GET /evaluations
  - Support filtering by status
  - Return paginated results
  - Include employee details in response
  - _Requirements: 3.1_

- [ ] 30. Update API Gateway with new endpoints
  - _Requirements: 9.2_

- [ ] 30.1 Add new API endpoints to Terraform configuration
  - POST /employees (create employee)
  - POST /projects (create project)
  - POST /projects/{projectId}/assign (assign employee)
  - GET /evaluations (list evaluations)
  - PUT /evaluations/{id}/approve (approve evaluation)
  - PUT /evaluations/{id}/review (review evaluation)
  - PUT /evaluations/{id}/reject (reject evaluation)
  - GET /dashboard/metrics (dashboard statistics)
  - _Requirements: 9.2_

- [ ] 30.2 Update CORS configuration for new endpoints
  - Add CORS headers to all new Lambda functions
  - Configure OPTIONS methods
  - _Requirements: 9.2_

- [ ] 30.3 Deploy updated API Gateway
  - Apply Terraform changes
  - Test all new endpoints
  - Update API documentation
  - _Requirements: 9.2_

- [ ] 31. Final Integration Testing
  - _Requirements: All_

- [ ] 31.1 Test complete employee registration flow
  - Test modal opening and form validation
  - Test API integration and data persistence
  - Verify employee list refresh
  - _Requirements: 1.1, 1.2_

- [ ] 31.2 Test complete project registration and recommendation flow
  - Test project creation modal
  - Test AI recommendation trigger
  - Verify recommendation results display
  - Test project assignment functionality
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 31.3 Test evaluation workflow end-to-end
  - Test resume upload and parsing
  - Test evaluation status updates
  - Test approve, review, reject actions
  - Verify status changes persist
  - _Requirements: 3.1, 10.1, 10.2, 10.3_

- [ ] 31.4 Test dashboard data integration
  - Verify all metrics load from DynamoDB
  - Test data refresh functionality
  - Verify UI matches design specifications
  - _Requirements: 8.1, 8.2_

- [ ] 32. Update documentation for new features
  - _Requirements: All_

- [ ] 32.1 Update API documentation
  - Document all new endpoints
  - Add request/response examples
  - Include error codes and handling
  - _Requirements: 9.2_

- [ ] 32.2 Create user guide for new features
  - Document employee registration process
  - Document project registration and AI recommendation
  - Document evaluation workflow
  - Include screenshots from UI
  - _Requirements: All_

- [ ] 33. Final Checkpoint - Phase 2 Complete
  - Ensure all new features are working correctly
  - Verify UI matches design specifications from screenshots
  - Confirm all hardcoded data has been removed
  - Ask the user if questions arise.
