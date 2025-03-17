# pragma: init
"""
Delta Phi Star Contrast

https://github.com/Myndex/deltaphistar
"""
from __future__ import annotations
import math
from coloraide import algebra as alg
from coloraide.contrast import ColorContrast
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from coloraide.color import Color


class DeltaPhiStarContrast(ColorContrast):
    """Delta Phi Star contrast."""

    NAME = "delta-phi"

    PHI = (5 ** 0.5) * 0.5 + 0.5
    SQRT2 = math.sqrt(2)

    def contrast(self, color1: Color, color2: Color, **kwargs: Any) -> float:
        """Contrast using Delta Phi Star."""

        lstar_txt = color1.get('lab-d65.l')
        lstar_bg = color2.get('lab-d65.l')

        contrast = (
            alg.nth_root(abs(alg.spow(lstar_bg, self.PHI) -
            alg.spow(lstar_txt, self.PHI)), self.PHI) *
            self.SQRT2 -
            40.0
        )

        return 0.0 if contrast < 7.5 else contrast