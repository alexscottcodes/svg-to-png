from cog import BasePredictor, Input, Path
import cairosvg
from PIL import Image
import io
import tempfile
import os
import time
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import sys


class Predictor(BasePredictor):
    def setup(self):
        """Initialize the console for rich output"""
        self.console = Console(file=sys.stderr, force_terminal=True)
        
        self.console.print(Panel.fit(
            "[bold cyan]SVG to PNG Converter[/bold cyan]\n"
            "[dim]High-quality vector to raster conversion[/dim]",
            border_style="cyan"
        ))
        
    def _log_step(self, emoji: str, message: str, status: str = "info"):
        """Log a formatted step with emoji and styling"""
        colors = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "processing": "magenta"
        }
        color = colors.get(status, "white")
        self.console.print(f"{emoji}  [{color}]{message}[/{color}]")
    
    def _parse_svg_dimensions(self, svg_data: bytes) -> tuple:
        """Extract width and height from SVG"""
        try:
            root = ET.fromstring(svg_data)
            width = root.get('width', 'unknown')
            height = root.get('height', 'unknown')
            viewBox = root.get('viewBox', 'unknown')
            return width, height, viewBox
        except:
            return 'unknown', 'unknown', 'unknown'
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _create_info_table(self, svg_info: dict, output_info: dict) -> Table:
        """Create a rich table with conversion information"""
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Input (SVG)", style="yellow")
        table.add_column("Output (PNG)", style="green")
        
        table.add_row("Dimensions", 
                     f"{svg_info['width']} × {svg_info['height']}", 
                     f"{output_info['width']} × {output_info['height']} px")
        table.add_row("File Size", 
                     svg_info['size'], 
                     output_info['size'])
        table.add_row("DPI", 
                     "Vector (infinite)", 
                     str(output_info['dpi']))
        table.add_row("Background", 
                     "N/A", 
                     output_info['background'])
        
        if svg_info.get('viewBox'):
            table.add_row("ViewBox", svg_info['viewBox'], "—")
        
        return table

    def predict(
        self,
        svg_file: Path = Input(
            description="SVG file to convert to PNG"
        ),
        width: int = Input(
            description="Output width in pixels (leave empty to use SVG width)",
            default=None,
            ge=1,
            le=10000
        ),
        height: int = Input(
            description="Output height in pixels (leave empty to use SVG height)",
            default=None,
            ge=1,
            le=10000
        ),
        scale: float = Input(
            description="Scale factor to multiply SVG dimensions by (overrides width/height if set)",
            default=None,
            ge=0.1,
            le=10.0
        ),
        dpi: int = Input(
            description="DPI (dots per inch) for rendering",
            default=96,
            ge=72,
            le=600
        ),
        background_color: str = Input(
            description="Background color (hex code like '#FFFFFF' or 'transparent')",
            default="transparent",
        ),
    ) -> Path:
        """Convert SVG to high-resolution PNG with detailed progress tracking"""
        
        start_time = time.time()
        
        # Create a progress bar context
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False
        ) as progress:
            
            # Main conversion task
            main_task = progress.add_task("[cyan]Converting SVG to PNG...", total=100)
            
            # Step 1: Read SVG file
            progress.update(main_task, advance=15, description="[cyan]Reading SVG file...")
            self._log_step("📖", "Reading input SVG file", "processing")
            
            with open(svg_file, 'rb') as f:
                svg_data = f.read()
            
            svg_size = len(svg_data)
            svg_width, svg_height, viewBox = self._parse_svg_dimensions(svg_data)
            
            self._log_step("✓", f"Loaded SVG: {self._format_file_size(svg_size)}", "success")
            
            # Step 2: Parse and validate
            progress.update(main_task, advance=10, description="[cyan]Parsing SVG structure...")
            self._log_step("🔍", f"Analyzing SVG (dimensions: {svg_width} × {svg_height})", "processing")
            time.sleep(0.3)  # Brief pause for visual feedback
            
            # Parse background color
            background = None if background_color.lower() == "transparent" else background_color
            
            # Step 3: Prepare conversion parameters
            progress.update(main_task, advance=15, description="[cyan]Configuring conversion parameters...")
            self._log_step("⚙️", "Preparing conversion settings", "processing")
            
            convert_params = {'dpi': dpi}
            if background:
                convert_params['background_color'] = background
                self._log_step("🎨", f"Background: {background_color}", "info")
            else:
                self._log_step("🎨", "Background: transparent", "info")
            
            # Handle scaling options
            if scale is not None:
                convert_params['scale'] = scale
                self._log_step("📏", f"Scaling by factor: {scale}x", "info")
            elif width is not None or height is not None:
                if width is not None:
                    convert_params['output_width'] = width
                    self._log_step("📐", f"Width: {width}px", "info")
                if height is not None:
                    convert_params['output_height'] = height
                    self._log_step("📐", f"Height: {height}px", "info")
            
            self._log_step("🎯", f"DPI: {dpi}", "info")
            
            # Step 4: Convert SVG to PNG
            progress.update(main_task, advance=5, description="[magenta]Rendering SVG...")
            self._log_step("🎨", "Rendering SVG with Cairo...", "processing")
            time.sleep(0.2)
            
            try:
                png_data = cairosvg.svg2png(
                    bytestring=svg_data,
                    **convert_params
                )
                progress.update(main_task, advance=30)
                self._log_step("✓", "SVG rendered successfully", "success")
            except Exception as e:
                self._log_step("✗", f"Rendering failed: {str(e)}", "error")
                raise
            
            # Step 5: Post-processing with PIL
            progress.update(main_task, advance=15, description="[cyan]Post-processing image...")
            self._log_step("🖼️", "Opening image with PIL for optimization", "processing")
            
            img = Image.open(io.BytesIO(png_data))
            img_width, img_height = img.size
            
            self._log_step("✓", f"Image loaded: {img_width} × {img_height} pixels", "success")
            
            # Step 6: Save optimized PNG
            progress.update(main_task, advance=10, description="[cyan]Saving optimized PNG...")
            self._log_step("💾", "Writing optimized PNG to disk", "processing")
            
            output_path = Path(tempfile.mktemp(suffix=".png"))
            img.save(output_path, "PNG", optimize=True)
            
            output_size = os.path.getsize(output_path)
            progress.update(main_task, advance=5, description="[green]Conversion complete!")
            
            self._log_step("✓", f"PNG saved: {self._format_file_size(output_size)}", "success")
        
        # Final summary
        elapsed_time = time.time() - start_time
        
        self.console.print()  # Empty line
        
        # Create summary table
        svg_info = {
            'width': svg_width,
            'height': svg_height,
            'size': self._format_file_size(svg_size),
            'viewBox': viewBox
        }
        
        output_info = {
            'width': img_width,
            'height': img_height,
            'size': self._format_file_size(output_size),
            'dpi': dpi,
            'background': background_color
        }
        
        summary_table = self._create_info_table(svg_info, output_info)
        self.console.print(Panel(summary_table, 
                                title="[bold green]Conversion Summary[/bold green]",
                                border_style="green"))
        
        # Performance stats
        self.console.print(
            f"\n[bold cyan]⚡ Conversion completed in {elapsed_time:.2f} seconds[/bold cyan]"
        )
        
        compression_ratio = (1 - output_size / svg_size) * 100 if output_size < svg_size else 0
        if compression_ratio > 0:
            self.console.print(f"[dim]Size change: {compression_ratio:+.1f}%[/dim]")
        
        self.console.print(Panel.fit(
            "[bold green]✓ SUCCESS[/bold green]\n"
            f"[dim]Output: {output_path}[/dim]",
            border_style="green"
        ))
        
        return output_path