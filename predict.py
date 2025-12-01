from cog import BasePredictor, Input, Path
import cairosvg
from PIL import Image
import io
import tempfile
import os


class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        # No model weights to load for SVG conversion
        pass

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
        """Convert SVG to high-resolution PNG"""
        
        # Read the SVG file
        with open(svg_file, 'rb') as f:
            svg_data = f.read()
        
        # Parse background color
        background = None if background_color.lower() == "transparent" else background_color
        
        # Prepare conversion parameters
        convert_params = {
            'dpi': dpi,
        }
        
        if background:
            convert_params['background_color'] = background
        
        # Handle scaling options
        if scale is not None:
            # Scale the SVG by a factor
            convert_params['scale'] = scale
        elif width is not None or height is not None:
            # Set specific dimensions
            if width is not None:
                convert_params['output_width'] = width
            if height is not None:
                convert_params['output_height'] = height
        
        # Convert SVG to PNG bytes
        png_data = cairosvg.svg2png(
            bytestring=svg_data,
            **convert_params
        )
        
        # Open with PIL for potential post-processing
        img = Image.open(io.BytesIO(png_data))
        
        # Save to temporary output file
        output_path = Path(tempfile.mktemp(suffix=".png"))
        img.save(output_path, "PNG", optimize=True)
        
        return output_path