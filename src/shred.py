#!/usr/bin/env python3
"""
PPTX Shredder - Transform PowerPoint presentations into LLM-optimized markdown
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.logging import RichHandler
import logging

from intelligent_extractor import IntelligentPPTXExtractor
from intelligent_formatter import IntelligentMarkdownFormatter
from utils import is_pptx_file, sanitize_filename

# Set up rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("pptx_shredder")

console = Console()

@click.command()
@click.argument('input_files', nargs=-1, type=click.Path(), required=False)
@click.option('--input-dir', '-i', default='input', 
              help='Input directory to scan for PPTX files (default: input/)')
@click.option('--output-dir', '-o', default='output', 
              help='Output directory for generated markdown files (default: output/)')
@click.option('--strategy', default='instructional',
              type=click.Choice(['instructional', 'sequential', 'module-based']),
              help='Chunking strategy to use')
@click.option('--chunk-size', default=1500, type=int,
              help='Maximum tokens per chunk')
@click.option('--config', type=click.Path(exists=True),
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--dry-run', is_flag=True,
              help='Show what would be processed without actually processing')
@click.version_option(version='0.1.0')
def shred(input_files, input_dir, output_dir, strategy, chunk_size, config, verbose, dry_run):
    """Transform PowerPoint presentations into LLM-optimized markdown.
    
    🎯 Production Mode: Drop PPTX files in input/ folder, run shred.py, pick up markdown from output/
    
    Examples:
        python src/shred.py                    # Process all files in input/ folder  
        python src/shred.py file.pptx         # Process specific file
        python src/shred.py --dry-run          # Preview what would be processed
        python src/shred.py -v --strategy sequential --chunk-size 2000
    """
    # Set logging level
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    # Show startup banner
    console.print(Panel.fit(
        "[bold blue]PPTX Shredder v0.1.0[/bold blue]\n"
        "[dim]Transform PowerPoint → LLM-optimized Markdown[/dim]\n"
        "[dim]Built for technical trainers[/dim]",
        border_style="blue"
    ))
    
    # Determine files to process
    files_to_process = _discover_files(input_files, input_dir)
    
    if not files_to_process:
        console.print("[yellow]⚠️  No PPTX files found to process.[/yellow]")
        console.print(f"💡 Drop .pptx files in the [bold]{input_dir}/[/bold] folder or specify files directly.")
        return
    
    # Show processing plan
    _show_processing_plan(files_to_process, output_dir, strategy, chunk_size, dry_run)
    
    if dry_run:
        console.print("[yellow]🔍 Dry run complete - no files were processed.[/yellow]")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process files with rich progress tracking
    _process_files(files_to_process, output_path, strategy, chunk_size, verbose)


def _discover_files(input_files: tuple, input_dir: str) -> List[Path]:
    """Discover PPTX files to process."""
    files_to_process = []
    
    if input_files:
        # Process specific files provided as arguments
        for file_path in input_files:
            path = Path(file_path)
            if path.exists() and is_pptx_file(str(path)):
                files_to_process.append(path)
            elif path.exists():
                logger.warning(f"Skipping {path} - not a PPTX file")
            else:
                logger.error(f"File not found: {path}")
    else:
        # Scan input directory for PPTX files
        input_path = Path(input_dir)
        if input_path.exists():
            pptx_files = list(input_path.glob("*.pptx")) + list(input_path.glob("*.ppt"))
            files_to_process.extend(pptx_files)
            logger.info(f"Found {len(pptx_files)} PPTX files in {input_dir}/")
        else:
            logger.warning(f"Input directory {input_dir}/ does not exist")
    
    return sorted(files_to_process)


def _show_processing_plan(files: List[Path], output_dir: str, strategy: str, chunk_size: int, dry_run: bool):
    """Display processing plan in a nice table."""
    table = Table(title="📋 Processing Plan", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Size", justify="right", style="green")
    table.add_column("Status", justify="center")
    
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        status = "🔍 Preview" if dry_run else "✅ Ready"
        table.add_row(file_path.name, f"{size_mb:.1f} MB", status)
    
    console.print(table)
    
    # Show configuration
    config_panel = Panel(
        f"[bold]Strategy:[/bold] {strategy}\n"
        f"[bold]Chunk Size:[/bold] {chunk_size} tokens\n"
        f"[bold]Output:[/bold] {output_dir}/",
        title="⚙️ Configuration",
        border_style="green"
    )
    console.print(config_panel)


def _process_files(files: List[Path], output_path: Path, strategy: str, chunk_size: int, verbose: bool):
    """Process files with rich progress indicators."""
    total_files = len(files)
    total_slides_processed = 0
    total_chunks_created = 0
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[cyan]Processing presentations...", total=total_files)
        
        for file_path in files:
            file_task = progress.add_task(f"[blue]Processing {file_path.name}...", total=100)
            
            try:
                # Extract content using intelligent extractor
                progress.update(file_task, advance=20, description=f"[blue]🧠 Intelligent extraction {file_path.name}...")
                extractor = IntelligentPPTXExtractor(str(file_path), use_llm=True)
                slides_data = extractor.extract_all_slides()
                total_slides_processed += len(slides_data)
                
                if verbose:
                    logger.info(f"Extracted {len(slides_data)} slides from {file_path.name}")
                
                # Format to markdown using intelligent formatter
                progress.update(file_task, advance=30, description=f"[blue]Formatting {file_path.name}...")
                formatter = IntelligentMarkdownFormatter(chunk_size=chunk_size)
                markdown_files = formatter.format(slides_data, file_path.stem)
                total_chunks_created += len(markdown_files)
                
                # Write files
                progress.update(file_task, advance=30, description=f"[blue]Writing {file_path.name}...")
                files_written = []
                for filename, content in markdown_files.items():
                    output_file = output_path / filename
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_written.append(output_file.name)
                
                progress.update(file_task, advance=20, description=f"[green]✅ {file_path.name} complete")
                
                if verbose:
                    logger.info(f"Created: {', '.join(files_written)}")
                
                # Success message
                console.print(f"✅ {file_path.name} → {len(markdown_files)} markdown file(s)")
                
            except Exception as e:
                progress.update(file_task, description=f"[red]❌ {file_path.name} failed")
                logger.error(f"Error processing {file_path.name}: {e}")
                if verbose:
                    console.print_exception()
                continue
            
            finally:
                progress.update(main_task, advance=1)
    
    # Show completion summary
    elapsed_time = time.time() - start_time
    _show_completion_summary(total_files, total_slides_processed, total_chunks_created, elapsed_time, output_path)


def _show_completion_summary(files: int, slides: int, chunks: int, elapsed: float, output_path: Path):
    """Show processing completion summary."""
    summary = Panel(
        f"[bold green]🎉 Processing Complete![/bold green]\n\n"
        f"[bold]Files Processed:[/bold] {files}\n"
        f"[bold]Slides Extracted:[/bold] {slides}\n" 
        f"[bold]Chunks Created:[/bold] {chunks}\n"
        f"[bold]Time Elapsed:[/bold] {elapsed:.1f}s\n"
        f"[bold]Output Location:[/bold] {output_path}/\n\n"
        f"[dim]Ready for LLM consumption! 🤖[/dim]",
        title="📊 Summary",
        border_style="green"
    )
    console.print(summary)

if __name__ == '__main__':
    shred()