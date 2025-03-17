# ColorAide Contrasty

An extension for [ColorAide](https://github.com/facelessuser/coloraide) that provides functionality to find accessible color variants that achieve specific contrast ratios against background colors.

## Features

- **Contrasty Method**: Find color variants that achieve target contrast ratios
- **Multiple Contrast Methods**:
  - WCAG 2.1 (Standard web contrast)
  - APCA (Accessible Perceptual Contrast Algorithm)
  - L* contrast (Simple lightness difference contrast)
  - Delta Phi Star (Perceptual contrast based on golden ratio)
- **Chroma Preservation**: Option to preserve the original chroma when adjusting colors
- **Easy Integration**: Simple extension of ColorAide's Color class
- **Bidirectional Adjustment**: Create both lighter and darker variants

## Installation

```bash
# Clone the repository
git clone https://github.com/hereticmilk/coloraide_contrasty.git

# Install dependencies
pip install coloraide
```

## Usage

```python
from coloraide_contrasty import Color

# Create a color
red = Color("red")

# Get a darker variant with WCAG 2.1 contrast of 4.5:1 against white
accessible_red = red.contrasty("white", 4.5)
print(f"WCAG Accessible: {accessible_red.to_string()}")
print(f"Contrast ratio: {accessible_red.contrast('white')}")

# Get a lighter variant using APCA contrast method
apca_red = red.contrasty("black", -30, method="apca")
print(f"APCA Accessible: {apca_red.to_string()}")
print(f"APCA contrast: {apca_red.contrast('black', method='apca')}")

# Using Lstar contrast method
lstar_red = red.contrasty("white", 45, method="lstar")
print(f"Lstar Accessible: {lstar_red.to_string()}")
print(f"Lstar contrast: {lstar_red.contrast('white', method='lstar')}")

# Using Delta Phi Star contrast method
delta_phi_red = red.contrasty("white", 20, method="delta-phi")
print(f"Delta Phi Accessible: {delta_phi_red.to_string()}")
print(f"Delta Phi contrast: {delta_phi_red.contrast('white', method='delta-phi')}")

# Preserve chroma when adjusting lightness
vibrant = Color("oklrch", [0.65, 0.3, 130])
vibrant_accessible = vibrant.contrasty("white", 4.5, preserve_chroma=True)
print(f"Accessible vibrant: {vibrant_accessible.to_string()}")
```

## Color Contrast Methods

### WCAG 2.1 (Default)
Uses the standard Web Content Accessibility Guidelines (WCAG) 2.1 contrast ratio calculation:
- 4.5:1 minimum for normal text (AA)
- 7:1 for enhanced contrast (AAA)
- Based on relative luminance of colors
- Widely used and recognized accessibility standard
- Implemented through ColorAide's built-in contrast method

### APCA
The Accessible Perceptual Contrast Algorithm provides a more perceptually accurate contrast measurement:
- Typically uses values between 45-60 for readable text
- Accounts for the polarity of contrast (light on dark vs dark on light)
- Complex non-linear model with multiple exponents and scaling factors
- Custom luminance calculation method for more accurate perceptual modeling
- Applies soft clamping for near-black colors
- Returns values in the 0-100+ range (bidirectional)

### L* Contrast
Simple difference in L* (lightness) values in the Lab color space:
- Simple and intuitive to understand
- Typically needs differences of 40-50 for good readability
- Linear model based on CIE L* lightness
- Uses LCH-D65 color space
- Returns direct difference in lightness (0-100 range)
- Not sensitive to contrast direction (only returns absolute difference)

### Delta Phi Star
Uses the golden ratio to calculate contrast:
- Values below 7.5 are considered "0" contrast
- Higher values indicate more contrast
- Based on perceptual non-linearity of human vision
- Uses the golden ratio (φ ≈ 1.618) for non-linear scaling
- Moderate complexity between L* and APCA
- Returns values in the 0-100+ range (values below 7.5 return 0)

## Contrast Method Comparison

| Feature | WCAG 2.1 | L* Contrast | Delta Phi Star | APCA |
|---------|----------|-------------|----------------|------|
| **Complexity** | Moderate | Simple | Moderate | Complex |
| **Color Space** | sRGB | LCH-D65 | LAB-D65 | sRGB |
| **Math Model** | Relative luminance ratio | Linear difference | Golden ratio powers | Multiple exponents & scaling |
| **Output Range** | 1:1 to 21:1 ratio | 0-100 (difference) | 0-100+ (values <7.5 are 0) | 0-100+ (bidirectional) |
| **Direction Sensitivity** | Not sensitive | Not sensitive | Not sensitive | Polarity-aware |
| **Perceptual Accuracy** | Moderate | Basic | Good | Excellent |
| **Implementation Complexity** | Moderate | Very simple (3 lines) | Moderate | Complex (many constants) |
| **Pre-processing** | Luminance calculation | None | None | Custom luminance, soft clamping |
| **Best For** | Standard compliance | Simple implementations | Better perceptual accuracy | Maximum perceptual accuracy |

### When to Use Each Method:

- **WCAG 2.1**: When you need compliance with web accessibility standards
- **Lstar**: When you need a simple, easy-to-understand contrast measure
- **Delta Phi Star**: When you need a perceptually improved contrast measure with moderate complexity
- **APCA**: When you need the most perceptually accurate contrast measure, especially for text readability

## How It Works

The `contrasty` method uses a binary search algorithm to find a color variant with the desired contrast:

1. Converts colors to OkLrCh color space for better perceptual manipulation
2. Performs a binary search to find the lightness value that achieves the target contrast
3. Preserves chroma proportion to maintain color vibrancy if requested
4. Ensures the resulting color is in gamut

## License

[MIT License](LICENSE)

## Credits

- [ColorAide](https://github.com/facelessuser/coloraide) - Base color manipulation library
- [APCA](https://github.com/Myndex/SAPC-APCA) - Accessible Perceptual Contrast Algorithm
- [Delta Phi Star](https://github.com/Myndex/deltaphistar) - Perceptual contrast based on golden ratio
