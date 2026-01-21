import hashlib
import json
from datetime import datetime
from typing import Optional, List

# ============================================================================
# INTEGRATION GUIDE - How to use this system with data_ingestion.py and api.py
# ============================================================================
#
# QUICK START:
# 1. This file (hash_chain.py) = Core engine for tracking amendments
# 2. data_ingestion.py = Reads XML files and feeds amendments into chain
# 3. api.py = Exposes chain via REST API for web/mobile apps
# 4. main.py = Entry point that starts everything
#
# COMPLETE WORKFLOW:
#   [XML File from ISAP] → [DataIngestionPipeline] → [Parse XML] → 
#   [Create HashChain] → [Add Amendment] → [LLM Auto-summarizes] → 
#   [Hash-chain stores immutably] → [FastAPI endpoints] → [Web UI]
#
# FILES STRUCTURE:
#   Zzzz_All/
#   ├── hash_chain.py          ← This file (core)
#   ├── data_ingestion.py      ← XML parser + pipeline
#   ├── api.py                 ← FastAPI REST endpoints
#   ├── main.py                ← Entry point
#   ├── requirements.txt       ← Dependencies
#   └── config.json            ← Configuration
#
# TO RUN:
#   $ pip install -r requirements.txt
#   $ python main.py
#   → Open http://localhost:8000
#
# ============================================================================

