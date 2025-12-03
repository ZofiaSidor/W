"""Data ingestion from XML files"""

import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime
from hash_chain import Amendment, HashChain, LLMSummaryGenerator

class LegalDocumentParser:
    """Parse XML legal documents"""
    
    def parse_file(self, filepath: str) -> List[dict]:
        """Read XML file and extract amendments"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            amendments = []
            
            amendments_elem = root.find('Amendments')
            if amendments_elem:
                for amendment_elem in amendments_elem.findall('Amendment'):
                    amendment_data = {
                        'version': amendment_elem.findtext('Version', '1'),
                        'content': amendment_elem.findtext('Content', ''),
                        'author': amendment_elem.findtext('Author', 'Unknown'),
                        'date': amendment_elem.findtext('Date', datetime.now().isoformat()),
                        'change_type': amendment_elem.findtext('Type', 'substantive'),
                        'summary': amendment_elem.findtext('Summary', None),
                    }
                    amendments.append(amendment_data)
            
            return amendments
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return []


class DataIngestionPipeline:
    """Orchestrate XML import into hash chain"""
    
    def __init__(self, llm_generator: Optional[LLMSummaryGenerator] = None):
        self.parser = LegalDocumentParser()
        self.llm_generator = llm_generator
    
    def ingest_xml_file(self, filepath: str) -> Optional[HashChain]:
        """Complete ingestion workflow"""
        print(f"Ingesting: {filepath}")
        
        amendments_data = self.parser.parse_file(filepath)
        if not amendments_data:
            return None
        
        chain = HashChain("ACT-UNKNOWN", "Unknown Legal Act", llm=self.llm_generator)
        
        for amendment_data in amendments_data:
            amendment = Amendment(
                content=amendment_data['content'],
                change_type=amendment_data['change_type'],
                author=amendment_data['author'],
                summary=amendment_data.get('summary'),
                llm=self.llm_generator
            )
            chain.add_amendment(amendment)
        
        chain.verify_integrity()
        return chain
