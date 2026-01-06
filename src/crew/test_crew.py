"""CrewAI Crew orchestration for test generation."""

import json
import re
from typing import Optional
from pathlib import Path

from crewai import Crew, Process

from src.agents import (
    create_parser_agent,
    create_analyzer_agent,
    create_generator_agent,
    create_reviewer_agent,
    create_github_agent,
)
from src.tasks import (
    create_parse_task,
    create_analyze_task,
    create_generate_task,
    create_review_task,
    create_github_task,
)
from src.config.settings import get_settings
from src.utils.file_handler import FileHandler, save_generated_test
from src.utils.git_utils import GitUtils, generate_pr_body
from src.models.schemas import GeneratedTest, PRMetadata, WorkflowResult


class TestGeneratorCrew:
    """Orchestrates the multi-agent test generation workflow."""
    
    def __init__(
        self,
        output_dir: str = "output/generated_tests",
        verbose: bool = True
    ):
        """Initialize the TestGeneratorCrew.
        
        Args:
            output_dir: Directory for generated test files
            verbose: Whether to enable verbose output
        """
        self.output_dir = output_dir
        self.verbose = verbose
        self.settings = get_settings()
        self.file_handler = FileHandler()
        
        # Initialize agents
        self._init_agents()
    
    def _init_agents(self):
        """Initialize all agents."""
        if self.verbose:
            print("🤖 Initializing agents...")
        
        self.parser_agent = create_parser_agent()
        self.analyzer_agent = create_analyzer_agent()
        self.generator_agent = create_generator_agent()
        self.reviewer_agent = create_reviewer_agent()
        self.github_agent = create_github_agent()
        
        if self.verbose:
            print("✅ Agents initialized")
    
    def generate_tests(
        self,
        scenario_text: str,
        push_to_github: bool = False,
        base_branch: str = "main"
    ) -> WorkflowResult:
        """Run the complete test generation workflow.
        
        Args:
            scenario_text: Raw test scenario text
            push_to_github: Whether to push to GitHub and create PR
            base_branch: Target branch for PR
            
        Returns:
            WorkflowResult with generated tests and PR info
        """
        result = WorkflowResult(
            input_file="inline",
            scenarios_count=1,
            generated_tests=[],
            success=True
        )
        
        try:
            # Step 1: Create tasks for test generation
            if self.verbose:
                print("\n📋 Creating test generation tasks...")
            
            parse_task = create_parse_task(self.parser_agent, scenario_text)
            analyze_task = create_analyze_task(
                self.analyzer_agent, 
                context=[parse_task]
            )
            generate_task = create_generate_task(
                self.generator_agent,
                context=[analyze_task]
            )
            review_task = create_review_task(
                self.reviewer_agent,
                context=[generate_task]
            )
            
            # Step 2: Create and run the crew
            if self.verbose:
                print("🚀 Starting test generation crew...")
            
            crew = Crew(
                agents=[
                    self.parser_agent,
                    self.analyzer_agent,
                    self.generator_agent,
                    self.reviewer_agent,
                ],
                tasks=[
                    parse_task,
                    analyze_task,
                    generate_task,
                    review_task,
                ],
                process=Process.sequential,
                verbose=self.verbose,
            )
            
            crew_result = crew.kickoff()
            
            # Step 3: Extract and save the generated code
            if self.verbose:
                print("\n💾 Processing generated code...")
            
            generated_test = self._process_crew_result(crew_result, scenario_text)
            
            if generated_test:
                # Save the test file
                saved_files = self._save_generated_files(generated_test)
                result.generated_tests.append(generated_test)
                
                if self.verbose:
                    print(f"✅ Saved {len(saved_files)} file(s)")
                
                # Step 4: Push to GitHub if requested - use GitHub Agent
                if push_to_github:
                    if self.verbose:
                        print("\n🐙 Running GitHub Agent for branch creation and PR...")
                    
                    pr_metadata = self._run_github_agent(
                        files=saved_files,
                        feature_name=self._extract_feature_name(scenario_text),
                        base_branch=base_branch
                    )
                    result.pr_metadata = pr_metadata
            else:
                result.success = False
                result.errors.append("Failed to generate test code")
                
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            if self.verbose:
                print(f"❌ Error: {e}")
        
        return result
    
    def _process_crew_result(
        self,
        crew_result,
        scenario_text: str
    ) -> Optional[GeneratedTest]:
        """Process the crew result and extract generated code.
        
        Args:
            crew_result: Result from the crew
            scenario_text: Original scenario text
            
        Returns:
            GeneratedTest object or None
        """
        try:
            # Get the final output (from reviewer)
            raw_output = str(crew_result)
            
            # Try to extract code from JSON response
            code = self._extract_code_from_result(raw_output)
            
            if not code:
                # Maybe the result is just the code
                code = raw_output
            
            # Generate filename from scenario
            feature_name = self._extract_feature_name(scenario_text)
            filename = self._generate_filename(feature_name)
            
            # Check if it's valid Python
            is_valid = self._validate_python_code(code)
            
            return GeneratedTest(
                filename=filename,
                content=code,
                test_count=1,
                is_valid=is_valid,
                review_notes=["Generated by AI Test Generator"]
            )
            
        except Exception as e:
            if self.verbose:
                print(f"Error processing result: {e}")
            return None
    
    def _extract_code_from_result(self, result: str) -> Optional[str]:
        """Extract Python code from the crew result.
        
        Args:
            result: Raw result string
            
        Returns:
            Extracted Python code or None
        """
        # Try to parse as JSON and extract final_code
        try:
            # Find JSON block in the result
            json_match = re.search(r'```json\s*\n?\{.*?\}\s*\n?```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Remove markdown code fence
                json_str = re.sub(r'```json\s*\n?', '', json_str)
                json_str = re.sub(r'\n?```', '', json_str)
                
                try:
                    data = json.loads(json_str)
                    if "final_code" in data:
                        code = data["final_code"]
                        # Handle escaped newlines
                        code = code.replace('\\n', '\n')
                        code = code.replace('\\"', '"')
                        return code.strip()
                except json.JSONDecodeError:
                    pass
            
            # Try direct JSON parsing
            json_match = re.search(r'\{[^{}]*"final_code"[^{}]*\}', result, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if "final_code" in data:
                        code = data["final_code"]
                        code = code.replace('\\n', '\n')
                        return code.strip()
                except json.JSONDecodeError:
                    pass
                    
        except Exception:
            pass
        
        # Try to extract final_code value directly using regex
        final_code_match = re.search(
            r'"final_code"\s*:\s*["\']+(.*?)["\']+\s*[,}]',
            result,
            re.DOTALL
        )
        if final_code_match:
            code = final_code_match.group(1)
            # Unescape the code
            code = code.replace('\\n', '\n')
            code = code.replace('\\"', '"')
            code = code.replace("\\'", "'")
            return code.strip()
        
        # Try to extract code block
        code_match = re.search(
            r'```python\n(.*?)```',
            result,
            re.DOTALL
        )
        if code_match:
            return code_match.group(1).strip()
        
        # Check if the result looks like Python code
        if "import pytest" in result or "def test_" in result:
            # Clean up any markdown artifacts
            code = result.replace("```python", "").replace("```", "")
            code = re.sub(r'```json.*?```', '', code, flags=re.DOTALL)
            return code.strip()
        
        return None
    
    def _extract_feature_name(self, scenario_text: str) -> str:
        """Extract feature name from scenario text.
        
        Args:
            scenario_text: Raw scenario text
            
        Returns:
            Feature name
        """
        # Try to find "Feature:" line
        feature_match = re.search(r'Feature:\s*(.+)', scenario_text)
        if feature_match:
            return feature_match.group(1).strip()
        
        # Try first line
        first_line = scenario_text.strip().split('\n')[0]
        return first_line[:50].strip()
    
    def _generate_filename(self, feature_name: str) -> str:
        """Generate a test filename from feature name.
        
        Args:
            feature_name: Feature name
            
        Returns:
            Valid Python filename
        """
        # Convert to snake_case
        name = feature_name.lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)
        name = name.strip('_')
        
        return f"test_{name}.py"
    
    def _validate_python_code(self, code: str) -> bool:
        """Validate that the code is valid Python.
        
        Args:
            code: Python code string
            
        Returns:
            True if valid
        """
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
    
    def _save_generated_files(self, test: GeneratedTest) -> list[str]:
        """Save generated test files to disk.
        
        Args:
            test: GeneratedTest object
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        # Ensure output directory exists
        self.file_handler.ensure_directory(self.output_dir)
        
        # Save main test file
        test_path = save_generated_test(
            self.output_dir,
            test.filename,
            test.content
        )
        saved_files.append(test_path)
        
        # Save page object if present
        if test.page_object_content and test.page_object_filename:
            po_path = save_generated_test(
                self.output_dir,
                test.page_object_filename,
                test.page_object_content
            )
            saved_files.append(po_path)
        
        return saved_files
    
    def _push_to_github(
        self,
        files: list[str],
        feature_name: str,
        base_branch: str
    ) -> PRMetadata:
        """Push generated files to GitHub and create PR.
        
        Args:
            files: List of file paths to commit
            feature_name: Feature name for PR
            base_branch: Target branch
            
        Returns:
            PRMetadata with result
        """
        git_utils = GitUtils()
        
        # Check if we're in a git repo
        if not git_utils.is_git_repo():
            return PRMetadata(
                branch_name="",
                title="",
                body="",
                files=files,
                success=False,
                error_message="Not a Git repository"
            )
        
        # Generate branch name
        branch_name = git_utils.generate_branch_name(
            suffix=re.sub(r'[^a-z0-9]', '-', feature_name.lower()[:20])
        )
        
        # Create branch
        success, message = git_utils.create_branch(branch_name)
        if not success:
            return PRMetadata(
                branch_name=branch_name,
                title="",
                body="",
                files=files,
                success=False,
                error_message=message
            )
        
        if self.verbose:
            print(f"  ✅ Created branch: {branch_name}")
        
        # Stage and commit files
        success, message = git_utils.stage_files(files)
        if not success:
            return PRMetadata(
                branch_name=branch_name,
                title="",
                body="",
                files=files,
                success=False,
                error_message=message
            )
        
        commit_message = f"Add auto-generated tests for {feature_name}"
        success, commit_hash = git_utils.commit(commit_message)
        if not success:
            return PRMetadata(
                branch_name=branch_name,
                title="",
                body="",
                files=files,
                success=False,
                error_message=commit_hash
            )
        
        if self.verbose:
            print(f"  ✅ Committed: {commit_hash}")
        
        # Push branch
        success, message = git_utils.push(branch_name)
        if not success:
            return PRMetadata(
                branch_name=branch_name,
                title="",
                body="",
                files=files,
                success=False,
                error_message=message
            )
        
        if self.verbose:
            print(f"  ✅ Pushed to origin")
        
        # Create PR
        pr_title = f"Add tests for {feature_name}"
        pr_body = generate_pr_body(feature_name, 1, files)
        
        success, pr_url = git_utils.create_pull_request(
            title=pr_title,
            body=pr_body,
            base_branch=base_branch
        )
        
        if success:
            if self.verbose:
                print(f"  ✅ PR created: {pr_url}")
            
            # Extract PR number from URL
            pr_number = None
            pr_match = re.search(r'/pull/(\d+)', pr_url)
            if pr_match:
                pr_number = int(pr_match.group(1))
            
            return PRMetadata(
                branch_name=branch_name,
                title=pr_title,
                body=pr_body,
                base_branch=base_branch,
                files=files,
                pr_url=pr_url,
                pr_number=pr_number,
                success=True
            )
        else:
            return PRMetadata(
                branch_name=branch_name,
                title=pr_title,
                body=pr_body,
                files=files,
                success=False,
                error_message=pr_url
            )

    def _run_github_agent(
        self,
        files: list[str],
        feature_name: str,
        base_branch: str
    ) -> PRMetadata:
        """Run the GitHub Agent to push code and create PR using CrewAI.
        
        Args:
            files: List of file paths to commit
            feature_name: Feature name for the PR
            base_branch: Target branch for the PR
            
        Returns:
            PRMetadata with result
        """
        if self.verbose:
            print("  🤖 GitHub Agent: Starting Git operations...")
        
        # Create the GitHub task for the agent
        github_task = create_github_task(
            agent=self.github_agent,
            files=files,
            feature_name=feature_name,
            base_branch=base_branch
        )
        
        # Create a mini crew with just the GitHub agent
        github_crew = Crew(
            agents=[self.github_agent],
            tasks=[github_task],
            process=Process.sequential,
            verbose=self.verbose,
        )
        
        try:
            # Run the GitHub agent
            crew_result = github_crew.kickoff()
            
            if self.verbose:
                print(f"  📝 GitHub Agent Result: {str(crew_result)[:200]}")
            
            # Parse the result to extract PR information
            result_str = str(crew_result)
            
            # Try to extract PR URL from result
            pr_url_match = re.search(r'https://github\.com/[^\s]+/pull/\d+', result_str)
            pr_url = pr_url_match.group(0) if pr_url_match else None
            
            # Extract branch name
            branch_match = re.search(r'test/auto-generated[^\s]*', result_str)
            branch_name = branch_match.group(0) if branch_match else f"test/auto-generated-{feature_name}"
            
            if pr_url:
                pr_number = None
                pr_num_match = re.search(r'/pull/(\d+)', pr_url)
                if pr_num_match:
                    pr_number = int(pr_num_match.group(1))
                
                return PRMetadata(
                    branch_name=branch_name,
                    title=f"Add tests for {feature_name}",
                    body=generate_pr_body(feature_name, 1, files),
                    base_branch=base_branch,
                    files=files,
                    pr_url=pr_url,
                    pr_number=pr_number,
                    success=True
                )
            else:
                # Fallback to direct method if agent didn't return PR URL
                if self.verbose:
                    print("  ⚠️ GitHub Agent didn't return PR URL, falling back to direct method...")
                return self._push_to_github(files, feature_name, base_branch)
                
        except Exception as e:
            if self.verbose:
                print(f"  ❌ GitHub Agent error: {e}, falling back to direct method...")
            # Fallback to the direct method
            return self._push_to_github(files, feature_name, base_branch)

    def generate_from_file(self, input_file: str, push_to_github: bool = False, base_branch: str = "main") -> WorkflowResult:
        """Generate tests from a scenario file."""
        scenario_text = self.file_handler.read_file(input_file)
        if scenario_text is None:
            return WorkflowResult(input_file=input_file, scenarios_count=0, success=False, errors=[f"Could not read file: {input_file}"])
        result = self.generate_tests(scenario_text=scenario_text, push_to_github=push_to_github, base_branch=base_branch)
        result.input_file = input_file
        return result

