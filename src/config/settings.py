"""Configuration settings for the AI Test Case Generator."""

from dataclasses import dataclass, field
from typing import Optional
import subprocess
import sys


@dataclass
class OllamaSettings:
    """Ollama LLM configuration."""
    
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    timeout: int = 120  # seconds
    temperature: float = 0.7

    def get_model_string(self) -> str:
        """Get the full model string for CrewAI."""
        return f"ollama/{self.model}"


@dataclass
class GitHubSettings:
    """GitHub CLI configuration."""
    
    base_branch: str = "main"
    branch_prefix: str = "test/auto-generated"
    pr_title_prefix: str = "[Auto-Generated] "
    
    @staticmethod
    def is_gh_installed() -> bool:
        """Check if GitHub CLI is installed."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if GitHub CLI is authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


@dataclass
class PlaywrightSettings:
    """Playwright test generation settings."""
    
    browser: str = "chromium"
    headless: bool = True
    base_url: str = "http://localhost:3000"
    timeout: int = 30000  # milliseconds
    
    # Test file settings
    test_class_prefix: str = "Test"
    test_method_prefix: str = "test_"


@dataclass
class OutputSettings:
    """Output configuration."""
    
    output_dir: str = "output/generated_tests"
    generate_page_objects: bool = True
    generate_fixtures: bool = True


@dataclass
class Settings:
    """Main configuration class."""
    
    ollama: OllamaSettings = field(default_factory=OllamaSettings)
    github: GitHubSettings = field(default_factory=GitHubSettings)
    playwright: PlaywrightSettings = field(default_factory=PlaywrightSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    
    # Verbose mode
    verbose: bool = True
    
    def validate(self) -> list[str]:
        """Validate settings and return list of warnings."""
        warnings = []
        
        # Check Ollama availability
        if not self._check_ollama():
            warnings.append(
                "Ollama is not running. Start it with: ollama serve"
            )
        
        return warnings
    
    def _check_ollama(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(
                f"{self.ollama.base_url}/api/tags",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, TimeoutError, Exception):
            return False
    
    def check_model_available(self) -> bool:
        """Check if the configured model is available in Ollama."""
        try:
            import urllib.request
            import json
            
            req = urllib.request.Request(
                f"{self.ollama.base_url}/api/tags",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                
                # Check if our model (or a variant) is available
                model_base = self.ollama.model.split(":")[0]
                return any(model_base in m for m in models)
        except Exception:
            return False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure_settings(
    model: Optional[str] = None,
    base_branch: Optional[str] = None,
    output_dir: Optional[str] = None,
    verbose: bool = True,
) -> Settings:
    """Configure and return settings with custom values."""
    global _settings
    
    _settings = Settings(
        ollama=OllamaSettings(
            model=model or "qwen2.5-coder:7b"
        ),
        github=GitHubSettings(
            base_branch=base_branch or "main"
        ),
        output=OutputSettings(
            output_dir=output_dir or "output/generated_tests"
        ),
        verbose=verbose,
    )
    
    return _settings

