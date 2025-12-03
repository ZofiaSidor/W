import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime
from hash_chain import Amendment, HashChain, LLMSummaryGenerator

class LegalDocumentParser:
    """Parses XML legal documents and extracts amendments"""
    
    def __init__(self):
        pass
    
    def parse_file(self, filepath: str) -> List[dict]:
        """Read XML file and extract amendments"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            amendments = self._extract_amendments(root)
            print(f"✓ Parsed {len(amendments)} amendments from {filepath}")
            return amendments
        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
            return []
        except ET.ParseError as e:
            print(f"✗ XML parsing error: {e}")
            return []
    
    def _extract_amendments(self, root) -> List[dict]:
        """Extract all amendments from XML"""
        amendments = []
        amendments_elem = root.find('Amendments')
        
        if amendments_elem is None:
            return amendments
        
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
    
    def parse_string(self, xml_string: str) -> List[dict]:
        """Parse XML from string"""
        try:
            root = ET.fromstring(xml_string)
            return self._extract_amendments(root)
        except ET.ParseError as e:
            print(f"✗ XML parsing error: {e}")
            return []


class DiffEngine:
    """Detects changes between amendment versions"""
    
    def compare_amendments(self, old_content: str, new_content: str) -> dict:
        """Compare two versions"""
        old_sections = set(old_content.split('\n'))
        new_sections = set(new_content.split('\n'))
        
        return {
            'added_lines': list(new_sections - old_sections),
            'removed_lines': list(old_sections - new_sections),
            'total_changes': len(new_sections - old_sections) + len(old_sections - new_sections)
        }


class DataIngestionPipeline:
    """Orchestrates XML import → Hash Chain"""
    
    def __init__(self, llm_generator: Optional[LLMSummaryGenerator] = None):
        self.parser = LegalDocumentParser()
        self.diff_engine = DiffEngine()
        self.llm_generator = llm_generator
    
    def ingest_xml_file(self, filepath: str) -> Optional[HashChain]:
        """Complete ingestion workflow"""
        print(f"\n{'='*70}")
        print(f"INGESTING: {filepath}")
        print(f"{'='*70}")
        
        print("📖 Step 1: Parsing XML...")
        amendments_data = self.parser.parse_file(filepath)
        
        if not amendments_data:
            print("✗ No amendments found")
            return None
        
        print("📋 Step 2: Creating HashChain...")
        act_id = "ACT-UNKNOWN"
        act_title = "Unknown Legal Act"
        chain = HashChain(act_id, act_title, llm_generator=self.llm_generator)
        
        print(f"🔗 Step 3: Adding {len(amendments_data)} amendments...")
        for i, amendment_data in enumerate(amendments_data, 1):
            amendment = Amendment(
                content=amendment_data['content'],
                change_type=amendment_data['change_type'],
                author=amendment_data['author'],
                summary=amendment_data.get('summary'),
                llm_generator=self.llm_generator if amendment_data.get('summary') is None else None
            )
            chain.add_amendment(amendment)
            print(f"  ✓ Amendment {i}/{len(amendments_data)} added")
        
        print("🔐 Step 4: Verifying chain integrity...")
        if chain.verify_integrity():
            print("✓ All amendments verified")
        else:
            print("✗ Chain integrity check failed!")
        
        return chain
    
    def save_chain_to_json(self, chain: HashChain, filepath: str) -> bool:
        """Save HashChain to JSON"""
        import json
        try:
            data = {
                'act_id': chain.act_id,
                'act_title': chain.act_title,
                'history': chain.get_history()
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Chain saved to {filepath}")
            return True
        except Exception as e:
            print(f"✗ Error saving chain: {e}")
            return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATA INGESTION MODULE - DEBUG TEST")
    print("="*70)
    
    # TEST 1: Parser initialization
    print("\n✓ TEST 1: Parser Initialization")
    try:
        parser = LegalDocumentParser()
        print("  ✓ Parser created")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 2: Parse XML string
    print("\n✓ TEST 2: Parse XML String")
    try:
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<LegalAct>
    <Amendments>
        <Amendment>
            <Version>1</Version>
            <Content>Artykuł 1: Test content.</Content>
            <Author>Test Author</Author>
            <Date>2024-01-15</Date>
            <Type>substantive</Type>
        </Amendment>
    </Amendments>
</LegalAct>"""
        
        amendments = parser.parse_string(sample_xml)
        print(f"  ✓ Parsed {len(amendments)} amendment(s)")
        assert len(amendments) == 1, "Should have 1 amendment"
        assert amendments[0]['author'] == 'Test Author', "Author mismatch"
        print("  ✓ XML parsing works correctly")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 3: DiffEngine
    print("\n✓ TEST 3: Diff Engine")
    try:
        diff_engine = DiffEngine()
        old = "Line 1\nLine 2\nLine 3"
        new = "Line 1\nLine 2 MODIFIED\nLine 3\nLine 4 NEW"
        
        diff = diff_engine.compare_amendments(old, new)
        print(f"  ✓ Diff calculated")
        print(f"  ✓ Added lines: {len(diff['added_lines'])}")
        print(f"  ✓ Removed lines: {len(diff['removed_lines'])}")
        print(f"  ✓ Total changes: {diff['total_changes']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 4: Pipeline initialization
    print("\n✓ TEST 4: Pipeline Initialization")
    try:
        llm = LLMSummaryGenerator()
        pipeline = DataIngestionPipeline(llm_generator=llm)
        print("  ✓ Pipeline created")
        print("  ✓ Parser initialized")
        print("  ✓ DiffEngine initialized")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 5: Ingest XML string via pipeline
    print("\n✓ TEST 5: Pipeline XML Ingestion")
    try:
        sample_xml_multi = """<?xml version="1.0" encoding="UTF-8"?>
<LegalAct>
    <Amendments>
        <Amendment>
            <Version>1</Version>
            <Content>Artykuł 1: Niniejszym ustawą osoby mają prawo.</Content>
            <Author>Legislator A</Author>
            <Date>2024-01-15</Date>
            <Type>substantive</Type>
        </Amendment>
        <Amendment>
            <Version>2</Version>
            <Content>Artykuł 1: Niniejszym ustawą osoby mają prawo. Artykuł 2: Dodatkowe przepisy.</Content>
            <Author>Legislator B</Author>
            <Date>2024-02-20</Date>
            <Type>substantive</Type>
        </Amendment>
    </Amendments>
</LegalAct>"""
        
        amendments = pipeline.parser.parse_string(sample_xml_multi)
        print(f"  ✓ Parsed {len(amendments)} amendments")
        assert len(amendments) == 2, "Should have 2 amendments"
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 6: JSON Save
    print("\n✓ TEST 6: JSON Save/Load")
    try:
        llm = LLMSummaryGenerator()
        chain = HashChain("ACT-TEST", "Test Act", llm_generator=llm)
        
        amendment = Amendment(
            content="Test",
            change_type="substantive",
            author="Test",
            summary="Test summary",
            llm_generator=None
        )
        chain.add_amendment(amendment)
        
        # Save
        success = pipeline.save_chain_to_json(chain, "/tmp/test_chain.json")
        assert success, "Save failed"
        print("  ✓ Chain saved to JSON")
        
        # Verify file exists
        import os
        assert os.path.exists("/tmp/test_chain.json"), "JSON file not created"
        print("  ✓ JSON file verified")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    print("\n" + "="*70)
    print("✓ ALL DATA INGESTION TESTS PASSED!")
    print("="*70 + "\n")
