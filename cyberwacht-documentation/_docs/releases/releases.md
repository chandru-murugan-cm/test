---
title: Releases
description: Releases
---

# Release Notes

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Feb 28, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features & Enhancements</h2>
    <ul style="line-height: 1.5;">
      <li><b>Azure Credentials Validation:</b> Implemented Azure credentials validation and enhanced error messaging during validation failures.</li>
      <li><b>User Feedback:</b> Addressed user feedback related to vulnerability tracking. Enhanced to handle vulnerability data retrieval and introduced a UI component for displaying vulnerability details.</li>
    </ul>
  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Feb 21, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features & Enhancements</h2>
    <ul style="line-height: 1.5;">
      <li><b>Deletion Functionality for Configured Domains:</b> Added the ability to delete configured domains (Repo, Web3, Cloud). Related findings are automatically removed upon configuration deletion.</li>
    </ul>
  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Feb 14, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2> New Features & Enhancements</h2>
    <ul style="line-height: 1.5;">
    <li><b>GCP Cloud Scanner:</b> Developed and integrated a cloud scanner for Google Cloud Platform (GCP) to enhance security and monitoring.</li>
      <li><b>Compliance Visualization:</b> Added horizontal cards and summary charts for better compliance insights.</li>
      <li><b>Dashboard Enhancements:</b> Added additional content to improve user experience.</li>
    </ul>

  <h2>Bug Fixes</h2>
    <ul style="line-height: 1.5;">
      <li><b>Data Accuracy in pie chart:</b> Corrected inaccurate data representation for better precision.</li>
      <li><b>Next Scan Column Issue:</b> Resolved display issues for better readability.</li>
      <li><b>GCP Cloud Scan Details:</b> Fixed issues with recommendations and target name accuracy.</li>
      <li><b>Framework-Scanner Type Link:</b> Improved functionality and navigation.</li>
    </ul>

  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Feb 7, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features & Enhancements</h2>
    <ul style="line-height: 1.5;">
      <li><b>Expanded Framework Support:</b> Added more frameworks and updated scanner types for improved performance.</li>
      <li><b>Compliance Scanner Improvements:</b> Enhanced mapping for greater consistency and accuracy.</li>
      <li><b>Manual Compliance Evaluation:</b> Added and improved features for manual compliance assessments.</li>
      <li><b>License & SBOM Enhancements:</b> Improved scanning with better data insights and reporting.</li>
      <li><b>UI Updates:</b> Optimized interface elements for a smoother user experience.</li>
    </ul>

  <h2>Bug Fixes</h2>
    <ul style="line-height: 1.5;">
      <li><b>Fixed Duplicate Cloud Entries:</b> Resolved an issue where multiple cloud entries were created when clicking "Finish" multiple times.</li>
      <li><b>Project Reset Issue:</b> Fixed a problem where projects would reset on refresh.</li>
      <li><b>Framework Error Fixes:</b> Addressed various errors related to framework detection and reporting.</li>
     
    </ul>

  </div>
</div>
---
<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Jan 31, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features & Enhancements</h2>
    <ul style="line-height: 1.5;">
      <li><b>Updated SAMM UI:</b> Improved usability for a more intuitive experience.</li>
      <li><b>Integrated Findings UI with Compliance Details:</b> Enhanced visibility by linking findings with compliance requirements.</li>
    </ul>

    <h2>Bug Fixes</h2>
    <ul style="line-height: 1.5;">
      <li><b>Fixed Project Deletion Issue:</b> Prevents accidental removals of projects.</li>
      <li><b>Cloud Scanner Fix:</b> Resolved an issue where the scanner reported the same findings when tested with dummy data.</li>
      <li><b>Duplicate Entry Fix:</b> Addressed a repeated project deletion issue in the system.</li>
    </ul>

  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Jan 27, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">

  <h2>New Feature</h2>

    <ul style="line-height: 1.5;">
      <li><b>ASVS (Application Security Verification Standard)</b> is now fully integrated into the Cyberwacht platform.</li>

    </ul>

  </div>