class LLMSummaryGenerator:
    """
    Uses an LLM to convert legal amendments into simple, plain-language summaries.
    This makes complex law changes understandable to average people.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.use_real_llm = api_key is not None
    
    def simplify(self, legal_text: str, previous_text: Optional[str] = None) -> str:
        """Convert legal text into simple language"""
        if self.use_real_llm:
            return self._call_real_llm(legal_text, previous_text)
        else:
            return self._fallback_simplify(legal_text, previous_text)
    
    def _fallback_simplify(self, legal_text: str, previous_text: Optional[str] = None) -> str:
        """Simple rule-based simplification with Polish legal dictionary"""
        simple = legal_text
        
        # POLISH LEGAL JARGON DICTIONARY (100+ terms)
        replacements = {
            # BASIC LEGAL TERMS
            'niniejszym ustawą': 'tą ustawą',
            'niezależnie od': 'mimo że',
            'niezależnie od postanowień': 'mimo przepisów',
            'zgodnie z': 'według',
            'zgodnie z artykułem': 'według artykułu',
            'w ramach': 'w granicach',
            'w zakresie': 'w granicach',
            
            # MODAL VERBS & OBLIGATIONS
            'powinien': 'musi',
            'powinna': 'musi',
            'powinno': 'musi',
            'powinni': 'muszą',
            'obowiązany': 'zobowiązany',
            'obowiązana': 'zobowiązana',
            'uprawniony': 'ma prawo',
            'uprawniona': 'ma prawo',
            
            # PRONOUNS & REFERENCES
            'wspomniany wyżej': 'wymieniony wyżej',
            'wspominany wyżej': 'wymieniony wyżej',
            'powyższy': 'wymieniony',
            'powyższa': 'wymieniona',
            'powyższe': 'wymienione',
            'w którym': 'gdzie',
            'w której': 'gdzie',
            'jego': 'tego',
            'jej': 'tego',
            
            # TIME & TEMPORAL LANGUAGE
            'następnie': 'potem',
            'wówczas': 'wtedy',
            'do dnia': 'przed',
            'od dnia': 'od',
            'przed wejściem w życie': 'zanim zacznie obowiązywać',
            'wchodzi w życie': 'zaczyna obowiązywać',
            
            # LEGISLATION & LEGAL DOCUMENTS
            'ustawa': 'prawo',
            'ustawy': 'praw',
            'artykuł': 'Art.',
            'artykułu': 'Art.',
            'sekcja': 'część',
            'paragraf': '§',
            'rozporządzenie': 'rozporządzenie',
            'przepis': 'reguła',
            'przepisy': 'reguły',
            'kodeks': 'kodeks',
            
            # RIGHTS & OBLIGATIONS
            'prawo do': 'może',
            'prawo mieć': 'może mieć',
            'prawo do udziału': 'może uczestniczyć',
            'obowiązek': 'musi',
            'zobowiązanie': 'musi',
            'odpowiedzialność': 'odpowiada za',
            'odpowiada': 'odpowiada za',
            
            # ADMINISTRATIVE & PROCEDURAL LANGUAGE
            'właściwy': 'odpowiedni',
            'właściwa': 'odpowiednia',
            'kompetentny': 'uprawniony',
            'przeprowadzić': 'zrobić',
            'wyznaczony': 'określony',
            'wyznaczona': 'określona',
            'ustalone': 'określone',
            'określona': 'wyjaśniona',
            'zawiadomić': 'powiadomić',
            'informować': 'powiadomić',
            
            # FINANCIAL & PENALTY LANGUAGE
            'grzywna': 'kara pieniężna',
            'sankcja': 'kara',
            'sankcji': 'kary',
            'karalność': 'podlega karze',
            'karny': 'z karą',
            'podatek': 'opłata rządowa',
            'opłata': 'opłata',
            
            # EXCEPTIONS & CONDITIONS
            'z wyjątkiem': 'oprócz',
            'pod warunkiem': 'jeśli',
            'warunkiem': 'wymaganiem',
            'warunki': 'wymagania',
            'zastrzeżenie': 'wyjątek',
            'zastrzeżenia': 'wyjątki',
            
            # LEGAL PERSONS & ENTITIES
            'osoba prawna': 'organizacja',
            'osób prawnych': 'organizacji',
            'osoba fizyczna': 'osoba prywatna',
            'podmiot': 'organizacja',
            'podmioty': 'organizacje',
            'jednostka': 'organizacja',
            'instytucja': 'organizacja',
            
            # EFFECTS & CONSEQUENCES
            'skutki': 'efekty',
            'skutek': 'efekt',
            'konsekwencja': 'wynik',
            'konsekwencji': 'wyniku',
            'następstwo': 'wynik',
            'bezprawnie': 'nielegalne',
            'bezprawny': 'nielegalny',
            
            # VERB FORMS & ACTIONS
            'przysługuje': 'ma prawo',
            'przysługuje prawo': 'ma prawo',
            'upoważnia': 'daje prawo',
            'upoważnia do': 'daje prawo do',
            'zabrania': 'nie pozwala',
            'zakazuje': 'nie pozwala',
            'zabrania się': 'nie wolno',
            'dopuszcza': 'pozwala',
            'dopuszcza się': 'można',
            
            # EXAMPLES & ILLUSTRATIONS
            'przykładowo': 'na przykład',
            'między innymi': 'włączając',
            'zwłaszcza': 'szczególnie',
            'oraz': 'i',
            'albo': 'lub',
            'bądź': 'lub',
            
            # NEGATION
            'nie powinien': 'nie może',
            'nie powinna': 'nie może',
            'niepodlegający': 'nie ma',
            'niewłaściwy': 'nieodpowiedni',
            'nieuprawnionym': 'bez prawa',
            
            # ENGLISH FALLBACK
            'hereby': 'tą ustawą',
            'notwithstanding': 'mimo że',
            'pursuant to': 'według',
            'aforementioned': 'wymieniony wyżej',
            'shall': 'musi',
            'wherein': 'gdzie',
            'thereof': 'tego',
            'thereupon': 'potem',
            'SECTION': 'Część',
            'ARTICLE': 'Artykuł',
        }
        
        for legal_word, simple_word in replacements.items():
            simple = simple.replace(legal_word, simple_word)
            if legal_word and legal_word[0].islower():
                capitalized = legal_word[0].upper() + legal_word[1:]
                simple = simple.replace(capitalized, simple_word.capitalize())
        
        simple = simple.replace('ARTYKUŁ', 'Artykuł')
        simple = simple.replace('CZĘŚĆ', 'Część')
        simple = simple.replace('USTAWA', 'Ustawa')
        
        if len(simple) > 200:
            simple = simple[:200].rsplit(' ', 1)[0] + '...'
        
        return simple
    
    def _call_real_llm(self, legal_text: str, previous_text: Optional[str] = None) -> str:
        """Call real LLM API (OpenAI, Claude, etc.)"""
        return "LLM API not configured yet"

# ============================================================================
# AMENDMENT CLASS
# ============================================================================

class Amendment:
    """Represents a single change to a legal act"""
    
    def __init__(self, content: str, change_type: str, author: str, 
                 summary: Optional[str] = None, llm_generator: Optional[LLMSummaryGenerator] = None):
        self.content = content
        self.change_type = change_type
        self.author = author
        self.timestamp = datetime.now().isoformat()
        
        if summary is None and llm_generator is not None:
            self.summary = llm_generator.simplify(content)
        else:
            self.summary = summary or "No summary provided"
    
    def to_dict(self) -> dict:
        """Convert amendment to dictionary"""
        return {
            'content': self.content,
            'change_type': self.change_type,
            'author': self.author,
            'summary': self.summary,
            'timestamp': self.timestamp
        }

# ============================================================================
# CHAINNODE CLASS
# ============================================================================

class ChainNode:
    """Single node in the hash chain"""
    
    def __init__(self, amendment: Amendment, parent_hash: Optional[str] = None):
        self.amendment = amendment
        self.parent_hash = parent_hash
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Create SHA-256 fingerprint"""
        data = json.dumps({
            'amendment': self.amendment.to_dict(),
            'parent_hash': self.parent_hash
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify(self) -> bool:
        """Verify hash hasn't been tampered with"""
        return self.hash == self._calculate_hash()

# ============================================================================
# HASHCHAIN CLASS
# ============================================================================

class HashChain:
    """Immutable change history using hash-chaining"""
    
    def __init__(self, act_id: str, act_title: str, llm_generator: Optional[LLMSummaryGenerator] = None):
        self.act_id = act_id
        self.act_title = act_title
        self.chain: List[ChainNode] = []
        self.llm_generator = llm_generator
    
    def add_amendment(self, amendment: Amendment) -> str:
        """Add new amendment to chain"""
        parent_hash = self.chain[-1].hash if self.chain else None
        node = ChainNode(amendment, parent_hash)
        self.chain.append(node)
        return node.hash
    
    def get_history(self) -> List[dict]:
        """Get complete amendment history"""
        return [{
            'version': i + 1,
            'hash': node.hash,
            'parent_hash': node.parent_hash,
            'amendment': node.amendment.to_dict()
        } for i, node in enumerate(self.chain)]
    
    def verify_integrity(self) -> bool:
        """Verify entire chain hasn't been tampered with"""
        for i, node in enumerate(self.chain):
            if not node.verify():
                print(f"✗ Node {i} hash mismatch!")
                return False
            if i > 0 and node.parent_hash != self.chain[i-1].hash:
                print(f"✗ Node {i} parent link broken!")
                return False
        
        print("✓ Chain integrity verified!")
        return True

if __name__ == "__main__":
    llm = LLMSummaryGenerator()
    act = HashChain("ACT-001", "Polish Civil Code Amendment", llm_generator=llm)
    
    act.add_amendment(Amendment(
        content="Artykuł 1: Niniejszym ustawą, osoby fizyczne mają prawo do ochrony danych osobowych.",
        change_type="substantive",
        author="Legislator A",
        llm_generator=llm
    ))
    
    print("\n=== LEGAL ACT CHANGE HISTORY ===")
    for entry in act.get_history():
        print(f"\n📋 Version {entry['version']}")
        print(f"👤 Author: {entry['amendment']['author']}")
        print(f"📝 Summary: {entry['amendment']['summary']}")
    
    print("\n=== INTEGRITY CHECK ===")
    act.verify_integrity()
