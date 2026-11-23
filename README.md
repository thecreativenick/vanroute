# vanroute

A delivery route planner for vans with capacities and time windows (VRPTW). Orders come in
overnight; by morning every van has a route, a map and a printable driver sheet.

## Status

Early scaffold. Done so far:

- Parser for the Solomon benchmark text format.
- Route and whole-plan checker: capacity, time windows (with waiting), depot hours, every
  customer served exactly once, vehicle count.
- A nearest-neighbour construction heuristic that produces feasible start solutions.

## Planned milestones

1. Local search: 2-opt, relocate, exchange and cross moves with fast feasibility checks.
2. Metaheuristic: adaptive large neighbourhood search, with vehicle count minimised first.
3. Benchmark runner over all 56 Solomon instances, compared with best-known results.
4. Localhost route-map page and per-van PDF driver sheets.

## Success bar

Routes land within 5% of best-known results on the Solomon benchmarks, each solved in under a
minute on 4 CPU cores.

## Development

```bash
pip install -e .[dev]
pytest
```
