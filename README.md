# Telegram Assistant for Rent Management

A comprehensive solution for managing rental properties through Telegram integration, featuring three distinct interfaces for different user roles.

## Table of Contents
- [Development](#development)
- [Quality](#quality)
- [Architecture](#architecture)
- [Usage](#usage)

## Development

### Kanban board

**Board Link**: [GitLab Issues Board](https://gitlab.pg.innopolis.university/d.agafonov/assistant-for-rent-project/-/boards)

**Column Entry Criteria**:

- **Open**: 
  - New issues created from templates
  - Issues must have clear acceptance criteria
  - Must be labeled with appropriate priority and type

- **To Do**: 
  - Issues assigned to team members
  - All dependencies resolved
  - Clear definition of done established

- **In Progress**: 
  - Developer actively working on the issue
  - Branch created following naming convention
  - Regular commits being made

- **Review**: 
  - Pull request created and linked to issue
  - All automated tests passing
  - Code review requested from team members

- **Done**: 
  - Pull request merged to main branch
  - All acceptance criteria met
  - Issue closed with appropriate resolution

### Git workflow

**Base Workflow**: GitHub Flow (adapted for GitLab)

**Workflow Rules**:

1. **Creating Issues**:
   - Use predefined templates: [Bug Report](/.gitlab/issue_templates/bugReportTemplate.md), [User story](/.gitlab/issue_templates/userStoryTemplate.md) , [Non code](/.gitlab/issue_templates/non_code_task.md) , [Technical tasks](/.gitlab/issue_templates/technicalTask.md)
   - All issues must have clear title and description
   - Include acceptance criteria for features

2. **Labelling Issues**:
   - `bug` - for bug reports
   - `technical` - for new features
   - `Non code task` - for anther updates
   - `user story` - for user stories
   - `priority::critical/high/medium/low` - for prioritization

3. **Assigning Issues**:
   - Issues assigned during sprint planning
   - One primary assignee per issue
   - Additional reviewers can be added

4. **Branch Management**:
   - **Naming Convention**: `feature/issue-number-short-description` or `bugfix/issue-number-short-description`
   - **Creation**: Branch from `main` for all new work
   - **Merging**: Only through pull requests with review

5. **Commit Messages**:
   - Format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   - Example: `feat(backend): add user authentication endpoint`

6. **Pull Requests**:
   - Use [PR template](/.gitlab/merge_request_templates/default.md)
   - Link to related [issue](https://gitlab.pg.innopolis.university/d.agafonov/assistant-for-rent-project/-/merge_requests/1)
   - Include testing instructions
   - Require at least one review before merge

7. **Code Reviews**:
   - All code must be reviewed before merge
   - Focus on functionality, security, and maintainability
   - Use GitLab's review features

8. **Merging**:
   - Squash commits for cleaner history
   - Delete feature branches after merge
   - Update issue status automatically

9. **Issue Resolution**:
   - Close issues only when all acceptance criteria are met
   - Include testing evidence when applicable

### Secrets management

**Rules for Secrets Management**:

- **Storage**: All secrets stored in GitLab CI/CD variables (protected and masked)
- **Environment Variables**: Used for runtime configuration
- **API Keys**: Stored as environment variables, never in code
- **Database Credentials**: Configured through environment variables
- **Telegram Bot Token**: Stored in GitLab variables as `BOT_TOKEN`

**Security Practices**:
- No secrets in version control
- Regular rotation of API keys
- Separate secrets for different environments (dev/staging/prod)
- Access logs for secret usage

### Automated tests

**Testing Tools**:
- **Python Backend and JavaScript Frontend**: pytest and Jest and React Testing Library for unit and integration tests
- **End-to-End**: Cypress for full application testing

**Test Types Implemented**:

1. **Unit Tests**:
   - Location: `Quality/Unit tests/`
   - Coverage: API endpoints, business logic, database operations
   - Tool: pytest

2. **Integration Tests**:
   - Location: `Quality/Integration tests/`
   - Coverage: API integration, database transactions, component rendering, user interactions
   - Tool: pytest with test database, Jest + React Testing Library

3. **End-to-End Tests**:
   - Location: `Quality/E2E test/`
   - Coverage: Complete user workflows
   - Tool: Cypress

### Continuous Integration

**Workflow Files**:
- [Main CI Pipeline](/.gitlab-ci.yml) - Main build and test pipeline

**Static Analysis Tools**:
- **ESLint**: JavaScript/TypeScript code linting and style checking
- **Prettier**: Code formatting enforcement
- **Black**: Python code formatting
- **Flake8**: Python code style and error checking
- **MyPy**: Python static type checking

**Testing Tools in CI**:
- **pytest**: Python backend testing with coverage reporting
- **Jest**: JavaScript frontend unit testing
- **Cypress**: End-to-end testing in headless mode

### Continuous Deployment

**CD Pipeline**: Automated deployment to production server

**Deployment Stages**:
1. **Build**: Create production builds for all applications
2. **Test**: Run full test suite including E2E tests
3. **Deploy**: Deploy to Ubuntu server using systemd services
4. **Verify**: Health checks and smoke tests

**Deployment Tools**:
- **Docker**: Containerization for consistent environments
- **systemd**: Service management on Ubuntu server
- **Cloudflare Tunnel**: Secure external access
- **GitLab Runners**: Automated deployment execution

## Quality

### Reliability

#### Fault Tolerance
**Importance**: The system must handle failures gracefully to ensure continuous service for property management operations.

**Quality Attribute Scenario**:
- **Source**: Database connection failure
- **Stimulus**: Database becomes unavailable
- **Artifact**: Backend API service
- **Environment**: Production environment under normal load
- **Response**: System continues to serve cached data and queues write operations
- **Response Measure**: System maintains 99% uptime with <5 second recovery time

**Test**: [Reliability Test](Quality/reliability_test.py)

### Performance Efficiency

#### Time Behavior

**mportance**: Ensures responsive user experience during peak usage when multiple users simultaneously access web applications. Critical for user retention in property management scenarios.

**Quality Attribute Scenario**:
- **Source**: Multiple simultaneous users accessing Assisted-for-vert web apps
- **Stimulus**: High volume of task creation requests during peak hours
- **Artifact**: Task creation service
- **Environment**: Production environment during high-usage periods
- **Response**: System processes requests with minimal delay
- **Response Measure**: Average response time ≤ 3 seconds with 100+ concurrent users

**Test**: [Performance Test](Quality/performance_test.py)

### Security

#### Confidentiality

**Importance**: Protects sensitive user data (phone numbers, payment plans, emails) and prevents unauthorized account access. Essential for legal compliance and user trust.

**Quality Attribute Scenario**:
- **Source**: Unauthorized user attempting access
- **Stimulus**: Attempt to access private account data
- **Artifact**: Authentication/authorization system
- **Environment**: Production during registration/authentication
- **Response**: System blocks access and logs attempt
- **Response Measure**: 100% unauthorized access blocked within 1 second

**Test**: [Security Test](Quality/security_test.py)

## Architecture

### Static view

The system follows a microservices architecture with clear separation of concerns:

![Component Diagram](Architecture/static-view/component-diagram.png)

**Components**:
- **Backend API**: FastAPI-based REST API handling business logic
- **Frontend Applications**: Three React applications for different user roles
- **Telegram Bot**: Python-based bot for user interactions
- **Database**: SQLite for data persistence
- **External Services**: Cloudflare for CDN and security

**Coupling and Cohesion**:
- **Low Coupling**: Components communicate through well-defined APIs
- **High Cohesion**: Each component has a single, well-defined responsibility
- **Maintainability**: Modular design allows independent updates and testing

### Dynamic view

The following sequence diagram shows the property creation workflow:

![Sequence Diagram](Architecture/dynamic-view/property-creation-sequence.png)

**Scenario**: Manager creates a new property listing
1. Manager authenticates through Frontend
2. Frontend sends property data to Backend API
3. Backend validates and stores data in Database
4. Backend notifies Telegram Bot of new property
5. Bot sends notification to relevant assistants
6. Frontend receives confirmation and updates UI

**Performance**: This scenario executes in 1.2 seconds on average in production environment.

### Deployment view

![Deployment Diagram](Architecture/deployment-view/deployment-diagram.png)

**Deployment Architecture**:
- **Ubuntu Server**: Hosts all application components
- **systemd Services**: Manages application lifecycle
- **Cloudflare Tunnel**: Provides secure external access
- **Domain Structure**: 
  - `rent-assistant.ru` - Main client interface
  - `api.rent-assistant.ru` - Backend API
  - `manager.rent-assistant.ru` - Manager interface
  - `assistant.rent-assistant.ru` - Assistant interface

**Deployment Choices**:
- **Single Server**: Simplified deployment and maintenance
- **Service-based**: Easy scaling and monitoring
- **Tunnel-based Access**: Enhanced security without VPN

## Usage

### Accessing MVP v2

**Live Application**: https://rent-assistant.ru

**Authentication Credentials**:
- **Manager Access**: https://manager.rent-assistant.ru
  - Username: `manager`
  - Password: `manager123`
- **Assistant Access**: https://assistant.rent-assistant.ru
  - Username: `assistant`
  - Password: `assistant123`

### Features

1. **Property Management**: Create, update, and manage rental properties
2. **Tenant Management**: Track tenant information and lease agreements
3. **Task Assignment**: Assign maintenance and management tasks to assistants
4. **Telegram Integration**: Receive notifications and updates via Telegram
5. **Multi-role Access**: Separate interfaces for managers, assistants, and clients

### Getting Started

1. **For Managers**:
   - Access the manager portal at https://manager.rent-assistant.ru
   - Create property listings
   - Assign tasks to assistants
   - Monitor system activity

2. **For Assistants**:
   - Access the assistant portal at https://assistant.rent-assistant.ru
   - View assigned tasks
   - Update task status
   - Communicate with managers

3. **For Clients**:
   - Access the main interface at https://rent-assistant.ru
   - Browse available properties
   - Submit rental applications
   - Receive updates via Telegram

### Technical Requirements

- **Browser**: Modern web browser with JavaScript enabled
- **Internet Connection**: Required for all features
- **Telegram Account**: Optional, for bot interactions 