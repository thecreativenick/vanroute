"""Checking routes against capacity and time windows, and a first construction heuristic."""

from __future__ import annotations

from dataclasses import dataclass

from .instance import Instance

Route = list[int]  # customer ids, depot excluded


@dataclass
class RouteReport:
    feasible: bool
    distance: float
    load: int
    errors: list[str]


def check_route(inst: Instance, route: Route) -> RouteReport:
    errors: list[str] = []
    load = sum(inst.customers[c].demand for c in route)
    if load > inst.capacity:
        errors.append(f"load {load} exceeds capacity {inst.capacity}")
    time, dist, prev = 0.0, 0.0, 0
    for c in route:
        leg = inst.dist(prev, c)
        dist += leg
        cust = inst.customers[c]
        time = max(time + leg, cust.ready)  # wait if early
        if time > cust.due + 1e-9:
            errors.append(f"customer {c} reached at {time:.2f}, due {cust.due:.2f}")
        time += cust.service
        prev = c
    back = inst.dist(prev, 0)
    dist += back
    if route and time + back > inst.depot.due + 1e-9:
        errors.append(f"returns to depot at {time + back:.2f}, depot closes {inst.depot.due:.2f}")
    return RouteReport(not errors, dist, load, errors)


def check_solution(inst: Instance, routes: list[Route]) -> tuple[bool, float, list[str]]:
    """Whole-plan check: every customer served exactly once, vehicle count, each route feasible."""
    errors: list[str] = []
    seen = [c for r in routes for c in r]
    expected = set(range(1, len(inst.customers)))
    if sorted(seen) != sorted(expected):
        missing = expected - set(seen)
        dupes = {c for c in seen if seen.count(c) > 1}
        errors.append(f"customers missing {sorted(missing)} duplicated {sorted(dupes)}")
    used = [r for r in routes if r]
    if len(used) > inst.vehicles:
        errors.append(f"uses {len(used)} vehicles, only {inst.vehicles} available")
    total = 0.0
    for i, r in enumerate(used):
        rep = check_route(inst, r)
        total += rep.distance
        errors.extend(f"route {i}: {e}" for e in rep.errors)
    return not errors, total, errors


def nearest_neighbor(inst: Instance) -> list[Route]:
    """Greedy start solution: extend each route with the feasible customer that can start soonest."""
    unserved = set(range(1, len(inst.customers)))
    routes: list[Route] = []
    while unserved:
        route: Route = []
        time, load, prev = 0.0, 0, 0
        while True:
            best, best_start = None, None
            for c in unserved:
                cust = inst.customers[c]
                if load + cust.demand > inst.capacity:
                    continue
                start = max(time + inst.dist(prev, c), cust.ready)
                if start > cust.due or start + cust.service + inst.dist(c, 0) > inst.depot.due:
                    continue
                if best_start is None or (start, inst.dist(prev, c)) < (best_start, inst.dist(prev, best)):
                    best, best_start = c, start
            if best is None:
                break
            route.append(best)
            unserved.discard(best)
            load += inst.customers[best].demand
            time = best_start + inst.customers[best].service
            prev = best
        if not route:
            raise ValueError(f"customers {sorted(unserved)} cannot be served by any single vehicle")
        routes.append(route)
    return routes
