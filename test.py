import json
from agents.prd_frd_generator import generate_prd_frd_node

# Example 1: Using explicit project details (old way)
state_explicit = {"requirements": {
  "projectName": "TaskFlow Pro",
  "featureName": "Smart Project Analytics",
  "industry": "Project Management Software",
  "target_users": "Project managers, team leads, executives",
  "business_context": "SaaS platform adding AI-powered analytics"
}}

# Example 2: Using BRD document extraction (new way)
state_brd = {"requirements": {
  "projectName": "To Be Extracted",  # Will be extracted from BRD
  "featureName": "To Be Extracted",  # Will be extracted from BRD
  "industry": "Healthcare Technology",
  "target_users": "Healthcare professionals and patients",
  "business_context": "Digital health platform development",
  "uploaded_documents": [
    {
      "name": "HealthConnect_Platform_BRD.docx",
      "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "size": 8500,
      "content": """
      HealthConnect Digital Health Platform
      Business Requirements Document
      
      Project: HealthConnect Telemedicine Platform
      
      Executive Summary:
      HealthConnect is a comprehensive telemedicine platform designed to connect patients 
      with healthcare providers through secure video consultations, digital prescriptions, 
      and integrated health records management.
      
      Primary Feature: AI-Powered Virtual Health Assistant
      
      The AI-Powered Virtual Health Assistant will provide patients with 24/7 access to 
      preliminary health assessments, symptom checking, medication reminders, and appointment 
      scheduling assistance.
      
      Core Requirements:
      - Natural language processing for symptom analysis
      - Integration with Electronic Health Records (EHR)
      - HIPAA-compliant data handling
      - Multi-language support
      - Mobile and web platform compatibility
      
      Target Users:
      - Patients seeking convenient healthcare access
      - Healthcare providers managing remote consultations
      - Healthcare administrators overseeing patient care
      """
    }
  ]
}}

print("===== Example 1: Explicit Project Details =====")
out1 = generate_prd_frd_node(state_explicit)
final_obj1 = out1.get("prd", {})
print("\n===== Summary (Explicit) =====")
print("Project:", final_obj1.get("projectName"))
print("Feature:", final_obj1.get("featureName"))

print("\n" + "="*60)
print("===== Example 2: BRD Document Extraction =====")
out2 = generate_prd_frd_node(state_brd)
final_obj2 = out2.get("prd", {})
print("\n===== Summary (BRD Extracted) =====")
print("Project:", final_obj2.get("projectName"))
print("Feature:", final_obj2.get("featureName"))
print("PRD keys:", list(final_obj2.get("prd", {}).keys()))
print("FRD count:", len(final_obj2.get("frd", [])))

print("\n" + "="*60)
print("===== Example 3: No Project/Feature Names (BRD Only) =====")
# This simulates what happens when streamlit doesn't send project_name/feature_name at all
state_brd_only = {"requirements": {
  # No projectName or featureName provided - should extract from BRD
  "industry": "Healthcare Technology",
  "target_users": "Healthcare professionals and patients",
  "business_context": "Digital health platform development",
  "uploaded_documents": [
    {
      "name": "MedConnect_Telehealth_BRD.pdf",
      "type": "application/pdf",
      "size": 12000,
      "content": """
      MedConnect Telehealth Solutions
      Business Requirements Document
      
      Project Overview:
      The MedConnect Telehealth Platform will revolutionize remote healthcare delivery 
      by providing a comprehensive solution for virtual consultations, patient monitoring, 
      and integrated care coordination.
      
      Core Feature: Real-Time Patient Monitoring System
      
      This system will continuously monitor patient vital signs, medication adherence, 
      and health indicators through connected IoT devices and mobile applications.
      
      Key Capabilities:
      - 24/7 vital signs monitoring via wearable devices
      - Automated alert system for healthcare providers
      - Patient dashboard with health trends
      - Integration with Electronic Medical Records (EMR)
      - Emergency response coordination
      """
    }
  ]
}}

out3 = generate_prd_frd_node(state_brd_only)
final_obj3 = out3.get("prd", {})
print("\n===== Summary (BRD Only - No Input Names) =====")
print("Project:", final_obj3.get("projectName"))
print("Feature:", final_obj3.get("featureName"))

print("\n===== BRD Extraction Tests =====")
print("Example 2 - Input with placeholders:")
print(f"  Input: 'To Be Extracted' → Extracted: '{final_obj2.get('projectName')}'")
print(f"  Input: 'To Be Extracted' → Extracted: '{final_obj2.get('featureName')}'")

print("\nExample 3 - No input names (BRD only):")
print(f"  No input → Extracted: '{final_obj3.get('projectName')}'")
print(f"  No input → Extracted: '{final_obj3.get('featureName')}'")

# Success checks
success_count = 0
if final_obj2.get('projectName') not in ['To Be Extracted', 'Unnamed Project', None]:
    print("\n✅ SUCCESS: Example 2 project name extracted from BRD!")
    success_count += 1
if final_obj2.get('featureName') not in ['To Be Extracted', 'Core Feature', None]:
    print("✅ SUCCESS: Example 2 feature name extracted from BRD!")
    success_count += 1
if final_obj3.get('projectName') not in ['To Be Extracted', 'Unnamed Project', None]:
    print("✅ SUCCESS: Example 3 project name extracted from BRD!")
    success_count += 1
if final_obj3.get('featureName') not in ['To Be Extracted', 'Core Feature', None]:
    print("✅ SUCCESS: Example 3 feature name extracted from BRD!")
    success_count += 1

print(f"\n===== Final Result: {success_count}/4 extractions successful =====")
