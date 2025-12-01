# SVG to PNG Converter - Replicate Cog

A high-quality SVG to PNG converter packaged as a Replicate model using Cog.

## Features

- Convert SVG files to high-resolution PNG images
- Adjustable output resolution (width, height, or scale factor)
- Configurable DPI (72-600)
- Transparent or custom background colors
- Optimized PNG output
- **Beautiful progress bars and real-time feedback**
- **Detailed conversion analytics and summaries**
- **Rich formatted logs with emoji indicators**
- **Performance metrics and file size tracking**

## Setup

### Prerequisites

1. Install Docker and ensure it's running
2. Install Cog:
```bash
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog
```

### Files

- `cog.yaml` - Defines dependencies and environment
- `predict.py` - Model prediction interface

## Local Testing

Test the model locally with Cog:

```bash
# Basic conversion
cog predict -i svg_file=@input.svg

# Scale by 2x
cog predict -i svg_file=@input.svg -i scale=2.0

# Specific dimensions
cog predict -i svg_file=@input.svg -i width=2000 -i height=2000

# High DPI with white background
cog predict -i svg_file=@input.svg -i dpi=300 -i background_color="#FFFFFF"

# Large scale, high DPI for print
cog predict -i svg_file=@input.svg -i scale=4.0 -i dpi=300
```

## API Usage

Via our model, you can use the Python client:

```python
import replicate

output = replicate.run(
    "unityaisolutions/svg-to-png:latest",
    input={
        "svg_file": open("logo.svg", "rb"),
        "scale": 3.0,
        "dpi": 300,
        "background_color": "transparent"
    }
)

# Save the output
with open("output.png", "wb") as f:
    f.write(output.read())
```

## Input Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `svg_file` | File | SVG file to convert | Required |
| `width` | Integer | Output width in pixels (1-10000) | SVG width |
| `height` | Integer | Output height in pixels (1-10000) | SVG height |
| `scale` | Float | Scale factor (0.1-10.0) - overrides width/height | None |
| `dpi` | Integer | Rendering DPI (72-600) | 96 |
| `background_color` | String | Background color hex or 'transparent' | transparent |

## Examples

**Create social media graphics:**
```bash
cog predict -i svg_file=@logo.svg -i width=1200 -i height=630
```

**High-res print ready:**
```bash
cog predict -i svg_file=@design.svg -i scale=5.0 -i dpi=300
```

**Icon generation:**
```bash
cog predict -i svg_file=@icon.svg -i width=512 -i height=512
```

## Notes

- The model uses CairoSVG for rendering, which provides high-quality output
- For best results with transparency, use PNG format
- Maximum dimensions are capped at 10000x10000 pixels
- Scale factors above 5x may result in very large files