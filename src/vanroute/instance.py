"""Vehicle routing problems with time windows (VRPTW) in the Solomon benchmark text format."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Customer:
    id: int
    x: float
    y: float
    demand: int
    ready: float
    due: float
    service: float


@dataclass
class Instance:
    name: str
    vehicles: int
    capacity: int
    customers: list[Customer]  # index 0 is the depot

    @property
    def depot(self) -> Customer:
        return self.customers[0]

    def dist(self, a: int, b: int) -> float:
        ca, cb = self.customers[a], self.customers[b]
        return math.hypot(ca.x - cb.x, ca.y - cb.y)


class FormatError(ValueError):
    pass


def parse_solomon(text: str) -> Instance:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines:
        raise FormatError("empty file")
    name = lines[0]
    try:
        v_idx = next(i for i, ln in enumerate(lines) if ln.upper().startswith("VEHICLE"))
        c_idx = next(i for i, ln in enumerate(lines) if ln.upper().startswith("CUSTOMER"))
    except StopIteration:
        raise FormatError("missing VEHICLE or CUSTOMER section") from None
    vehicles, capacity = (int(v) for v in lines[v_idx + 2].split()[:2])
    customers = []
    for ln in lines[c_idx + 1:]:
        parts = ln.split()
        if not parts[0].isdigit():  # column header line
            continue
        if len(parts) != 7:
            raise FormatError(f"customer line needs 7 columns: {ln!r}")
        cid, x, y, demand, ready, due, service = parts
        customers.append(Customer(int(cid), float(x), float(y), int(demand), float(ready), float(due), float(service)))
    if not customers or customers[0].id != 0:
        raise FormatError("first customer must be the depot (id 0)")
    if [c.id for c in customers] != list(range(len(customers))):
        raise FormatError("customer ids must be 0..n-1 in order")
    return Instance(name, vehicles, capacity, customers)


def load_solomon(path: str | Path) -> Instance:
    return parse_solomon(Path(path).read_text())
