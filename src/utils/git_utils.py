"""Git utility functions for repository operations."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from src.config.settings import get_settings


class GitUtils:
    """Utility class for Git operations."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize GitUtils with repository path.
        
        Args:
            repo_path: Path to the Git repository (default: current directory)
        """
        self.repo_path = Path(repo_path).resolve()
        self._repo = None
    
    @property
    def repo(self):
        """Get the Git repository object."""
        if self._repo is None:
            from git import Repo
            self._repo = Repo(self.repo_path)
        return self._repo
    
    def is_git_repo(self) -> bool:
        """Check if the path is a Git repository."""
        try:
            from git import Repo
            from git.exc import InvalidGitRepositoryError
            
            Repo(self.repo_path)
            return True
        except InvalidGitRepositoryError:
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        try:
            return self.repo.active_branch.name
        except Exception:
            return None
    
    def is_dirty(self) -> bool:
        """Check if the repository has uncommitted changes."""
        try:
            return self.repo.is_dirty()
        except Exception:
            return False
    
    def get_untracked_files(self) -> list[str]:
        """Get list of untracked files."""
        try:
            return self.repo.untracked_files
        except Exception:
            return []
    
    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Create and checkout a new branch.
        
        Args:
            branch_name: Name of the branch to create
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.repo.git.checkout("-b", branch_name)
            return True, f"Created and checked out branch: {branch_name}"
        except Exception as e:
            return False, f"Failed to create branch: {str(e)}"
    
    def generate_branch_name(self, suffix: str = "") -> str:
        """Generate a unique branch name with timestamp.
        
        Args:
            suffix: Optional suffix for the branch name
            
        Returns:
            Generated branch name
        """
        settings = get_settings()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        if suffix:
            return f"{settings.github.branch_prefix}-{suffix}-{timestamp}"
        return f"{settings.github.branch_prefix}-{timestamp}"
    
    def stage_files(self, files: list[str]) -> Tuple[bool, str]:
        """Stage files for commit.
        
        Args:
            files: List of file paths to stage
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.repo.index.add(files)
            return True, f"Staged {len(files)} file(s)"
        except Exception as e:
            return False, f"Failed to stage files: {str(e)}"
    
    def commit(self, message: str) -> Tuple[bool, str]:
        """Create a commit with the staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            Tuple of (success, message/hash)
        """
        try:
            commit = self.repo.index.commit(message)
            return True, commit.hexsha[:8]
        except Exception as e:
            return False, f"Failed to commit: {str(e)}"
    
    def push(self, branch_name: str, set_upstream: bool = True) -> Tuple[bool, str]:
        """Push branch to remote.
        
        Args:
            branch_name: Branch to push
            set_upstream: Whether to set upstream tracking
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if set_upstream:
                self.repo.git.push("--set-upstream", "origin", branch_name)
            else:
                self.repo.git.push("origin", branch_name)
            return True, f"Pushed {branch_name} to origin"
        except Exception as e:
            return False, f"Failed to push: {str(e)}"
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        base_branch: str = "main"
    ) -> Tuple[bool, str]:
        """Create a Pull Request using GitHub CLI.
        
        Args:
            title: PR title
            body: PR description
            base_branch: Target branch
            
        Returns:
            Tuple of (success, PR URL or error message)
        """
        settings = get_settings()
        
        if not settings.github.is_gh_installed():
            return False, "GitHub CLI (gh) is not installed"
        
        if not settings.github.is_authenticated():
            return False, "GitHub CLI is not authenticated"
        
        try:
            full_title = f"{settings.github.pr_title_prefix}{title}"
            
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--base", base_branch,
                    "--title", full_title,
                    "--body", body,
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "PR creation timed out"
        except Exception as e:
            return False, str(e)
    
    def get_remote_url(self) -> Optional[str]:
        """Get the remote origin URL."""
        try:
            return self.repo.remotes.origin.url
        except Exception:
            return None
    
    def checkout_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Checkout an existing branch.
        
        Args:
            branch_name: Branch to checkout
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.repo.git.checkout(branch_name)
            return True, f"Checked out branch: {branch_name}"
        except Exception as e:
            return False, f"Failed to checkout: {str(e)}"
    
    def get_status_summary(self) -> dict:
        """Get a summary of the repository status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "is_repo": self.is_git_repo(),
            "current_branch": self.get_current_branch(),
            "is_dirty": self.is_dirty(),
            "untracked_count": len(self.get_untracked_files()),
            "remote_url": self.get_remote_url(),
        }


def generate_pr_body(
    feature_name: str,
    scenarios_count: int,
    files: list[str]
) -> str:
    """Generate a PR description body.
    
    Args:
        feature_name: Name of the feature being tested
        scenarios_count: Number of test scenarios generated
        files: List of generated files
        
    Returns:
        Formatted PR body
    """
    files_list = "\n".join(f"- `{f}`" for f in files)
    
    return f"""## Auto-Generated Test Cases

This PR was automatically generated by the AI Test Case Generator.

### Summary
- **Feature**: {feature_name}
- **Scenarios**: {scenarios_count} test scenario(s)
- **Files Generated**: {len(files)}

### Generated Files
{files_list}

### How to Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run the generated tests
pytest {' '.join(files)} -v
```

### Notes
- These tests were generated from text scenarios using AI
- Please review the selectors and adjust if needed for your application
- Consider adding these tests to your CI/CD pipeline

---
*Generated by AI Test Case Generator with CrewAI + Ollama*
"""