</div>
----------------
<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;">
    <h2>Jan 17, 2025</h2>
  </div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>Improvements</h2>
    <ul style="line-height: 1.5;">
      <li><b>Updated SAMM UI with Project-Wise Scorecards:</b> The SAMM UI now features an updated interface with scorecards available on a project-wise basis, improving clarity and usability for users.</li>
      <li><b>Cloud Scanner for Microsoft Azure:</b> A cloud scanner has been successfully implemented for Microsoft Azure, enabling comprehensive scanning capabilities for Azure cloud environments, ensuring security and compliance.</li>
    </ul>

  <h2>Fixes</h2>
    <ul style="line-height: 1.5;">
      <li><b>Dependency Issue in Smart Contract Scanner:</b> Resolved a dependency issue affecting the scanning of smart contract files, ensuring seamless and uninterrupted functionality.</li>
      <li><b>Duplicate Repositories and Domains Issue:</b> Fixed an issue where duplicate repositories and domains were added when the add button was clicked multiple times.</li>
      <li><b>Scrolling Issue with Multiple Projects:</b> Addressed a scrolling issue that occurred when multiple projects were added, improving user experience and navigation in the interface.</li>
    </ul>

  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;"><h2>Jan 3, 2025</h2></div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>Enhancements</h2>

   <h3>SAMM Improvements:</h3>
   <ul style="line-height: 1.5;">
      <li>Improved SAMM functionality with key changes.</li>
      <li>Incorporated principles from the Software Assurance Maturity Model (SAMM), an open framework designed to help organizations implement a risk-based software security strategy tailored to their needs.</li>
      <li>SAMM supports the complete software lifecycle, enabling organizations to evaluate existing security practices, build a balanced software security assurance program, and demonstrate measurable improvements.</li>
    </ul>

   <h3>Documentation Updates:</h3>
   <ul style="line-height: 1.5;">
      <li>Linked the documentation server to the Cyberwacht UI for improved accessibility and usability.</li>
      <li>Enhanced search functionality within the documentation.</li>
    </ul>

   <h2>Fixes</h2>
   <ul style="line-height: 1.5;">
      <li>Resolved user project visibility issues when sharing projects.</li>
      <li>Fixed duplicate findings displayed for multiple smart contract scans.</li>
      <li>Made scan types on the scheduler page read-only.</li>
      <li>Addressed table alignment issues on the scheduler page.</li>
      <li>Fixed pagination not working for page sizes other than 10 per page.</li>
      <li>Resolved the issue of the current project resetting to the first project on refresh during scan status updates.</li>
      <li>Fixed scheduling multiple scans updating all schedulers with the same scan types.</li>
      <li>Improved handling of duplicate entries in smart contract findings.</li>
    </ul>

  </div>
</div>

---

<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;"><h2>Dec 20, 2024</h2></div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features</h2>
     <ul style="line-height: 1.5;">
        <li><b>Smart Contract Scanner:</b> Fully integrated and deployed the smart contract scanner.</li>
        <li><b>Automatic Daily Scans:</b> Implemented automatic daily scan scheduling functionality.</li>
        <li><b>Backend Enhancements:</b> Added various backend functionality improvements.</li>
      </ul>

   <h2>Fixes</h2>
        <ul style="line-height: 1.5;">
        <li>Resolved editing issues for repository labels.</li>
        <li>Fixed issues with configuration and execution for security scans.</li>
      </ul>

  </div>
</div>
---
<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;"><h2>Dec 10, 2024</h2></div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>New Features</h2>
     <ul style="line-height: 1.5;">
        <li><b>GitHub Integration:</b> Added read-only access functionality for GitHub private repositories.</li>
        <li><b>Forgot Password Enhancement:</b> Implemented reset link functionality for the forgot password feature.</li>
      </ul>

   <h2>Fixes</h2>
     <ul style="line-height: 1.5;">
        <li>Resolved issues with user session switching between the previous and current users.</li>
        <li>Fixed the filter functionality in the findings table in the UI.</li>
        <li>Addressed a bug referencing a nonexistent file.</li>
      </ul>

  </div>
