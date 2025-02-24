import os
from typing import List, Dict, Any
import argparse
from pathlib import Path
import re

import anthropic
from PyPDF2 import PdfReader
import docx
import pandas as pd

class DocumentProcessor:
    """Process various document types and extract text content."""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF files."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX files."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_excel(file_path: str) -> str:
        """Extract text from Excel files."""
        try:
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            print(f"Error extracting text from Excel {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting text from text file {file_path}: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text from a file based on its extension."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif file_extension == '.docx':
            return cls.extract_from_docx(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return cls.extract_from_excel(file_path)
        elif file_extension == '.txt':
            return cls.extract_from_txt(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""


class DocumentExtractor:
    """Identify and extract relevant sections from documents using an LLM."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def identify_relevant_sections(self, document_text: str, document_type: str) -> Dict[str, str]:
        """
        Use LLM to identify relevant sections from document text based on document type.
        Returns a dictionary of section names and their content.
        """
        # Create a prompt based on document type
        prompt = self._create_section_extraction_prompt(document_text, document_type)
        
        # Get response from Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system="You are an expert at extracting relevant banking information from documents. Extract only what's asked for in the exact format specified.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response to extract sections
        return self._parse_section_response(response.content[0].text)
    
    def _create_section_extraction_prompt(self, document_text: str, document_type: str) -> str:
        """Create a prompt for extracting relevant sections based on document type."""
        
        # Determine which sections to extract based on document type
        sections_to_extract = self._get_sections_for_document_type(document_type)
        
        prompt = f"""
        I have a {document_type} document with the following content:

        ```
        {document_text[:5000]}  # Limiting text length to avoid token limits
        ```

        Please extract the following sections from this document:
        {sections_to_extract}

        For each section, return the content in this exact format:
        <section_name>: [extracted content]
        ===END_SECTION===
        
        If a section is not found, respond with:
        <section_name>: NOT_FOUND
        ===END_SECTION===
        """
        
        return prompt
    
    def _get_sections_for_document_type(self, document_type: str) -> str:
        """Define which sections to extract based on document type."""
        sections = {
            "financial_statement": "- Balance Sheet\n- Income Statement\n- Cash Flow Statement\n- Financial Ratios",
            "credit_report": "- Credit Score\n- Payment History\n- Outstanding Debt\n- Credit Utilization",
            "business_plan": "- Executive Summary\n- Market Analysis\n- Company Description\n- Financial Projections",
            "property_appraisal": "- Property Description\n- Valuation\n- Comparable Properties\n- Market Conditions",
            "loan_application": "- Borrower Information\n- Loan Terms\n- Collateral Description\n- Purpose of Loan",
            "default": "- Summary\n- Financial Information\n- Risk Assessment\n- Recommendations"
        }
        
        return sections.get(document_type, sections["default"])
    
    def _parse_section_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response to extract sections and their content."""
        sections = {}
        pattern = r'([\w\s]+):\s*([\s\S]*?)(?:===END_SECTION===|$)'
        
        matches = re.findall(pattern, response)
        for section_name, content in matches:
            section_name = section_name.strip()
            content = content.strip()
            if content != "NOT_FOUND":
                sections[section_name] = content
        
        return sections


class MemoGenerator:
    """Generate banker's committee memo from extracted document sections."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_memo(self, extracted_sections: Dict[str, Dict[str, str]], memo_type: str) -> str:
        """
        Generate a banking memo from extracted sections.
        
        Args:
            extracted_sections: Dict mapping document filenames to their extracted sections
            memo_type: Type of memo to generate (loan_committee, investment_committee, etc.)
        
        Returns:
            Generated memo text
        """
        # Prepare data for prompt
        sections_data = ""
        for doc_name, sections in extracted_sections.items():
            sections_data += f"Document: {doc_name}\n"
            for section_name, content in sections.items():
                sections_data += f"  {section_name}: {content[:500]}...\n"  # Truncate for prompt
            sections_data += "\n"
        
        # Create prompt based on memo type
        prompt = self._create_memo_prompt(sections_data, memo_type)
        
        # Get response from Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system="You are an expert banking professional who creates clear, concise committee memos based on document extracts.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _create_memo_prompt(self, sections_data: str, memo_type: str) -> str:
        """Create a prompt for generating a memo based on the memo type."""
        memo_templates = {
            "loan_committee": """
            Create a loan committee memo with these sections:
            1. Executive Summary (brief overview of the loan request)
            2. Borrower Profile (key information about the borrower)
            3. Loan Structure (terms, amount, purpose, etc.)
            4. Financial Analysis (key metrics and assessment)
            5. Risk Assessment (identified risks and mitigations)
            6. Recommendation (clear approval/decline recommendation)
            """,
            
            "investment_committee": """
            Create an investment committee memo with these sections:
            1. Investment Overview (brief description of the investment opportunity)
            2. Market Analysis (relevant market conditions and trends)
            3. Financial Projections (expected returns, timelines)
            4. Risk Analysis (potential risks and mitigation strategies)
            5. Strategic Fit (alignment with bank's investment strategy)
            6. Recommendation (clear approval/decline recommendation)
            """,
            
            "default": """
            Create a banking committee memo with these sections:
            1. Executive Summary (overview of the request/situation)
            2. Background Information (relevant context)
            3. Financial Analysis (key financial considerations)
            4. Risk Assessment (potential risks and mitigations)
            5. Recommendation (clear recommended action)
            """
        }
        
        template = memo_templates.get(memo_type, memo_templates["default"])
        
        prompt = f"""
        Based on the following extracted document sections:
        
        {sections_data}
        
        {template}
        
        The memo should be professional, concise, and highlight the most critical information for the committee's decision-making. Use appropriate banking terminology and formatting.
        """
        
        return prompt


def main():
    parser = argparse.ArgumentParser(description="Generate a banker's memo from document sections")
    parser.add_argument("--docs_dir", required=True, help="Directory containing documents to process")
    parser.add_argument("--api_key", required=True, help="Anthropic API key")
    parser.add_argument("--memo_type", default="loan_committee", help="Type of memo to generate")
    parser.add_argument("--output", default="committee_memo.txt", help="Output file for generated memo")
    args = parser.parse_args()
    
    # Initialize processors
    doc_processor = DocumentProcessor()
    extractor = DocumentExtractor(api_key=args.api_key)
    memo_generator = MemoGenerator(api_key=args.api_key)
    
    # Process all documents in the directory
    extracted_sections = {}
    for filename in os.listdir(args.docs_dir):
        file_path = os.path.join(args.docs_dir, filename)
        if not os.path.isfile(file_path):
            continue
        
        print(f"Processing {filename}...")
        
        # Extract document text
        document_text = doc_processor.extract_text(file_path)
        if not document_text:
            print(f"Could not extract text from {filename}, skipping...")
            continue
        
        # Determine document type from filename
        # This is a simple heuristic and could be improved
        doc_type = "default"
        if "financial" in filename.lower() or "statement" in filename.lower():
            doc_type = "financial_statement"
        elif "credit" in filename.lower() or "report" in filename.lower():
            doc_type = "credit_report"
        elif "business" in filename.lower() or "plan" in filename.lower():
            doc_type = "business_plan"
        elif "property" in filename.lower() or "appraisal" in filename.lower():
            doc_type = "property_appraisal"
        elif "loan" in filename.lower() or "application" in filename.lower():
            doc_type = "loan_application"
        
        # Extract relevant sections
        sections = extractor.identify_relevant_sections(document_text, doc_type)
        extracted_sections[filename] = sections
        
        print(f"Extracted {len(sections)} sections from {filename}")
    
    # Generate memo
    print(f"Generating {args.memo_type} memo...")
    memo = memo_generator.generate_memo(extracted_sections, args.memo_type)
    
    # Save memo to file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(memo)
    
    print(f"Memo saved to {args.output}")


if __name__ == "__main__":
    main()