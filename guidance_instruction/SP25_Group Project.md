# Comprehensive Guide for Python and Flask Group Project


## Learning Objectives

### Core Objectives
1. **Collaborative Development:** Master Agile methodology in team environments.
2. **Software Quality Assurance:** Integrate robust testing practices in development workflows.
3. **Python and Flask Expertise:** Design scalable and functional web applications.
4. **API Testing:** Test internal and public APIs effectively using Postman and Requests.
5. **Unit Testing:** Validate individual components or functions using Pytest.
6. **Integration Testing:** Test interactions between components and APIs with Pytest.
7. **UI Testing:** Automate UI workflows using Selenium and Playwright.
8. **Acceptance Testing:** Ensure system-wide requirements are met using `Robot Framework` or `Behave` (BDD)
9. **Parallel Testing Skills:** Develop test plans, cases, and automated scripts using industry tools.
10. **Test Coverage:** Achieve and document a test coverage requirement of 70-80%.
11. **Documentation and Presentation:** Produce high-quality, reflective project documentation.


### Tasks to Achieve Objectives
1. Form a development team and define individual roles.
2. Set up a GitHub repository and create a project management board.
3. Design a web application that will be used to integrate and practice Software Quality Assurance
    - Will also be used as the basis your `Educational Labs` and testing process
4. Develop user stories with acceptance criteria and integrate testing plans.
5. Develop documentation as required for an agile project to enhance collaboration, development and testing
6. Write test plans and execute test cases using tools like Pytest, Requests, Selenium, Playwright and Robot Framework/Behave.
7. Create Test Coverage Reports showing test coverage and details
8. Create `Educational Labs` as live documents with ongoing updates and reviews.
9. Deliver a final presentation summarizing outcomes, challenges, and lessons learned.


## Project Overview

### General Requirements
- Develop a functional Python Flask-based web application. The application does not need to be fully comprehensive but should include enough features to allow for the required testing:
    - unit/pytest
    - integration/pytest
    - web application testing/ui/selenium/playwright
    - api testing/postman and requests
    - system acceptance testing/robot framework 
    
    For example, a task list application or an employee directory should include sufficient minimum functionality to fulfill requirements, such as APIs, CRUD operations, and user interface elements. Every feature implemented must be tested to ensure quality and reliability.

>[!NOTE]
> It is recommended you review the ``Project Guidance and Help/project_starter_architecture_prompts.md` in Blackboard for more information on which architecture to go forward with.

- Include robust documentation and testing at all stages. `Initial` documentation should include:
  - **Project Charter:** Outline objectives, scope, and initial goals.
  - **User Stories:** Define end-user needs with clear acceptance criteria.
  - **API Specifications:** Document endpoints, request/response formats, and expected behaviors.
  - **Initial Test Plan:** Provide an overview of testing strategies and tools to be used.
  - **Team Roles and Responsibilities:** Clarify individual contributions to foster collaboration.

- Apply Agile principles across iterative sprints.

- Collaborate using GitHub and Microsoft Teams.

### Application Features and Testing

Include the following minimum features and testing in the application:
- **API's:** The application will have a miniumum of four internal APIs and one public API.

- **Form Submissions:** Test input validation and submission workflows.

- **Page Navigation:** Validate navigation across multiple sections.

- **CRUD Operations:** Test data creation, retrieval, updates, and deletions.

- **Error Handling:** Simulate exceptions and test user feedback.

- **Keyboard Inputs:** Validate text inputs and shortcuts.

- **Page Navigation:** Test navigation between different pages or sections of the application.

- **Data Entry and Retrieval:** Test CRUD (Create, Read, Update, Delete) operations on data.

- **Data Validation:** Ensure the correctness of data processing and output.

- **Error Messages:** Test for correct error messages under various error conditions.

- **Handling Exceptions:** Ensure the application handles unexpected exceptions gracefully.

---

## Educational Lab Creation

### Overview
Create labs demonstrating testing tools using your application as the test subject.

### Lab Requirements
1. **Unit Testing Lab:**
   - **Tool:** Pytest
   - **Focus:** Test individual components.
   - **Process:** Step-by-step instructions on creating test suites
   - **Student Deliverables from the Lab** scripts, and expected outputs.
   - **Key** Test Suites used in project development 

2. **API Testing Lab:**
   - **Tools:** Postman, Requests
   - **Focus:** Test internal and public APIs.
   - **Process:** step-by-step instructions show how to test with `Postman`
   - **Student Deliverables from the Lab** Postman collections, scripts, and sample test results
   - **Key** Test Suites used in project development 

3. **UI Testing Lab:**
   - **Tools:** Selenium, Playwright
   - **Focus:** Automate and validate UI workflows.
   - **Process:** Step-by-step instructions on creating test suites
   - **Student Deliverables from the Lab** Sample automation scripts and test reports.
   - **Key** Test Suites used in project development 

4. **Acceptance Testing Lab:**
   - **Tool:** Robot Framework or Behave
   - **Focus:** Validate end-to-end user stories.
   - **Process:** Step-by-step instructions on creating test suites
   - **Student Deliverables from the Lab** Test suites and detailed result documentation.
   - **Key** Test Suites used in project development 


## Agile Sprint Breakdown

You will create your own Agile Sprint Breakdown and Tasks. But End of Sprint and Beginning of Sprint should be in each breakdown. 

At the end and beginning of a sprint in Agile development, specific activities ensure smooth transitions, effective planning, and alignment of the team’s goals. Document to show completed. See `Project Guidance and Help/end_beginning_of_sprint.md` in Blackboard

---

## Collaboration and Assessment

### Tools
- **Version Control:** GitHub for repository and issues tracking.
- **Communication:** Teams for daily check-ins and task coordination.
- **Testing Frameworks:** Pytest, Selenium, Postman, Robot Framework.

### Final Deliverables

- A **well-organized repository** with all code, tests, and documentation. Details Below.

#### GitHub Repository Only

  - **Functional Web Application:** A developed web application with features added **incrementally** over the sprints. 
  - **Comprehensive Test Suite:** A compehensive test suite of Unit, UI, API and Acceptance Tests ensuring the application meets quality standards
  - **User Stories or any documentation:** used for application requirements
  - **Test Plan** 
  - **Test Scenarios** 
  - **Test Cases** 
  - **API Documentation** S
  
  #### Both GitHub Repository and Submit to Blackboard
- **Test Coverage Report:** Detailed reports demonstrating the test coverage of 70 - 80% achieved.
- **Educational Labs:** Reflecting pytest, postman, requests, selenium, playwright and robot framework 
- **Project Presenation** 

>[WARNING]
> All of the above are considered living documents and for the application, features should be added **incrementally** over the sprints. It is expected that I will see Issues, Pull Requests, Milestones etc in GitHub reflecting incremental change over the semester vs one rush job towards the end of the semester. **The project will be graded accordingly.**


### Evaluation Criteria
1. **Teamwork:** Contributions tracked via GitHub and peer evaluations.
2. **Code Quality:** Modular and well-documented code.
3. **Testing Thoroughness:** Comprehensive coverage and reliable tests.
4. **Documentation:** Clear, reflective, and complete project documentation.
5. **Lab Content:** Accurate and relevant to the project.




