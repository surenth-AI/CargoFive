import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

class PlannerEngine:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_plan(self, discovery_results):
        """
        Analyzes the full discovery results to understand the workbook's structure 
        and create a multi-step processing schedule.
        """
        
        # Prepare a condensed summary of the workbook for the LLM
        workbook_summary = self._create_summary(discovery_results)
        
        prompt = f"""
        You are a Logistics Data Architect. I have scanned an Excel workbook containing complex shipping rate tables.
        
        YOUR GOAL: 
        1. Understand the purpose of each sheet and table.
        2. Group the data into logical 'Regions' or 'Trades' (e.g., Far East, Mediterranean, Intra-Asia).
        3. Identify dependencies (e.g., "Table B in Sheet 2 contains surcharges for Table A in Sheet 1").
        4. Create a step-by-step 'Execution Schedule' for our processing agent.

        --- WORKBOOK DISCOVERY SUMMARY ---
        {json.dumps(workbook_summary, indent=2)}

        --- INSTRUCTIONS ---
        Return a JSON object with this exact structure:
        {{
            "workbook_understanding": "Brief summary of what this file is (e.g., 'MSC 2024 Global Rate Contract')",
            "sheet_roles": {{
                "Sheet Name": "Role (e.g., MAIN_RATES, LOCAL_CHARGES, SURCHARGES, ARBITRARIES, INLAND, TERMS)"
            }},
            "schedule": [
                {{
                    "task_id": "Task 1",
                    "region_name": "e.g., Far East Trade",
                    "primary_sheet": "Sheet Name",
                    "primary_tables": ["Table Name 1", "Table Name 2"],
                    "context_sheets": ["Sheet Name containing surcharges or dates"],
                    "processing_instructions": "Specific guidance for this trade (e.g., 'Focus on THC and BAF extraction here')",
                    "priority": 1
                }}
            ]
        }}

        Be intelligent: If you see many sheets with similar names, group them. If you see a sheet called 'Surcharges', mark it as context for all rate tasks.
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1:
                return json.loads(text[start_idx:end_idx])
            return {}
        except Exception as e:
            print(f"Planner Agent failed: {e}")
            return {}

    def _create_summary(self, discovery_results):
        """Creates a lightweight summary of sheets and tables for the planner."""
        summary = {}
        for sheet_name, sheet_data in discovery_results.items():
            tables_info = []
            for t in sheet_data.get("tables", []):
                # We only send headers and names to save tokens
                tables_info.append({
                    "name": t.get("name"),
                    "type": t.get("type"),
                    "headers": t.get("headers", [])[:15] # First 15 headers
                })
            
            summary[sheet_name] = {
                "metadata": sheet_data.get("metadata"),
                "table_count": len(tables_info),
                "tables": tables_info
            }
        return summary

planner_engine = PlannerEngine()
