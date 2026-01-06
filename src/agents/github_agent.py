"""GitHub Agent - Handles Git operations and Pull Request creation for API tests."""

from crewai import Agent, LLM
from crewai.tools import tool
import subprocess
from datetime import datetime
from typing import Optional

from src.config.settings import get_settings


def create_github_agent() -> Agent:
    """Create the GitHub Agent that handles Git and PR operations.
    
    This agent is responsible for:
    - Creating feature branches for generated API tests
    - Committing generated test files
    - Pushing to remote repository
    - Creating Pull Requests via GitHub CLI
    """
    settings = get_settings()
    
    llm = LLM(
        model=settings.ollama.get_model_string(),
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )
    
    return Agent(
        role="GitHub DevOps Agent for API Tests",
        goal="""Manage Git operations and create Pull Requests for generated 
        API test code. Create properly named branches, commit with meaningful 
        messages describing the API tests, and create well-documented PRs.""",
        backstory="""You are a DevOps engineer with expertise in Git workflows 
        and GitHub automation for test automation projects. You follow best 
        practices for branch naming (feature/api-tests-*), commit messages 
        that describe the API being tested, and PR descriptions that include 
        test coverage details. You know how to use the GitHub CLI effectively 
        and can handle various Git scenarios including working with remote 
        repositories for API test projects.""",
        llm=llm,
        verbose=settings.verbose,
        allow_delegation=False,
        tools=[
            create_branch_tool(),
            commit_files_tool(),
            push_branch_tool(),
            create_pr_tool(),
            check_git_status_tool(),
        ],
    )


def create_branch_tool():
    """Create a tool for creating Git branches."""
    
    @tool
    def create_git_branch(branch_suffix: str = "") -> str:
        """Create a new Git branch for the generated API tests.
        
        Args:
            branch_suffix: Optional suffix to add to the branch name (e.g., api-name)
            
        Returns:
            The name of the created branch
        """
        from git import Repo
        from git.exc import InvalidGitRepositoryError
        
        settings = get_settings()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        if branch_suffix:
            branch_name = f"{settings.github.branch_prefix}-{branch_suffix}-{timestamp}"
        else:
            branch_name = f"{settings.github.branch_prefix}-{timestamp}"
        
        try:
            repo = Repo(".")
            
            # Ensure we're on a clean state
            if repo.is_dirty():
                return f"Error: Repository has uncommitted changes. Please commit or stash them first."
            
            # Create and checkout the new branch
            repo.git.checkout("-b", branch_name)
            
            return branch_name
            
        except InvalidGitRepositoryError:
            return "Error: Not a Git repository. Please initialize Git first."
        except Exception as e:
            return f"Error creating branch: {str(e)}"
    
    return create_git_branch


def commit_files_tool():
    """Create a tool for committing files."""
    
    @tool
    def commit_files(files: str, message: str) -> str:
        """Stage and commit API test files to Git.
        
        Args:
            files: Comma-separated list of file paths to commit
            message: Commit message describing the API tests
            
        Returns:
            Result of the commit operation
        """
        from git import Repo
        from git.exc import InvalidGitRepositoryError
        
        try:
            repo = Repo(".")
            
            # Parse file list
            file_list = [f.strip() for f in files.split(",")]
            
            # Stage files
            repo.index.add(file_list)
            
            # Commit
            commit = repo.index.commit(message)
            
            return f"Committed {len(file_list)} API test file(s) with hash {commit.hexsha[:8]}"
            
        except InvalidGitRepositoryError:
            return "Error: Not a Git repository."
        except Exception as e:
            return f"Error committing files: {str(e)}"
    
    return commit_files


def push_branch_tool():
    """Create a tool for pushing branches."""
    
    @tool
    def push_branch(branch_name: str) -> str:
        """Push the API test branch to the remote repository.
        
        Args:
            branch_name: Name of the branch to push
            
        Returns:
            Result of the push operation
        """
        from git import Repo
        from git.exc import InvalidGitRepositoryError
        
        try:
            repo = Repo(".")
            
            # Push with upstream tracking
            repo.git.push("--set-upstream", "origin", branch_name)
            
            return f"Successfully pushed API test branch '{branch_name}' to origin"
            
        except InvalidGitRepositoryError:
            return "Error: Not a Git repository."
        except Exception as e:
            return f"Error pushing branch: {str(e)}"
    
    return push_branch


def create_pr_tool():
    """Create a tool for creating Pull Requests."""
    
    @tool
    def create_pull_request(
        title: str,
        body: str,
        base_branch: str = "main"
    ) -> str:
        """Create a GitHub Pull Request for API tests using the gh CLI.
        
        Args:
            title: PR title describing the API tests
            body: PR description with test coverage details
            base_branch: Target branch for the PR (default: main)
            
        Returns:
            URL of the created PR or error message
        """
        settings = get_settings()
        
        # Check if gh CLI is available
        if not settings.github.is_gh_installed():
            return "Error: GitHub CLI (gh) is not installed. Install with: brew install gh"
        
        if not settings.github.is_authenticated():
            return "Error: GitHub CLI is not authenticated. Run: gh auth login"
        
        try:
            # Create PR using gh CLI
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--base", base_branch,
                    "--title", f"{settings.github.pr_title_prefix}{title}",
                    "--body", body,
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                return f"Pull Request for API tests created successfully: {pr_url}"
            else:
                return f"Error creating PR: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: PR creation timed out"
        except Exception as e:
            return f"Error creating PR: {str(e)}"
    
    return create_pull_request


def check_git_status_tool():
    """Create a tool for checking Git status."""
    
    @tool
    def check_git_status() -> str:
        """Check the current Git repository status for API test project.
        
        Returns:
            Current branch, status, and remote information
        """
        from git import Repo
        from git.exc import InvalidGitRepositoryError
        
        try:
            repo = Repo(".")
            
            current_branch = repo.active_branch.name
            is_dirty = repo.is_dirty()
            untracked = repo.untracked_files
            
            status = f"Branch: {current_branch}\n"
            status += f"Has uncommitted changes: {is_dirty}\n"
            status += f"Untracked files: {len(untracked)}\n"
            
            # Check remote
            try:
                remote_url = repo.remotes.origin.url
                status += f"Remote (origin): {remote_url}"
            except Exception:
                status += "Remote: No remote 'origin' configured"
            
            return status
            
        except InvalidGitRepositoryError:
            return "Error: Not a Git repository. Initialize with: git init"
        except Exception as e:
            return f"Error checking status: {str(e)}"
    
    return check_git_status
