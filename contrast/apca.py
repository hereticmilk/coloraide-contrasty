"""
APCA (Accessible Perceptual Contrast Algorithm) Contrast Implementation

https://github.com/Myndex/SAPC-APCA
"""
from __future__ import annotations
from coloraide.contrast import ColorContrast
from coloraide import algebra as alg
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from coloraide.color import Color


class APCAContrast(ColorContrast):
    """APCA 0.0.98G color contrast."""

    NAME = "apca"

    # Exponents
    NORM_BG = 0.56
    NORM_TXT = 0.57
    REV_TEXT = 0.62
    REV_BG = 0.65

    # Clamps
    BLK_THRS = 0.022
    BLK_CLMP = 1.414
    LO_CLIP = 0.1
    DELTA_Y_MIN = 0.0005

    # Scalers
    SCALE_BOW = 1.14
    LO_BOW_OFFSET = 0.027
    SCALE_WOB = 1.14
    LO_WOB_OFFSET = 0.027

    # Values for linearization
    MAIN_TRC = 2.4
    GAMMA = [0.2126729, 0.7151522, 0.0721750]

    def soft_clamp(self, y: float) -> float:
        """Soft clamp 'y' if near black."""

        return y if y >= self.BLK_THRS else y + (self.BLK_THRS - y) ** self.BLK_CLMP

    def luminance(self, color: Color) -> float:
        """
        Convert to linear sRGB using APCA constants and calculate 'Y' by summing values.

        Ideally, we'd just convert to XYZ D65 and grab the Y component, but in order to
        claim that we implement APCA, the license requires you to use exactly what they use.
        """

        # return color.luminance()
        return sum(alg.multiply([alg.spow(c, self.MAIN_TRC) for c in color.convert('srgb')[:-1]], self.GAMMA))

    def contrast(self, color1: Color, color2: Color, **kwargs: Any) -> float:
        """
        Contrast.

        Myndex assumes sRGB according to current publication.
        """

        # Calculate the luminance.
        lum_txt = self.luminance(color1)
        lum_bg = self.luminance(color2)

        # Clamp very dark values
        y_txt = self.soft_clamp(lum_txt)
        y_bg = self.soft_clamp(lum_bg)

        # Return Lc = 0 Early for extremely low delta Y.
        # Essentially a noise gate.
        if abs(y_bg - y_txt) < self.DELTA_Y_MIN:
            return 0.0

        # Calculate the SAPC contrast value and scale.
        # Determine direction: "black on white" or the reverse.
        if y_bg > y_txt:
            # dark text on light background
            sapc = ((y_bg ** self.NORM_BG) - (y_txt ** self.NORM_TXT)) * self.SCALE_BOW
        else:
            # light text on dark background
            sapc = ((y_bg ** self.REV_BG) - (y_txt ** self.REV_TEXT)) * self.SCALE_WOB

        if abs(sapc) < self.LO_CLIP:
            sapc = 0.0
        elif sapc > 0:
            sapc -= self.LO_BOW_OFFSET
        else:
            sapc += self.LO_WOB_OFFSET

        # Return Lc scaled by 100.
        return sapc * 100.0