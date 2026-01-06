"""Main entry point for the AI Test Case Generator.

Usage:
    python -m src.main --input input/scenarios.txt --output output/generated_tests/
    python -m src.main --input input/scenarios.txt --push-pr
    python -m src.main --input input/scenarios.txt --push-pr --base-branch develop
"""

import argparse
import sys
from pathlib import Path

from src.config.settings import get_settings, configure_settings
from src.crew.test_crew import TestGeneratorCrew


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║           AI Test Case Generator with CrewAI                  ║
║           Powered by Ollama (Local LLM)                       ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_prerequisites() -> bool:
    """Check that all prerequisites are met.
    
    Returns:
        True if all prerequisites are met
    """
    settings = get_settings()
    issues = []
    
    # Check Ollama
    if not settings._check_ollama():
        issues.append(
            "❌ Ollama is not running.\n"
            "   Start it with: ollama serve\n"
            "   Then pull a model: ollama pull qwen2.5-coder:7b"
        )
    else:
        print("✅ Ollama is running")
        
        # Check model
        if not settings.check_model_available():
            issues.append(
                f"⚠️  Model '{settings.ollama.model}' may not be available.\n"
                f"   Pull it with: ollama pull {settings.ollama.model}"
            )
        else:
            print(f"✅ Model '{settings.ollama.model}' is available")
    
    if issues:
        print("\n⚠️  Prerequisites check failed:")
        for issue in issues:
            print(f"\n{issue}")
        return False
    
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate Playwright test cases from text scenarios using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate tests from a scenario file:
    python -m src.main --input input/scenarios.txt
    
  Generate tests with custom output directory:
    python -m src.main --input input/scenarios.txt --output tests/generated/
    
  Generate tests and create a GitHub PR:
    python -m src.main --input input/scenarios.txt --push-pr
    
  Generate tests with a different Ollama model:
    python -m src.main --input input/scenarios.txt --model llama3.1:8b
        """
    )
    
    # Input/Output
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input scenario file"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="output/generated_tests",
        help="Output directory for generated tests (default: output/generated_tests)"
    )
    
    # GitHub options
    parser.add_argument(
        "--push-pr",
        action="store_true",
        help="Push generated tests to GitHub and create a Pull Request"
    )
    
    parser.add_argument(
        "--base-branch",
        default="main",
        help="Target branch for the PR (default: main)"
    )
    
    # LLM options
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model to use (default: qwen2.5-coder:7b)"
    )
    
    # Other options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose output (default: True)"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Disable verbose output"
    )
    
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip prerequisite checks"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()
    
    # Print banner
    if not args.quiet:
        print_banner()
    
    # Determine verbosity
    verbose = args.verbose and not args.quiet
    
    # Configure settings
    configure_settings(
        model=args.model,
        base_branch=args.base_branch,
        output_dir=args.output,
        verbose=verbose,
    )
    
    # Check prerequisites
    if not args.skip_checks:
        if verbose:
            print("🔍 Checking prerequisites...\n")
        
        if not check_prerequisites():
            print("\n💡 Fix the issues above and try again.")
            print("   Or use --skip-checks to bypass (not recommended)")
            sys.exit(1)
        
        if verbose:
            print()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)
    
    if verbose:
        print(f"📄 Input file: {args.input}")
        print(f"📁 Output directory: {args.output}")
        if args.push_pr:
            print(f"🐙 Will create PR targeting: {args.base_branch}")
        print()
    
    # Create and run the crew
    try:
        crew = TestGeneratorCrew(
            output_dir=args.output,
            verbose=verbose
        )
        
        result = crew.generate_from_file(
            input_file=args.input,
            push_to_github=args.push_pr,
            base_branch=args.base_branch
        )
        
        # Print results
        print("\n" + "=" * 60)
        
        if result.success:
            print("✅ Test generation completed successfully!")
            print()
            
            # Show generated files
            if result.generated_tests:
                print("📁 Generated files:")
                for test in result.generated_tests:
                    status = "✓" if test.is_valid else "⚠"
                    print(f"   {status} {args.output}/{test.filename}")
            
            # Show PR info
            if result.pr_metadata and result.pr_metadata.success:
                print()
                print("🔗 Pull Request created:")
                print(f"   {result.pr_metadata.pr_url}")
            elif result.pr_metadata and not result.pr_metadata.success:
                print()
                print(f"⚠️  PR creation failed: {result.pr_metadata.error_message}")
            
            # Show how to run tests
            print()
            print("🚀 To run the generated tests:")
            print(f"   pytest {args.output}/ -v")
            
        else:
            print("❌ Test generation failed!")
            for error in result.errors:
                print(f"   Error: {error}")
            sys.exit(1)
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

