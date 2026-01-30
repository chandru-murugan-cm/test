from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from mongoengine import DoesNotExist, ValidationError
from controllers.util import get_current_user_from_jwt_token
import uuid
from datetime import datetime, timezone
import json
from entities.CyberServiceEntity import (
    FindingMaster, RawScanOutput, Scans, ScannerTypes, Scanners,
    FindingSeverity, FindingStatus, ScanTargetType, ScanStatus
)
from typing import List


# Valid values for validation
VALID_SEVERITIES = ['critical', 'high', 'medium', 'low', 'informational']
VALID_STATUSES = ['open', 'closed', 'ignored', 'false positive']
VALID_TARGET_TYPES = ['repo', 'domain', 'container', 'cloud', 'web3', 'vm']


class ManualVaptUploadController:
    """
    Controller for handling manual VAPT JSON upload functionality.
    """

    def __init__(self) -> None:
        pass

    def _get_or_create_manual_scanner(self, current_user: str) -> str:
        """
        Get or create the 'Manual Scan' scanner entry.
        Returns the scanner_id.
        """
        try:
            scanner = Scanners.objects.get(name="Manual Scan")
            return scanner.scanner_id
        except DoesNotExist:
            scanner_id = str(uuid.uuid4())
            scanner = Scanners(
                scanner_id=scanner_id,
                name="Manual Scan",
                description="Manual VAPT findings uploaded via JSON",
                version="1.0",
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            scanner.save()
            return scanner_id

    def _get_or_create_manual_scanner_type(self, scanner_id: str, current_user: str) -> str:
        """
        Get or create the 'Manual VAPT' scanner type entry.
        Returns the scan_type_id.
        """
        try:
            scanner_type = ScannerTypes.objects.get(scan_type="Manual VAPT")
            return scanner_type.scan_type_id
        except DoesNotExist:
            scan_type_id = str(uuid.uuid4())
            scanner_type = ScannerTypes(
                scan_type_id=scan_type_id,
                scanner_ids=[scanner_id],
                scan_type="Manual VAPT",
                scan_target_type=ScanTargetType.DOMAIN,
                description="Manual VAPT findings uploaded via JSON file",
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            scanner_type.save()
            return scan_type_id

    def _validate_finding(self, finding: dict, index: int) -> List[str]:
        """
        Validate a single finding entry.
        Returns list of validation errors.
        """
        errors = []

        # Required fields
        if not finding.get('finding_name'):
            errors.append(f"Finding {index}: 'finding_name' is required")
        if not finding.get('finding_desc'):
            errors.append(f"Finding {index}: 'finding_desc' is required")

        # Validate severity
        severity = finding.get('severity', '').lower()
        if severity and severity not in VALID_SEVERITIES:
            errors.append(
                f"Finding {index}: Invalid severity '{severity}'. "
                f"Valid values: {', '.join(VALID_SEVERITIES)}"
            )

        # Validate status
        status = finding.get('status', '').lower()
        if status and status not in VALID_STATUSES:
            errors.append(
                f"Finding {index}: Invalid status '{status}'. "
                f"Valid values: {', '.join(VALID_STATUSES)}"
            )

        # Validate target_type
        target_type = finding.get('target_type', '').lower()
        if target_type and target_type not in VALID_TARGET_TYPES:
            errors.append(
                f"Finding {index}: Invalid target_type '{target_type}'. "
                f"Valid values: {', '.join(VALID_TARGET_TYPES)}"
            )

        return errors

    def _validate_json_structure(self, data: dict) -> List[str]:
        """
        Validate the overall JSON structure.
        Returns list of validation errors.
        """
        errors = []

        if not isinstance(data, dict):
            errors.append("JSON must be an object")
            return errors

        if 'findings' not in data:
            errors.append("JSON must contain a 'findings' array")
            return errors

        findings = data.get('findings', [])
        if not isinstance(findings, list):
            errors.append("'findings' must be an array")
            return errors

        if len(findings) == 0:
            errors.append("'findings' array cannot be empty")
            return errors

        for i, finding in enumerate(findings):
            if not isinstance(finding, dict):
                errors.append(f"Finding {i + 1}: must be an object")
                continue
            finding_errors = self._validate_finding(finding, i + 1)
            errors.extend(finding_errors)

        return errors

    def upload_manual_vapt(self, request):
        """
        Handle the manual VAPT JSON file upload.
        Creates Scan, RawScanOutput, and FindingMaster entries.
        """
        # Validate JWT token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Get form data
        project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')

        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Check for uploaded file
        if 'json_file' not in request.files:
            return jsonify({"error": "No JSON file provided"}), 400

        json_file = request.files['json_file']
        if json_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        if not json_file.filename.lower().endswith('.json'):
            return jsonify({"error": "File must be a .json file"}), 400

        # Parse JSON content
        try:
            file_content = json_file.read().decode('utf-8')
            json_data = json.loads(file_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
        except UnicodeDecodeError:
            return jsonify({"error": "File encoding error. Please use UTF-8 encoded JSON"}), 400

        # Validate JSON structure
        validation_errors = self._validate_json_structure(json_data)
        if validation_errors:
            return jsonify({
                "error": "JSON validation failed",
                "details": validation_errors
            }), 400

        try:
            # Get or create scanner and scanner type
            scanner_id = self._get_or_create_manual_scanner(current_user)
            scan_type_id = self._get_or_create_manual_scanner_type(scanner_id, current_user)

            # Create a scheduler ID for the manual scan (using a placeholder)
            scheduler_id = f"manual-{str(uuid.uuid4())}"

            # Create Scan record with status "completed"
            # Use user_id (selected user) as creator for proper data association
            scan_id = str(uuid.uuid4())
            scan = Scans(
                scan_id=scan_id,
                scheduler_id=scheduler_id,
                project_id=project_id,
                status=ScanStatus.Completed,
                execution_date=datetime.now(timezone.utc),
                description="Manual VAPT findings upload",
                created=datetime.now(timezone.utc),
                creator=user_id,
            )
            scan.save()

            # Create RawScanOutput with original JSON
            raw_scan_output_id = str(uuid.uuid4())
            raw_scan_output = RawScanOutput(
                raw_scan_output_id=raw_scan_output_id,
                scan_id=scan_id,
                scanner_id=scanner_id,
                output=file_content,
                created=datetime.now(timezone.utc),
                creator=user_id,
            )
            raw_scan_output.save()

            # Create FindingMaster entries for each finding
            findings = json_data.get('findings', [])
            created_findings = []

            for finding in findings:
                finding_id = str(uuid.uuid4())

                # Map severity string to enum
                severity_str = finding.get('severity', 'medium').lower()
                severity_map = {
                    'critical': FindingSeverity.Critical,
                    'high': FindingSeverity.High,
                    'medium': FindingSeverity.Medium,
                    'low': FindingSeverity.Low,
                    'informational': FindingSeverity.Informational,
                }
                severity = severity_map.get(severity_str, FindingSeverity.Medium)

                # Map status string to enum
                status_str = finding.get('status', 'open').lower()
                status_map = {
                    'open': FindingStatus.Open,
                    'closed': FindingStatus.Closed,
                    'ignored': FindingStatus.Ignored,
                    'false positive': FindingStatus.FalsePositive,
                }
                status = status_map.get(status_str, FindingStatus.Open)

                # Map target_type string to enum
                target_type_str = finding.get('target_type', 'domain').lower()
                target_type_map = {
                    'repo': ScanTargetType.REPO,
                    'domain': ScanTargetType.DOMAIN,
                    'container': ScanTargetType.CONTAINER,
                    'cloud': ScanTargetType.CLOUD,
                    'web3': ScanTargetType.WEB3,
                    'vm': ScanTargetType.VM,
                }
                target_type = target_type_map.get(target_type_str, ScanTargetType.DOMAIN)

                # Create FindingMaster entry
                # Use user_id (selected user) as creator, not the admin who uploads
                finding_master = FindingMaster(
                    finding_id=finding_id,
                    project_id=project_id,
                    target_id=project_id,  # Use project_id as target for manual findings
                    scan_type_id=scan_type_id,
                    raw_scan_output_id=raw_scan_output_id,
                    finding_name=finding.get('finding_name'),
                    finding_desc=finding.get('finding_desc'),
                    finding_date=datetime.now(timezone.utc),
                    severity=severity,
                    status=status,
                    target_type=target_type,
                    created=datetime.now(timezone.utc),
                    creator=user_id,
                )
                finding_master.save()
                created_findings.append({
                    'finding_id': finding_id,
                    'finding_name': finding.get('finding_name'),
                    'severity': severity_str,
                    'status': status_str,
                })

            return jsonify({
                "message": "Manual VAPT findings uploaded successfully",
                "data": {
                    "scan_id": scan_id,
                    "findings_count": len(created_findings),
                    "findings": created_findings
                }
            }), 201

        except Exception as e:
            return jsonify({"error": f"Failed to process upload: {str(e)}"}), 500

    def validate_json(self, request):
        """
        Validate a JSON file without creating any database entries.
        Useful for preview functionality.
        """
        # Validate JWT token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Check for uploaded file
        if 'json_file' not in request.files:
            return jsonify({"error": "No JSON file provided"}), 400

        json_file = request.files['json_file']
        if json_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        if not json_file.filename.lower().endswith('.json'):
            return jsonify({"error": "File must be a .json file"}), 400

        # Parse JSON content
        try:
            file_content = json_file.read().decode('utf-8')
            json_data = json.loads(file_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
        except UnicodeDecodeError:
            return jsonify({"error": "File encoding error. Please use UTF-8 encoded JSON"}), 400

        # Validate JSON structure
        validation_errors = self._validate_json_structure(json_data)
        if validation_errors:
            return jsonify({
                "valid": False,
                "errors": validation_errors
            }), 400

        # Return preview of findings
        findings = json_data.get('findings', [])
        preview = []
        for finding in findings:
            preview.append({
                'finding_name': finding.get('finding_name'),
                'finding_desc': finding.get('finding_desc'),
                'severity': finding.get('severity', 'medium'),
                'status': finding.get('status', 'open'),
                'target_type': finding.get('target_type', 'domain'),
            })

        return jsonify({
            "valid": True,
            "findings_count": len(findings),
            "preview": preview
        }), 200

    def get_manual_findings(self, request):
        """
        Get all manual VAPT findings with optional filters.
        Non-admin users can only see their own findings.
        Admin users can see all findings and filter by user_id.
        """
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        # Get filter parameters
        project_id = request.args.get('project_id')
        user_id = request.args.get('user_id')
        severity = request.args.get('severity')
        status = request.args.get('status')
        target_type = request.args.get('target_type')
        year = request.args.get('year')
        month = request.args.get('month')

        try:
            # Get the Manual VAPT scanner type
            try:
                scanner_type = ScannerTypes.objects.get(scan_type="Manual VAPT")
                scan_type_id = scanner_type.scan_type_id
            except DoesNotExist:
                return jsonify({"data": [], "total": 0}), 200

            # Build query filters
            filters = {"scan_type_id": scan_type_id, "isdeleted__ne": True}

            # Apply user-based filtering
            if not is_admin:
                # Non-admin users can only see their own findings
                filters["creator"] = current_user
            elif user_id:
                # Admin can filter by user_id
                filters["creator"] = user_id

            if project_id:
                filters["project_id"] = project_id

            # Convert severity string to enum for filtering
            if severity:
                severity_map = {
                    'critical': FindingSeverity.Critical,
                    'high': FindingSeverity.High,
                    'medium': FindingSeverity.Medium,
                    'low': FindingSeverity.Low,
                    'informational': FindingSeverity.Informational,
                }
                severity_enum = severity_map.get(severity.lower())
                if severity_enum:
                    filters["severity"] = severity_enum

            # Convert status string to enum for filtering
            if status:
                status_map = {
                    'open': FindingStatus.Open,
                    'closed': FindingStatus.Closed,
                    'ignored': FindingStatus.Ignored,
                    'false positive': FindingStatus.FalsePositive,
                }
                status_enum = status_map.get(status.lower())
                if status_enum:
                    filters["status"] = status_enum

            # Convert target_type string to enum for filtering
            if target_type:
                target_type_map = {
                    'repo': ScanTargetType.REPO,
                    'domain': ScanTargetType.DOMAIN,
                    'container': ScanTargetType.CONTAINER,
                    'cloud': ScanTargetType.CLOUD,
                    'web3': ScanTargetType.WEB3,
                    'vm': ScanTargetType.VM,
                }
                target_type_enum = target_type_map.get(target_type.lower())
                if target_type_enum:
                    filters["target_type"] = target_type_enum

            # Add date range filter for month/year
            if year and month:
                from calendar import monthrange
                year_int = int(year)
                month_int = int(month)
                _, last_day = monthrange(year_int, month_int)
                start_date = datetime(year_int, month_int, 1, 0, 0, 0, tzinfo=timezone.utc)
                end_date = datetime(year_int, month_int, last_day, 23, 59, 59, tzinfo=timezone.utc)
                filters["created__gte"] = start_date
                filters["created__lte"] = end_date

            # Query findings
            findings = FindingMaster.objects(**filters).order_by('-created')

            # Serialize results
            results = []
            for finding in findings:
                results.append({
                    "finding_id": finding.finding_id,
                    "project_id": finding.project_id,
                    "finding_name": finding.finding_name,
                    "finding_desc": finding.finding_desc,
                    "severity": finding.severity.value if finding.severity else "medium",
                    "status": finding.status.value if finding.status else "open",
                    "target_type": finding.target_type.value if finding.target_type else "domain",
                    "finding_date": finding.finding_date.isoformat() if finding.finding_date else None,
                    "created": finding.created.isoformat() if finding.created else None,
                    "creator": finding.creator,
                })

            return jsonify({
                "data": results,
                "total": len(results)
            }), 200

        except Exception as e:
            return jsonify({"error": f"Failed to fetch findings: {str(e)}"}), 500

    def update_finding(self, finding_id, request):
        """
        Update a manual VAPT finding.
        Non-admin users can only update their own findings.
        """
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        try:
            # Get the finding
            finding = FindingMaster.objects.get(finding_id=finding_id)

            # Check if user has permission to update this finding
            if not is_admin and finding.creator != current_user:
                return jsonify({"error": "You can only update your own findings"}), 403

            # Get request data
            data = request.get_json()

            # Update fields if provided
            if 'finding_name' in data:
                finding.finding_name = data['finding_name']
            if 'finding_desc' in data:
                finding.finding_desc = data['finding_desc']

            if 'severity' in data:
                severity_str = data['severity'].lower()
                severity_map = {
                    'critical': FindingSeverity.Critical,
                    'high': FindingSeverity.High,
                    'medium': FindingSeverity.Medium,
                    'low': FindingSeverity.Low,
                    'informational': FindingSeverity.Informational,
                }
                if severity_str in severity_map:
                    finding.severity = severity_map[severity_str]

            if 'status' in data:
                status_str = data['status'].lower()
                status_map = {
                    'open': FindingStatus.Open,
                    'closed': FindingStatus.Closed,
                    'ignored': FindingStatus.Ignored,
                    'false positive': FindingStatus.FalsePositive,
                }
                if status_str in status_map:
                    finding.status = status_map[status_str]

            if 'target_type' in data:
                target_type_str = data['target_type'].lower()
                target_type_map = {
                    'repo': ScanTargetType.REPO,
                    'domain': ScanTargetType.DOMAIN,
                    'container': ScanTargetType.CONTAINER,
                    'cloud': ScanTargetType.CLOUD,
                    'web3': ScanTargetType.WEB3,
                    'vm': ScanTargetType.VM,
                }
                if target_type_str in target_type_map:
                    finding.target_type = target_type_map[target_type_str]

            finding.updated = datetime.now(timezone.utc)
            finding.updator = current_user
            finding.save()

            return jsonify({
                "message": "Finding updated successfully",
                "data": {
                    "finding_id": finding.finding_id,
                    "finding_name": finding.finding_name,
                    "finding_desc": finding.finding_desc,
                    "severity": finding.severity.value if finding.severity else "medium",
                    "status": finding.status.value if finding.status else "open",
                    "target_type": finding.target_type.value if finding.target_type else "domain",
                }
            }), 200

        except DoesNotExist:
            return jsonify({"error": "Finding not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Failed to update finding: {str(e)}"}), 500

    def delete_finding(self, finding_id):
        """
        Delete a manual VAPT finding.
        Non-admin users can only delete their own findings.
        """
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        try:
            # Get the finding
            finding = FindingMaster.objects.get(finding_id=finding_id)

            # Check if user has permission to delete this finding
            if not is_admin and finding.creator != current_user:
                return jsonify({"error": "You can only delete your own findings"}), 403

            # Soft delete
            finding.isdeleted = True
            finding.updated = datetime.now(timezone.utc)
            finding.updator = current_user
            finding.save()

            return jsonify({
                "message": "Finding deleted successfully",
                "finding_id": finding_id
            }), 200

        except DoesNotExist:
            return jsonify({"error": "Finding not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Failed to delete finding: {str(e)}"}), 500
