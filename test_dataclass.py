from dataclasses import dataclass, field

@dataclass
class A:
    b: 'B' = field(default_factory=lambda: B())

@dataclass
class B:
    x: int = 1

print(A())
