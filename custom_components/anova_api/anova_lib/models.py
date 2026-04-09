"""Data models for the Anova API."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class DeviceType(str, Enum):
    """Enumeration of supported device type categories."""
    APC = "APC"  # Precision Cooker
    APO = "APO"  # Precision Oven


class TemperatureUnit(str, Enum):
    """Enumeration of temperature units."""
    C = "C"
    F = "F"


@dataclass
class AnovaDevice:
    """Represents a discovered Anova device."""
    device_id: str
    type: DeviceType
    model: str  # e.g., 'oven_v1', 'oven_v2', 'a3', 'pro'
    name: str = "Unknown Device"


@dataclass
class TemperatureState:
    """State of a temperature reading."""
    current: float = 0.0
    setpoint: float = 0.0


@dataclass
class HeaterState:
    """State of a heating element."""
    on: bool = False


@dataclass
class FanState:
    """State of the convection fan."""
    speed: int = 0  # 0 to 100


@dataclass
class VentState:
    """State of the exhaust vent (APO)."""
    open: bool = False


@dataclass
class TimerState:
    """State of the cooking timer."""
    running: bool = False
    initial: int = 0  # Initial timer value in seconds
    remaining: int = 0  # Remaining time in seconds


@dataclass
class APCState:
    """Current state of a Precision Cooker."""
    state: str = "idle"  # idle, preheating, cooking
    target_temperature: float = 0.0
    current_temperature: float = 0.0
    unit: TemperatureUnit = TemperatureUnit.C
    timer: TimerState = field(default_factory=TimerState)
    is_running: bool = False


@dataclass
class APOState:
    """Current state of a Precision Oven."""
    state: str = "idle"
    dry_bulb: TemperatureState = field(default_factory=TemperatureState)
    wet_bulb: TemperatureState = field(default_factory=TemperatureState)
    probe: TemperatureState = field(default_factory=TemperatureState)
    
    top_heater: HeaterState = field(default_factory=HeaterState)
    bottom_heater: HeaterState = field(default_factory=HeaterState)
    rear_heater: HeaterState = field(default_factory=HeaterState)
    
    fan: FanState = field(default_factory=FanState)
    vent: VentState = field(default_factory=VentState)
    
    humidity_setpoint: int = 0
    steam_percentage: int = 0
    
    timer: TimerState = field(default_factory=TimerState)
    is_running: bool = False
    
    # Track the raw telemetry payload for advanced integrations
    raw_state: Dict[str, Any] = field(default_factory=dict)
