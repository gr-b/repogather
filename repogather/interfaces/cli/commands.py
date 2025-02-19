from pathlib import Path
from dataclasses import asdict
from ...domain.models import GatherOptions, AnalysisOptions
from ...application.use_cases import GatherRepositoryUseCase, AnalyzeRepositoryUseCase
from ...application.output import OutputService, ClipboardOutput
from ...core.repository import RepositoryService
from ...core.analysis import AnalysisService
from ...core.token_counter import TokenCounter
from ...core.file_filter import FileFilter
from ...core.openai import OpenAIClient

def create_gather_options(args) -> GatherOptions:
    """Create GatherOptions from command line arguments."""
    return GatherOptions(
        include_tests=args.include_tests,
        include_config=args.include_config,
        include_ecosystem=args.include_ecosystem,
        include_gitignored=args.include_gitignored,
        exclude_patterns=args.exclude
    )

def create_analysis_options(args) -> AnalysisOptions:
    """Create AnalysisOptions from command line arguments."""
    gather_options = create_gather_options(args)
    return AnalysisOptions(
        **asdict(gather_options),
        query=args.query,
        model=args.model,
        relevance_threshold=args.relevance_threshold
    )

def get_services():
    """Create and configure all required services."""
    file_filter = FileFilter()
    token_counter = TokenCounter()
    openai_client = OpenAIClient()
    
    repo_service = RepositoryService(file_filter, token_counter)
    analysis_service = AnalysisService(openai_client)
    output_service = OutputService(ClipboardOutput())
    
    return repo_service, analysis_service, output_service

async def handle_gather(args) -> None:
    """Handle the gather command."""
    repo_service, _, output_service = get_services()
    options = create_gather_options(args)
    
    use_case = GatherRepositoryUseCase(repo_service, output_service)
    await use_case.execute(args.path, options)

async def handle_analyze(args) -> None:
    """Handle the analyze command."""
    repo_service, analysis_service, output_service = get_services()
    options = create_analysis_options(args)
    
    use_case = AnalyzeRepositoryUseCase(
        repo_service, 
        analysis_service, 
        output_service
    )
    await use_case.execute(args.path, options) 