</div>
---
<div style="display: flex; align-items: flex-start; gap: 1rem;">
  <div style="flex: 0 0 150px; text-align: right;"><h2>Dec 1, 2024</h2></div>

  <div style="border-left: 1px solid #ccc; padding-left: 1rem;">
    <h2>Key Features and Functionalities</h2>

   <h3>1. Project Management</h3>
     <ul style="line-height: 1.5;">
        <li><b>Seamless Project Creation:</b> Users can create projects effortlessly, associating domains and repositories with each project.</li>
        <li><b>Environment-Based Projects:</b> Users can create separate projects for each environment (e.g., development, staging, production) and monitor them individually.</li>
        <li><b>GitHub Integration:</b> Support for private repositories through GitHub Authentication ensures secure and efficient project setup.</li>
      </ul>

   <h3>2. Scanning Capabilities</h3>
     <ul style="line-height: 1.5;">
        <li><b>On-Demand Scans:</b> Users can initiate scans with the <b>Scan Now</b> option, selecting specific scan types for each scan.</li>
        <li><b>Scan Types:</b>
         <ul style="line-height: 1.5;">
            <li><b>Domain Scan:</b> Analyze domain-related vulnerabilities.</li>
            <li><b>Repository Scan:</b> Evaluate code repositories for vulnerabilities.</li>
          </ul>
        </li>
        <li><b>Comprehensive Techniques:</b> Each scan type incorporates multiple specialized scanning techniques to ensure thorough coverage.</li>
        <li><b>[Upcoming] Scan Scheduling:</b> Automate scans at regular intervals for consistent monitoring and improved efficiency.</li>
      </ul>

   <h3>3. Scans Page</h3>
     <ul style="line-height: 1.5;">
        <li><b>Scan History:</b> Access a detailed history of every triggered scan.</li>
        <li><b>Detailed Information:</b> View comprehensive data about each scan, including the specific scan types utilized.</li>
      </ul>

   <h3>4. Findings Page</h3>
     <ul style="line-height: 1.5;">
        <li><b>Categorized Results:</b> View scan results by severity (Critical, High, Medium, Low), scan type, and status (Open, Solved, Ignored).</li>
        <li><b>Filters:</b> Filter findings by target, severity, and status for streamlined analysis.</li>
        <li><b>Detailed Findings:</b> Navigate to findings for additional information such as the CWE ID and relevant metadata.</li>
        <li><b>AI Fix Recommendations:</b> Fix recommendations powered by AI provide actionable remediation steps.</li>
        <li><b>Finding Management:</b> Manage findings by marking them as Ignored, False Positive, or Closed, enabling effective tracking and resolution.</li>
      </ul>

   <h3>5. Repository and Domain Pages</h3>
     <ul style="line-height: 1.5;">
        <li><b>Context-Specific Findings:</b> Display findings specific to the associated repository or domain for focused analysis.</li>
      </ul>

   <h3>6. License & SBOM (Software Bill of Materials) Page</h3>
     <ul style="line-height: 1.5;">
        <li><b>License Findings:</b> Review findings related to open-source licenses, ensuring compliance and mitigating legal risks.</li>
        <li><b>SBOM Insights:</b> Gain transparency into open-source components and potential risks by managing dependencies effectively.</li>
      </ul>

   <h3>7. Language & Framework Page</h3>
     <ul style="line-height: 1.5;">
        <li><b>Technology Insights:</b> Detailed insights into the programming languages and frameworks detected in your repositories.</li>
        <li><b>Targeted Vulnerability Management:</b> Identify and address technology-specific vulnerabilities efficiently.</li>
      </ul>

   <h3>8. Dashboard</h3>
     <ul style="line-height: 1.5;">
        <li><b>Centralized Overview:</b> A comprehensive view classifying findings by severity levels (Critical, High, Medium, Low).</li>
        <li><b>Tracking Progress:</b> Monitor counts of open, solved, and ignored findings.</li>
        <li><b>Intuitive Design:</b> Provides quick situational awareness and supports effective decision-making.</li>
      </ul>

   <h3>9. Compliance</h3>
     <ul style="line-height: 1.5;">
        <li><b>Compliance Overview:</b> A centralized view of compliance guidelines.</li>
        <li><b>[Upcoming] Compliance Checks:</b> Highlight findings aligned with specific compliance items for improved accountability.</li>
      </ul>

  </div>
</div>
---
