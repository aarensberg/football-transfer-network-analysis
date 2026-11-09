"""Tests des clubs tremplins vers l'élite (`ftna.springboards`) sur données synthétiques."""

import math

import pytest
from conftest import frame

from ftna.careers import prepare_moves
from ftna.springboards import springboard_exits, springboard_rates, wilson_interval


def test_wilson_interval_known_value():
    lo, hi = wilson_interval(14, 97)
    assert lo == pytest.approx(0.0880, abs=1e-3)
    assert hi == pytest.approx(0.2278, abs=1e-3)
    assert all(math.isnan(x) for x in wilson_interval(0, 0))


def test_direct_and_two_hop_within_horizon():
    elite = frozenset({(900, 2012), (900, 2015), (900, 2016)})
    moves = prepare_moves(
        frame(
            [
                (1, 2012, 10, 900, 5e6, "Not loan"),  # direct
                (2, 2012, 10, 20, 0, "Not loan"),
                (2, 2015, 20, 900, 9e6, "Not loan"),  # 2 sauts en 3 ans
                (3, 2012, 10, 20, 0, "Not loan"),
                (3, 2016, 20, 900, 9e6, "Not loan"),  # 4 ans : hors horizon
            ]
        )
    )
    ex = springboard_exits(moves, elite, frozenset()).set_index("player_id")
    ex = ex[ex.left_club_id == 10].sort_index()
    assert ex.direct.tolist() == [True, False, False]
    assert ex.two_hop.tolist() == [False, True, False]
    assert ex.reached.tolist() == [True, True, False]


def test_two_hop_ignores_loan_to_elite():
    elite = frozenset({(900, 2013)})
    moves = prepare_moves(
        frame([(1, 2012, 10, 20, 0, "Not loan"), (1, 2013, 20, 900, 0, "Loan")])
    )
    ex = springboard_exits(moves, elite, frozenset())
    assert not ex[ex.left_club_id == 10].two_hop.any()


def test_exit_excluded_when_player_was_loaned_in_from_elite():
    elite = frozenset({(900, 2011), (900, 2012)})
    moves = prepare_moves(
        frame([(1, 2011, 900, 10, 0, "Loan"), (1, 2012, 10, 900, 0, "Not loan")])
    )
    assert (
        springboard_exits(moves, elite, frozenset()).query("left_club_id == 10").empty
    )


def test_sources_in_elite_or_excluded_are_ignored():
    elite = frozenset({(10, 2012), (900, 2012)})
    moves = prepare_moves(
        frame([(1, 2012, 10, 900, 0, "Not loan"), (2, 2012, 2464, 900, 0, "Not loan")])
    )
    assert springboard_exits(moves, elite, frozenset({2464})).empty


def test_loans_pseudo_clubs_and_years_outside_window_are_not_exits():
    moves = prepare_moves(
        frame(
            [
                (1, 2012, 10, 20, 0, "Loan"),
                (2, 2012, 10, 515, 0, "Unknown"),
                (3, 2009, 10, 20, 0, "Not loan"),
                (4, 2021, 10, 20, 0, "Not loan"),
            ]
        )
    )
    assert springboard_exits(moves, frozenset(), frozenset()).empty


def test_springboard_rates_filters_and_sorts_by_lower_bound():
    elite = frozenset({(900, 2012), (900, 2017)})
    rows = []
    # club 10 : 3 sorties sur 4 vers l'élite (2 en 2012, 1 en 2017) ; club 11 : 1 sur 4
    for pid, (src, year, dst) in enumerate(
        [(10, 2012, 900), (10, 2012, 900), (10, 2017, 900), (10, 2017, 30)]
        + [(11, 2012, 900), (11, 2012, 30), (11, 2012, 30), (11, 2012, 30)]
        + [(12, 2012, 900)]
    ):
        rows.append((pid, year, src, dst, 0, "Not loan"))
    exits = springboard_exits(prepare_moves(frame(rows)), elite, frozenset())
    rates = springboard_rates(exits, min_exits=4)
    assert list(rates.index) == [10, 11]  # club 12 : 1 seule sortie, filtré
    assert rates.loc[10, "rate"] == pytest.approx(0.75)
    assert rates.loc[10, "reached_early"] == 2 and rates.loc[10, "reached_late"] == 1
    assert rates.loc[10, "ci_low"] == pytest.approx(wilson_interval(3, 4)[0])


def test_return_to_elite_lender_is_not_a_springboard_even_out_of_order():
    # prêt entrant enregistré après la sortie, la même année
    elite = frozenset({(900, 2012)})
    moves = prepare_moves(
        frame([(1, 2012, 10, 900, 0, "Not loan"), (1, 2012, 900, 10, 0, "Loan")])
    )
    ex = springboard_exits(moves, elite, frozenset())
    assert not ex[ex.left_club_id == 10].reached.any()


def test_return_to_elite_lender_is_not_a_springboard_after_other_moves():
    # prêté par 900 en 2010, puis prêté ailleurs, puis retour définitif vers 900
    elite = frozenset({(900, 2010), (900, 2012)})
    moves = prepare_moves(
        frame(
            [
                (1, 2010, 900, 10, 0, "Loan"),
                (1, 2011, 10, 40, 0, "Loan"),
                (1, 2012, 10, 900, 0, "Not loan"),
            ]
        )
    )
    ex = springboard_exits(moves, elite, frozenset())
    assert not ex[ex.left_club_id == 10].reached.any()


def test_springboard_rates_by_period():
    elite = frozenset({(900, 2012), (900, 2017)})
    rows = [
        (0, 2012, 10, 900, 0, "Not loan"),
        (1, 2012, 10, 30, 0, "Not loan"),
        (2, 2017, 10, 900, 0, "Not loan"),
    ]
    exits = springboard_exits(prepare_moves(frame(rows)), elite, frozenset())
    rates = springboard_rates(exits, min_exits=1)
    row = rates.loc[10]
    assert (row["exits_early"], row["exits_late"]) == (2, 1)
    assert row["rate_early"] == pytest.approx(0.5)
    assert row["rate_late"] == pytest.approx(1.0)
