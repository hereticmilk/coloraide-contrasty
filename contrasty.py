"""
Contrasty function implementation for achieving target contrast ratios

This module provides the contrasty() method which finds color variants that
achieve specific contrast ratios against background colors.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from coloraide.color import Color


def contrasty(self, bg, cr, method='wcag21', preserve_chroma=False):
    """
    Find a variant of the current color that achieves the target contrast ratio
    against the background color.

    Parameters:
        bg (Color): The background color to contrast against
        cr (float): Target contrast ratio to achieve
        method (str): Contrast method to use ('wcag21', 'apca', 'lstar', 'delta-phi')
        preserve_chroma (bool): If True, attempts to preserve the original
                               chroma/lightness ratio when adjusting lightness

    Returns:
        Color: A new color with adjusted lightness to achieve the target contrast
    """
    # Convert to OkLrCh for manipulation (separates lightness from chroma and hue)
    fg = self.convert('oklrch')
    bg = self.__class__(bg).convert('oklrch')

    # Extract components
    h = fg[2]  # Hue
    c = fg[1]  # Chroma
    l = fg[0]  # Lightness
    bg_l = bg[0]  # Background lightness

    # Check if colors are very similar - handle special case for creating lighter/darker variants
    colors_similar = abs(fg.distance(bg)) < 0.05  # Small threshold for similar colors

    # Determine if we should create darker or lighter variant
    make_darker = cr > 0
    if cr < 0:
        cr = abs(cr)  # Use absolute value for calculations
        make_darker = False  # Negative CR means make lighter

    # If colors are similar and we need a variant, use direct lightness approach
    if colors_similar:
        if method == 'apca':
            # APCA needs different scaling since its values are typically 0-100+
            # For same colors, APCA will be close to 0
            if make_darker:
                # Create darker variant - use larger shifts for APCA
                shift_factor = min(cr / 60, 1.0)  # Scale by typical APCA range (0-100)
                new_l = max(l - (shift_factor * 0.4), 0.05)  # Limit how dark we go
            else:
                # Create lighter variant
                shift_factor = min(cr / 60, 1.0)
                new_l = min(l + (shift_factor * 0.4), 0.95)  # Limit how light we go
        elif method == 'lstar':
            # Lstar is simple - just adjust by the requested amount
            if make_darker:
                # For L*, cr is the target difference, so we directly use it
                # Scale it down slightly since L* uses a 0-100 scale and we're in 0-1
                new_l = max(l - (cr / 100), 0.05)
            else:
                new_l = min(l + (cr / 100), 0.95)
        elif method == 'delta-phi':
            # Delta Phi Star typically returns values in a range similar to WCAG but with different scaling
            # For Delta Phi, values below 7.5 are considered "0" and it tops out around 100
            if make_darker:
                # Scale to make larger shifts for higher contrast targets
                shift_factor = min(cr / 50, 1.0)  # Scale by typical Delta Phi range
                new_l = max(l - (shift_factor * 0.35), 0.05)  # Conservative shift
            else:
                # Create lighter variant
                shift_factor = min(cr / 50, 1.0)
                new_l = min(l + (shift_factor * 0.35), 0.95)  # Conservative shift
        else:
            # For WCAG and other methods with smaller scales
            if make_darker:
                # Create darker variant
                shift_amount = min((cr - 1.0) * 0.2, 0.4)  # Scale shift by contrast difference
                new_l = max(l - shift_amount, 0.05)  # Don't go completely black
            else:
                # Create lighter variant
                shift_amount = min((cr - 1.0) * 0.2, 0.4)  # Scale shift by contrast difference
                new_l = min(l + shift_amount, 0.95)  # Don't go completely white

        # Calculate new chroma if preserving proportions
        new_c = c
        if preserve_chroma and fg[0] > 0:
            new_c = c * (new_l / fg[0])

        # Create result color
        result = self.__class__('oklrch', [new_l, new_c, h], fg.alpha())

        # Ensure it's in gamut
        if not result.in_gamut('srgb'):
            result = result.fit('srgb')

        # Return in original color space
        return result.convert(self.space())

    # Initialize search parameters
    min_l = 0.0
    max_l = 1.0
    precision = 0.001
    max_iterations = 50

    # Start at a point away from the background lightness to ensure we can find a solution
    if abs(l - bg_l) < 0.05:  # If colors are very close in lightness
        if make_darker:
            l = max(bg_l - 0.1, 0.05)  # Start darker
        else:
            l = min(bg_l + 0.1, 0.95)  # Start lighter

    # Binary search to find a lightness that achieves target contrast
    current_contrast = fg.contrast(bg, method=method)
    iterations = 0

    # Handle method-specific contrast adjustments if needed
    if method == 'apca':
        # For APCA, positive contrast means text is darker than background
        if make_darker and l > bg_l:
            l = bg_l * 0.7  # Start with a darker value
        elif not make_darker and l < bg_l:
            l = bg_l * 1.3  # Start with a lighter value
            l = min(l, 0.95)  # Cap at 0.95
    elif method == 'delta-phi':
        # For Delta Phi Star, we need significant changes to reach threshold values
        # since values below 7.5 are considered "0"
        if make_darker and l > bg_l - 0.2:
            l = max(bg_l - 0.25, 0.05)  # Start with a noticeably darker value
        elif not make_darker and l < bg_l + 0.2:
            l = min(bg_l + 0.25, 0.95)  # Start with a noticeably lighter value

    # Binary search loop
    while abs(current_contrast - cr) > precision and iterations < max_iterations:
        iterations += 1

        # Determine direction based on comparison
        if abs(current_contrast) < cr:
            # Need more contrast - move away from bg lightness
            if make_darker and l > bg_l:
                # Should be darker but currently lighter
                max_l = l
                l = (min_l + l) / 2
            elif make_darker:
                # Should be darker and is already darker
                min_l = l
                l = (l + max_l) / 2
            elif not make_darker and l < bg_l:
                # Should be lighter but currently darker
                min_l = l
                l = (l + max_l) / 2
            else:
                # Should be lighter and is already lighter
                max_l = l
                l = (min_l + l) / 2
        else:
            # Need less contrast - move toward bg lightness
            if make_darker and l > bg_l:
                # Should be darker but currently lighter
                min_l = l
                l = (l + max_l) / 2
            elif make_darker:
                # Should be darker and is already darker
                max_l = l
                l = (min_l + l) / 2
            elif not make_darker and l < bg_l:
                # Should be lighter but currently darker
                max_l = l
                l = (min_l + l) / 2
            else:
                # Should be lighter and is already lighter
                min_l = l
                l = (l + max_l) / 2

        # Calculate new chroma if preserving proportions
        new_c = c
        if preserve_chroma and fg[0] > 0:
            new_c = c * (l / fg[0])

        # Create and test color
        test_color = self.__class__('oklrch', [l, new_c, h], fg.alpha())
        if not test_color.in_gamut('srgb'):
            test_color = test_color.fit('srgb')

        current_contrast = test_color.contrast(bg, method=method)

    # Second phase: Find the range of valid lightness values
    found_l = l
    min_valid_l = found_l
    max_valid_l = found_l
    step = precision / 2

    # Find minimum valid lightness
    test_l = found_l
    while test_l > 0 and iterations < max_iterations * 2:
        iterations += 1
        test_l -= step

        # Calculate chroma
        test_c = c
        if preserve_chroma and fg[0] > 0:
            test_c = c * (test_l / fg[0])

        # Test contrast
        test_color = self.__class__('oklrch', [test_l, test_c, h], fg.alpha())
        if not test_color.in_gamut('srgb'):
            test_color = test_color.fit('srgb')

        test_contrast = test_color.contrast(bg, method=method)

        if abs(test_contrast - cr) <= precision:
            min_valid_l = test_l
        else:
            break

    # Find maximum valid lightness
    test_l = found_l
    while test_l < 1 and iterations < max_iterations * 3:
        iterations += 1
        test_l += step

        # Calculate chroma
        test_c = c
        if preserve_chroma and fg[0] > 0:
            test_c = c * (test_l / fg[0])

        # Test contrast
        test_color = self.__class__('oklrch', [test_l, test_c, h], fg.alpha())
        if not test_color.in_gamut('srgb'):
            test_color = test_color.fit('srgb')

        test_contrast = test_color.contrast(bg, method=method)

        if abs(test_contrast - cr) <= precision:
            max_valid_l = test_l
        else:
            break

    # Use middle of valid range (as in the original JS function)
    final_l = (min_valid_l + max_valid_l) / 2

    # Calculate final chroma
    final_c = c
    if preserve_chroma and fg[0] > 0:
        final_c = c * (final_l / fg[0])

    # Create result color
    result = self.__class__('oklrch', [final_l, final_c, h], fg.alpha())

    # Ensure it's in gamut
    if not result.in_gamut('srgb'):
        result = result.fit('srgb')

    # Return in original color space
    return result.convert(self.space())