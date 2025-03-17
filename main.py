from __future__ import annotations
from coloraide import Color as Base
from coloraide.spaces.oklrab import Oklrab
from coloraide.spaces.oklrch import OkLrCh
from coloraide.contrast.lstar import LstarContrast
from contrast.apca import APCAContrast
from contrast.delta_phi import DeltaPhiStarContrast
from contrasty import contrasty

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from coloraide.color import Color


# Extend Color class and register necessary components
class Color(Base):
    contrasty = contrasty

# Register color spaces and contrast methods
Color.register(Oklrab())  # Register OkLrab first
Color.register(OkLrCh())  # Then register OkLrCh which depends on OkLrab
Color.register(APCAContrast())  # Register our APCA implementation
Color.register(LstarContrast())  # Register the built-in Lstar implementation
Color.register(DeltaPhiStarContrast())  # Register Delta Phi Star contrast

# Test code
if __name__ == "__main__":
    # Same color tests with different methods
    red = Color("red")

    # WCAG tests
    darker_red_wcag = red.contrasty("red", 1.5)  # Positive contrast = darker (WCAG)
    lighter_red_wcag = red.contrasty("red", -1.5)  # Negative contrast = lighter (WCAG)

    print(f"Original: {red.to_string()}")
    print(f"Darker WCAG (1.5:1): {darker_red_wcag.to_string(hex=True)}")
    print(f"Lighter WCAG (-1.5:1): {lighter_red_wcag.to_string(hex=True)}")

    # APCA tests
    darker_red_apca = red.contrasty("red", 30, method="apca")  # Positive APCA = darker
    lighter_red_apca = red.contrasty("red", -30, method="apca")  # Negative APCA = lighter

    print(f"\nOriginal: {red.to_string()}")
    print(f"Darker APCA (30): {darker_red_apca.to_string(hex=True)}")
    print(f"Lighter APCA (-30): {lighter_red_apca.to_string(hex=True)}")

    # Lstar tests - using the built-in Lstar contrast method
    darker_red_lstar = red.contrasty("red", 20, method="lstar")  # Positive Lstar = darker
    lighter_red_lstar = red.contrasty("red", -20, method="lstar")  # Negative Lstar = lighter

    print(f"\nOriginal: {red.to_string()}")
    print(f"Darker Lstar (20): {darker_red_lstar.to_string(hex=True)}")
    print(f"Lighter Lstar (-20): {lighter_red_lstar.to_string(hex=True)}")

    # Standard contrast examples
    accessible_red = red.contrasty("white", 7.0)  # WCAG AA compliant
    print(f"\nOriginal: {red.to_string()}")
    print(f"WCAG Accessible (7:1 contrast): {accessible_red.to_string()}")
    print(f"Contrast ratio: {accessible_red.contrast('white')}")

    # Lstar contrast for accessibility
    lstar_red = red.contrasty("white", 45, method="lstar")  # L* difference of 45 (typical accessibility requirement)
    print(f"Lstar Accessible (difference of 45): {lstar_red.to_string()}")
    print(f"Lstar contrast: {lstar_red.contrast('white', method='lstar')}")

    # OkLrCh color examples
    lrch_color = Color("oklrch", [0.75, 0.2, 30])
    print(f"\nOkLrCh Color: {lrch_color.to_string()}")
    accessible_lrch = lrch_color.contrasty("black", 4.5)
    print(f"Accessible OkLrCh: {accessible_lrch.to_string()}")
    print(f"Contrast ratio: {accessible_lrch.contrast('black')}")

    # Using APCA contrast method
    green = Color("green")
    apca_green = green.contrasty("black", 60, method="apca")
    print(f"\nOriginal: {green.to_string()}")
    print(f"APCA Accessible: {apca_green.to_string()}")
    print(f"APCA contrast: {apca_green.contrast('black', method='apca')}")

    # Preserving chroma proportion
    vibrant = Color("oklrch", [0.65, 0.3, 130])
    vibrant_accessible = vibrant.contrasty("white", 4.5, preserve_chroma=True)
    print(f"\nOriginal vibrant: {vibrant.to_string()}")
    print(f"Accessible vibrant: {vibrant_accessible.to_string()}")
    print(f"Contrast ratio: {vibrant_accessible.contrast('white')}")
    
    # Delta Phi Star tests
    blue = Color("blue")
    delta_phi_darker = blue.contrasty("white", 30, method="delta-phi")
    delta_phi_lighter = blue.contrasty("black", -30, method="delta-phi")
    
    print(f"\nOriginal: {blue.to_string()}")
    print(f"Delta Phi darker: {delta_phi_darker.to_string(hex=True)}")
    print(f"Delta Phi contrast: {delta_phi_darker.contrast('white', method='delta-phi')}")
    print(f"Delta Phi lighter: {delta_phi_lighter.to_string(hex=True)}")
    print(f"Delta Phi contrast: {delta_phi_lighter.contrast('black', method='delta-phi')}")
    
    # Compare different contrast methods on the same color
    sample = Color("hsl", [120, 80, 50])  # A vivid green
    print(f"\nOriginal sample: {sample.to_string()}")
    
    # Apply different contrast methods and compare
    wcag_sample = sample.contrasty("white", 4.5)  # WCAG AA
    apca_sample = sample.contrasty("white", 60, method="apca")  # APCA 60
    lstar_sample = sample.contrasty("white", 45, method="lstar")  # Lstar difference of 45
    delta_phi_sample = sample.contrasty("white", 20, method="delta-phi")  # Delta Phi 20
    
    print(f"WCAG (4.5:1): {wcag_sample.to_string(hex=True)} - {wcag_sample.contrast('white')}")
    print(f"APCA (60): {apca_sample.to_string(hex=True)} - {apca_sample.contrast('white', method='apca')}")
    print(f"Lstar (45): {lstar_sample.to_string(hex=True)} - {lstar_sample.contrast('white', method='lstar')}")
    print(f"Delta Phi (20): {delta_phi_sample.to_string(hex=True)} - {delta_phi_sample.contrast('white', method='delta-phi')}")