from enum import StrEnum
from typing import ClassVar
import enum

class Role(enum.StrEnum):
    ADMIN: ClassVar[str] = "ADMIN"
    CASHIER: str = "CASHIER"

print(f"Enum members: {list(Role)}")
try:
    print(f"Validation 'ADMIN': {Role('ADMIN')}")
except ValueError as e:
    print(f"Validation 'ADMIN' failed: {e}")

try:
    print(f"Validation 'CASHIER': {Role('CASHIER')}")
except ValueError as e:
    print(f"Validation 'CASHIER' failed: {e}")
