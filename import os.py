import os
import json
from pathlib import Path
from typing import Optional

from hash_chain import Amendment, HashChain, LLMSummaryGenerator
from data_ingestion import DataIngestionPipeline

class Config:
    """Load application configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load config from file or environment"""
        config = {
            'API_HOST': os.getenv('API_HOST', '0.0.0.0'),
            'API_PORT': int(os.getenv('API_PORT', '8000')),
            'LLM_API_KEY': os.getenv('LLM_API_KEY', None),
            'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'fallback'),
            'DEFAULT_LANGUAGE': os.getenv('DEFAULT_LANGUAGE', 'pl'),
            'XML_INPUT_DIR': os.getenv('XML_INPUT_DIR', './xml_files'),
            'JSON_OUTPUT_DIR': os.getenv('JSON_OUTPUT_DIR', './data'),
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
        }
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except json.JSONDecodeError:
                pass
        
        return config
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)


class LegalActTrackerApp:
    """Main application class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_generator: Optional[LLMSummaryGenerator] = None
        self.pipeline: Optional[DataIngestionPipeline] = None
        
        self._init_llm()
        self._init_pipeline()
        self._create_directories()
    
    def _init_llm(self):
        """Initialize LLM"""
        api_key = self.config.get('LLM_API_KEY')
        if api_key:
            self.llm_generator = LLMSummaryGenerator(api_key=api_key)
        else:
            self.llm_generator = LLMSummaryGenerator()
    
    def _init_pipeline(self):
        """Initialize pipeline"""
        self.pipeline = DataIngestionPipeline(llm_generator=self.llm_generator)
    
    def _create_directories(self):
        """Create necessary directories"""
        for directory in [
            self.config.get('XML_INPUT_DIR'),
            self.config.get('JSON_OUTPUT_DIR')
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MAIN APPLICATION - DEBUG TEST")
    print("="*70)
    
    # TEST 1: Config loading
    print("\n✓ TEST 1: Config Loading")
    try:
        config = Config()
        print("  ✓ Config loaded")
        print(f"  ✓ API Host: {config.get('API_HOST')}")
        print(f"  ✓ API Port: {config.get('API_PORT')}")
        print(f"  ✓ LLM Provider: {config.get('LLM_PROVIDER')}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 2: App initialization
    print("\n✓ TEST 2: App Initialization")
    try:
        app = LegalActTrackerApp(config)
        print("  ✓ App initialized")
        print("  ✓ LLM generator ready")
        print("  ✓ Pipeline ready")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 3: Directory creation
    print("\n✓ TEST 3: Directory Creation")
    try:
        xml_dir = config.get('XML_INPUT_DIR')
        json_dir = config.get('JSON_OUTPUT_DIR')
        
        assert Path(xml_dir).exists(), f"{xml_dir} not created"
        assert Path(json_dir).exists(), f"{json_dir} not created"
        
        print(f"  ✓ {xml_dir} exists")
        print(f"  ✓ {json_dir} exists")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 4: Full workflow
    print("\n✓ TEST 4: Full Workflow")
    try:
        # Create amendment
        amendment = Amendment(
            content="Artykuł 1: Niniejszym ustawą",
            change_type="substantive",
            author="Test",
            llm_generator=app.llm_generator
        )
        
        # Create chain
        chain = HashChain("TEST-ACT", "Test Act", llm_generator=app.llm_generator)
        chain.add_amendment(amendment)
        
        # Save
        app.pipeline.save_chain_to_json(chain, "test_output.json")
        
        assert Path("test_output.json").exists()
        print("  ✓ Full workflow completed")
        print("  ✓ Amendment created")
        print("  ✓ Chain created")
        print("  ✓ Chain saved to JSON")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    print("\n" + "="*70)
    print("✓ ALL MAIN APP TESTS PASSED!")
    print("="*70 + "\n")
