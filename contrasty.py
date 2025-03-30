"""
Contrasty function implementation for achieving target contrast ratios

This module provides the contrasty() method which finds color variants that
achieve specific contrast ratios against background colors.
"""
from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from coloraide.color import Color

# Define a small epsilon for floating point comparisons and adjustments
EPSILON = 1e-5

def contrasty(
    self: Color,
    bg: Color | str,
    cr: float,
    method: str = 'wcag21',
    preserve_chroma: bool = False
) -> Color:
    """
    Find a variant of the current color that achieves the target contrast ratio
    against the background color by adjusting lightness in OkLrCh space.

    Parameters:
        bg: The background color (as Color object or string) to contrast against.
        cr: Target contrast ratio/value.
            - For WCAG 2.1, this is the ratio (e.g., 4.5, 7.0).
            - For APCA, L*, Delta-Phi, this is the target value.
            - If positive, finds a variant with that contrast magnitude, typically
              adjusting towards black if starting lighter than bg, or white if
              starting darker than bg (or adjusting away from bg if similar lightness).
            - If negative, finds a variant with that contrast magnitude but
              adjusts in the opposite direction (e.g., finds a *lighter* variant
              even if starting lighter than bg).
        method: Contrast method ('wcag21', 'apca', 'lstar', 'delta-phi').
        preserve_chroma: If True, attempts to preserve the original chroma proportion
                         relative to lightness (C/L) when adjusting lightness. Note that
                         this can push colors out of gamut more easily.

    Returns:
        A new Color object with adjusted lightness to meet the target contrast,
        converted back to the original color space. If no solution is found
        within tolerance, returns the closest attempt.
    """
    # --- Input Validation and Setup ---
    if not isinstance(bg, self.__class__):
        bg_color = self.__class__(bg)
    else:
        bg_color = bg

    # Use OkLrCh for perceptually relevant lightness manipulation
    # Keep the original color for reference and final conversion
    original_color = self
    fg_color = self.convert('oklrch')
    bg_color = bg_color.convert('oklrch')

    # Extract initial components
    initial_l = fg_color[0]
    initial_c = fg_color[1]
    h = fg_color[2]  # Hue remains constant
    alpha = fg_color.alpha() # Preserve alpha
    bg_l = bg_color[0]

    # Determine target direction (make darker or lighter relative to background)
    # A negative target contrast `cr` means we explicitly want the *opposite*
    # direction adjustment than what would naturally achieve contrast.
    target_contrast_magnitude = abs(cr)
    if target_contrast_magnitude < EPSILON:
         # Target is essentially zero contrast, return the color unchanged
         # or maybe slightly adjusted towards bg_l? For now, return unchanged.
         # Or perhaps better, return the color that *matches* bg_l if possible.
         # Let's match bg_l, preserving chroma if requested.
        l = bg_l
        c = initial_c
        if preserve_chroma and initial_l > EPSILON:
            c = initial_c * (l / initial_l)
        result = self.__class__('oklrch', [l, c, h], alpha).fit('srgb')
        return result.convert(original_color.space())


    # If cr is negative, flip the intended adjustment direction
    # Otherwise, default is to move away from the background lightness
    explicit_direction = cr < 0
    natural_make_darker = initial_l > bg_l # Naturally need to go darker for contrast
    if initial_l == bg_l: # If exactly same lightness, default to darker unless explicit lighter requested
        natural_make_darker = True

    make_darker = explicit_direction ^ natural_make_darker # XOR logic: flip if explicit requested

    # --- Binary Search Setup ---
    min_l = 0.0
    max_l = 1.0
    current_l = initial_l
    best_l = current_l # Keep track of the best L found so far

    # Handle starting at the exact same lightness as the background
    if abs(current_l - bg_l) < EPSILON:
        # Nudge the starting lightness slightly to establish a search direction
        current_l += EPSILON if not make_darker else -EPSILON
        current_l = max(0.0, min(1.0, current_l)) # Clamp to valid range

    # Search parameters
    # Precision based on typical contrast method sensitivity
    precision = 0.01 if method == 'wcag21' else 0.1 # Looser for APCA/L*/DeltaPhi? Maybe adjust.
    if method == 'apca': precision = 0.5 # APCA values can vary more
    max_iterations = 50
    iterations = 0
    
    # Store the closest contrast difference found
    min_contrast_diff = float('inf')

    # --- Binary Search Loop ---
    while iterations < max_iterations:
        iterations += 1

        # Calculate chroma for the current lightness `current_l`
        current_c = initial_c
        if preserve_chroma and initial_l > EPSILON:
            # Scale chroma proportionally, but prevent division by zero
            current_c = initial_c * (current_l / initial_l)

        # Create the test color, fit it to the sRGB gamut (important!)
        test_color = self.__class__('oklrch', [current_l, current_c, h], alpha)
        if not test_color.in_gamut('srgb', tolerance=0):
             test_color = test_color.fit('srgb')
             # After fitting, L and C might have changed, update them
             fitted_oklrch = test_color.convert('oklrch')
             current_l = fitted_oklrch[0] # Use the *actual* L after fitting
             current_c = fitted_oklrch[1] # Use the *actual* C after fitting

        # Calculate the contrast for the fitted color
        current_contrast = test_color.contrast(bg_color, method=method)

        # Check if we met the target contrast magnitude within precision
        contrast_diff = abs(current_contrast) - target_contrast_magnitude
        
        # Update best guess if this is closer
        if abs(contrast_diff) < min_contrast_diff:
             min_contrast_diff = abs(contrast_diff)
             best_l = current_l

        if abs(contrast_diff) < precision:
            # Found a satisfactory lightness
            best_l = current_l
            break

        # Adjust search range based on the contrast difference and desired direction
        if contrast_diff < 0:
            # Current contrast magnitude is TOO LOW. Need to move `current_l` FURTHER from `bg_l`.
            if make_darker: # We want darker, so need lower L
                max_l = current_l # Lower L further
            else: # We want lighter, so need higher L
                min_l = current_l # Raise L further
        else:
            # Current contrast magnitude is TOO HIGH. Need to move `current_l` CLOSER to `bg_l`.
            if make_darker: # We want darker, current L is too low
                min_l = current_l # Raise L towards bg_l
            else: # We want lighter, current L is too high
                max_l = current_l # Lower L towards bg_l

        # Calculate the midpoint for the next iteration
        next_l = (min_l + max_l) / 2

        # Avoid getting stuck if search space collapses
        if abs(next_l - current_l) < EPSILON:
             # Try nudging slightly based on direction
             nudge = EPSILON * (1 if max_l > min_l else -1) # Small nudge
             current_l += nudge
             if current_l < min_l or current_l > max_l: # If nudge failed, break
                 break
        else:
             current_l = next_l

        # Safety break if range is invalid
        if min_l > max_l:
            break

    # --- Result Generation ---
    # Use the best lightness found during the search
    final_l = best_l

    # Calculate final chroma
    final_c = initial_c
    if preserve_chroma and initial_l > EPSILON:
        final_c = initial_c * (final_l / initial_l)

    # Create the final color object
    result_color = self.__class__('oklrch', [final_l, final_c, h], alpha)

    # Ensure the final result is in gamut
    if not result_color.in_gamut('srgb', tolerance=0):
        result_color = result_color.fit('srgb')

    # Convert back to the original color space and return
    return result_color.convert(original_color.space())
