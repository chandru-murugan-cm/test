---
title: Findings

description: Findings
---

# Findings

In the **Findings Table**, you can view all the findings along with their associated details such as the date, target, scan type, severity, and status.

## Table Fields and Descriptions

| Field            | Description                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------ |
| **Finding Date** | Shows the date and time when the finding was reported.                                                       |
| **Target**       | Indicates whether the finding is associated with a domain or repository.                                     |
| **Scan Type**    | Displays the type of scanner used for the scan.                                                              |
| **Finding**      | Provides detailed information about the finding, including a description of the identified issue.            |
| **Severity**     | Represents the severity level of the finding, categorized as: Critical, High, Medium, Low, or Informational. |
| **Status**       | Shows the current status of the finding.                                                                     |

### Status Options:

- **Open**: Issue has not yet been resolved.
- **Closed**: Issue has been resolved. If the issue occurs again during the next scan, the status will automatically change back to "Open."
- **False Positive**: The finding is identified as a false positive and does not require further action.
- **Ignored**: The finding is acknowledged but intentionally ignored, often due to specific business or technical reasons.

## Finding Details and Fix Recommendations

When you click on a specific finding, you can view detailed information about the issue and possible solutions. The details are divided into the following sections:

1. **Overview**

   - Displays a summary of the issue and its significance.

2. **Details**

   - Provides in-depth information about the finding, including:
     - The file path(s) where the issue was detected.
     - Additional technical details for better understanding.

3. **Fix Recommendation**
   - Offers step-by-step solutions or guidance to resolve the identified issue effectively.

## Severity Levels

The severity of each finding is classified as follows:

- **Critical**: Immediate action required; the issue poses a severe security risk.
- **High**: High-risk issues that should be addressed urgently.
- **Medium**: Moderate-risk issues that need attention but are not immediately critical.
- **Low**: Minor issues with lower priority.
- **Informational**: Non-critical information for improving configurations or monitoring.

## Status Lifecycle

- **Open**: The issue is newly reported or unresolved.
- **Closed**: The issue has been fixed or no longer exists.
- **Reopened**: If a previously closed issue is detected again during a rescan, its status changes back to Open.
- **False Positive**: The issue has been identified as a false positive and does not require further action.
- **Ignored**: The issue is acknowledged but intentionally ignored, often due to specific business or technical reasons.
