import random

import pytest

from vanroute import FormatError, check_route, check_solution, nearest_neighbor, parse_solomon

# A tiny made-up instance in Solomon's layout.
TINY = """
TINY1

VEHICLE
NUMBER     CAPACITY
  3          20

CUSTOMER
CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME  DUE DATE   SERVICE   TIME

    0      0          0          0          0        200          0
    1      3          4         10          0         50          5
    2      6          8         10         10         60          5
    3     -3         -4          5          0        100          5
    4      0         10         15         30        120          5
"""


def random_instance(n, seed):
    rng = random.Random(seed)
    rows = ["    0  50  50  0  0  1000  0"]
    for i in range(1, n + 1):
        ready = rng.randint(100, 600)  # late enough that every customer is reachable
        rows.append(f"  {i}  {rng.randint(0, 100)}  {rng.randint(0, 100)}  {rng.randint(1, 20)}  {ready}  {ready + rng.randint(60, 300)}  10")
    text = f"RAND{seed}\nVEHICLE\nNUMBER CAPACITY\n {n} 100\nCUSTOMER\nCUST NO. X Y DEMAND READY DUE SERVICE\n" + "\n".join(rows)
    return parse_solomon(text)


def test_parse_tiny():
    inst = parse_solomon(TINY)
    assert inst.name == "TINY1"
    assert (inst.vehicles, inst.capacity) == (3, 20)
    assert len(inst.customers) == 5
    assert inst.dist(0, 1) == pytest.approx(5.0)


def test_route_check_waits_and_measures():
    inst = parse_solomon(TINY)
    rep = check_route(inst, [1, 2])
    assert rep.feasible
    assert rep.load == 20
    assert rep.distance == pytest.approx(5 + 5 + 10)


def test_route_check_flags_capacity_and_lateness():
    inst = parse_solomon(TINY)
    rep = check_route(inst, [1, 2, 4])
    assert not rep.feasible
    assert any("capacity" in e for e in rep.errors)


def test_solution_check_detects_missing_customer():
    inst = parse_solomon(TINY)
    ok, _, errors = check_solution(inst, [[1, 2], [3]])
    assert not ok and "missing [4]" in errors[0]


def test_nearest_neighbor_is_feasible_on_tiny():
    inst = parse_solomon(TINY)
    ok, total, errors = check_solution(inst, nearest_neighbor(inst))
    assert ok, errors
    assert total > 0


@pytest.mark.parametrize("seed", range(10))
def test_nearest_neighbor_is_feasible_on_random(seed):
    inst = random_instance(40, seed)
    ok, _, errors = check_solution(inst, nearest_neighbor(inst))
    assert ok, errors


def test_rejects_bad_file():
    with pytest.raises(FormatError):
        parse_solomon("NAME\nno sections here")
