"""Tests des carrières des joueurs formés (`ftna.careers`) sur données synthétiques."""

import math

import pandas as pd
import pytest
from conftest import frame

from ftna.careers import (
    ACADEMIES,
    Academy,
    academy_departures,
    academy_players,
    academy_summary,
    bootstrap_capture_ci,
    capture_ratio,
    elite_seasons,
    later_value,
    pooled_departures,
    prepare_moves,
)
from ftna.data import RAW_DIR


def test_prepare_moves_drops_end_of_loan_and_keeps_raw_order():
    t = frame(
        [
            (1, 2015, 10, 20, 0, "Loan"),
            (1, 2015, 20, 10, 0, "End of loan"),
            (1, 2016, 30, 40, 0, "Not loan"),
        ]
    )
    m = prepare_moves(t)
    assert list(m.transfer_type) == ["Loan", "Not loan"]
    # position dans le fichier brut : départage des mouvements d'une même année
    assert list(m.row) == [0, 2]


def test_prepare_moves_sorts_by_player_then_year_then_row():
    t = frame(
        [
            (2, 2016, 1, 2, 0, "Unknown"),
            (1, 2017, 1, 2, 0, "Unknown"),
            (1, 2015, 3, 4, 0, "Unknown"),
        ]
    )
    m = prepare_moves(t)
    assert list(zip(m.player_id, m.year)) == [(1, 2015), (1, 2017), (2, 2016)]


def test_elite_seasons_ranks_by_max_value_per_club_season():
    cl = pd.DataFrame(
        {
            "club_id": [1, 1, 2, 3],
            "season": [2015] * 4,
            "market_value": [10, 500, 300, 100],  # doublon (1, 2015) : maximum = 500
        }
    )
    assert elite_seasons(cl, top_n=2) == frozenset({(1, 2015), (2, 2015)})


def test_academy_players_uses_first_youth_entry_within_window():
    a = Academy("X", 1, frozenset({2}))
    moves = prepare_moves(
        frame(
            [
                (7, 2007, 99, 2, 0, "Unknown"),
                (7, 2010, 99, 2, 0, "Unknown"),
                (8, 2012, 99, 2, 0, "Unknown"),
            ]
        )
    )
    # 7 est entré en 2007, hors de la fenêtre 2008–2019
    assert academy_players(moves, a).to_dict() == {8: 2012}


def test_academy_organisation_includes_first_team():
    a = Academy("X", 1, frozenset({2, 3}))
    assert a.organisation == frozenset({1, 2, 3})


@pytest.mark.skipif(
    not (RAW_DIR / "clubs.csv").exists(), reason="données brutes absentes"
)
def test_academy_ids_exist_in_clubs_csv():
    ids = set(pd.read_csv(RAW_DIR / "clubs.csv", usecols=["id"]).id)
    assert len(ACADEMIES) == 15 and ACADEMIES[0].name == "PSG"
    for academy in ACADEMIES:
        assert academy.organisation <= ids, academy.name


ACAD = Academy("X", 1, frozenset({2}))


def test_departure_ignores_internal_moves_and_loans():
    # même année : prêt depuis la réserve, puis montée en équipe première, puis vente
    moves = prepare_moves(
        frame(
            [
                (5, 2015, 2, 50, 0, "Loan"),
                (5, 2015, 2, 1, 0, "Unknown"),
                (5, 2017, 1, 60, 3e6, "Not loan"),
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    assert dep.loc[5, "joined_club_id"] == 60
    assert dep.loc[5, "transfer_fee"] == 3e6


def test_departure_to_pseudo_club_counts_as_release():
    moves = prepare_moves(frame([(5, 2016, 2, 515, 0, "Unknown")]))
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    assert dep.loc[5, "joined_club_id"] == 515


def test_departure_only_for_given_players():
    moves = prepare_moves(
        frame([(5, 2016, 2, 60, 0, "Unknown"), (6, 2016, 2, 60, 0, "Unknown")])
    )
    assert list(academy_departures(moves, ACAD, pd.Index([6])).index) == [6]


def test_later_value_window_stops_at_return_to_academy():
    # départ, vente tierce, rachat, revente par l'académie, puis vente tierce : seule
    # la vente tierce d'avant le retour appartient au premier départ
    moves = prepare_moves(
        frame(
            [
                (5, 2018, 1, 60, 0, "Not loan"),
                (5, 2019, 60, 65, 7e6, "Not loan"),
                (5, 2020, 65, 1, 4e6, "Not loan"),  # rachat par l'académie
                (5, 2022, 1, 70, 50e6, "Not loan"),  # revente par l'académie
                (5, 2023, 70, 80, 20e6, "Not loan"),  # après le retour : exclue
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset({(80, 2023)}))
    assert out.loc[5, "later_max_fee"] == 7e6
    assert out.loc[5, "later_buyer"] == 65
    assert not bool(out.loc[5, "reached_elite"])
    assert bool(out.loc[5, "bought_back"])


def test_bought_back_ignores_internal_promotion_recorded_after_sale():
    # cas Adli : la montée réserve → équipe première est enregistrée après la vente
    moves = prepare_moves(
        frame(
            [
                (5, 2018, 1, 60, 5.5e6, "Not loan"),
                (5, 2018, 2, 1, 0, "Unknown"),
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset())
    assert not bool(out.loc[5, "bought_back"])


def test_later_value_includes_same_year_sale_recorded_before_departure():
    # cas Raúl de Tomás : la revente apparaît avant le départ dans le fichier
    moves = prepare_moves(
        frame(
            [
                (5, 2019, 60, 70, 22.5e6, "Not loan"),
                (5, 2019, 1, 60, 20e6, "Not loan"),
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset())
    assert out.loc[5, "later_max_fee"] == 22.5e6


def test_later_value_respects_order_within_same_year():
    # vente ultérieure la même année que le départ, mais après lui dans le fichier
    moves = prepare_moves(
        frame(
            [
                (5, 2018, 1, 60, 2e6, "Not loan"),
                (5, 2018, 60, 70, 9e6, "Not loan"),
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset())
    assert out.loc[5, "later_max_fee"] == 9e6
    assert out.loc[5, "later_fee_sum"] == 9e6  # l'indemnité de départ n'est pas comptée
    assert not bool(out.loc[5, "reached_elite"])


def test_later_value_without_later_move():
    moves = prepare_moves(frame([(5, 2018, 1, 60, 2e6, "Not loan")]))
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset())
    assert out.loc[5, "later_max_fee"] == 0
    assert pd.isna(out.loc[5, "later_buyer"])
    assert not bool(out.loc[5, "bought_back"])


def test_capture_ratio_nan_when_no_later_fee():
    df = pd.DataFrame({"transfer_fee": [1e6], "later_max_fee": [0.0]})
    assert math.isnan(capture_ratio(df))
    assert all(math.isnan(x) for x in bootstrap_capture_ci(df, n_boot=50))


def test_capture_ratio_value():
    df = pd.DataFrame({"transfer_fee": [15e6, 0.0], "later_max_fee": [60e6, 20e6]})
    assert capture_ratio(df) == pytest.approx(15 / 80)


def test_bootstrap_ci_brackets_ratio_and_is_deterministic():
    df = pd.DataFrame(
        {
            "transfer_fee": [15e6, 0.0, 1e6, 0.0, 5e6],
            "later_max_fee": [60e6, 20e6, 16e6, 0.0, 5e6],
        }
    )
    lo, hi = bootstrap_capture_ci(df, n_boot=200, seed=42)
    assert lo <= capture_ratio(df) <= hi
    assert (lo, hi) == bootstrap_capture_ci(df, n_boot=200, seed=42)


def test_academy_summary_counts_only_evaluable_departures():
    acad = Academy("Y", 1, frozenset({2}))
    moves = prepare_moves(
        frame(
            [
                (5, 2010, 99, 2, 0, "Unknown"),
                (5, 2014, 2, 60, 1e6, "Not loan"),
                (5, 2017, 60, 70, 10e6, "Not loan"),  # élite à 3 ans : dans l'horizon
                (6, 2015, 99, 2, 0, "Unknown"),
                (6, 2022, 2, 61, 0, "Unknown"),  # départ après 2021 : non évaluable
            ]
        )
    )
    table, detail = academy_summary(moves, frozenset({(70, 2017)}), academies=(acad,))
    row = table.loc["Y"]
    assert row["players"] == 2 and row["departures"] == 1
    assert row["capture_ratio"] == pytest.approx(0.1)
    assert row["reached_elite_share"] == 1.0
    assert row["bought_back"] == 0
    assert detail["Y"].evaluable.to_dict() == {5: True, 6: False}


def test_departure_row_is_never_mixed_when_values_are_missing():
    # `groupby().first()` prendrait l'indemnité de la ligne suivante
    moves = prepare_moves(
        frame([(5, 2016, 2, 60, 0, "Unknown"), (5, 2017, 1, 61, 3e6, "Not loan")])
    )
    moves.loc[0, "transfer_fee"] = float("nan")
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    assert dep.loc[5, "joined_club_id"] == 60
    assert math.isnan(dep.loc[5, "transfer_fee"])


def test_loan_fee_is_not_later_value():
    moves = prepare_moves(
        frame(
            [
                (5, 2018, 1, 60, 0, "Not loan"),
                (5, 2019, 60, 70, 7e6, "Loan"),  # prêt payant
                (5, 2020, 60, 80, 2e6, "Not loan"),
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5]))
    out = later_value(moves, dep, ACAD, elite=frozenset())
    assert out.loc[5, "later_max_fee"] == 2e6
    assert out.loc[5, "later_buyer"] == 80


def test_reached_elite_within_fixed_horizon():
    moves = prepare_moves(
        frame(
            [
                (5, 2015, 1, 60, 0, "Not loan"),
                (5, 2019, 60, 900, 0, "Not loan"),  # 4 ans après le départ
                (6, 2015, 1, 60, 0, "Not loan"),
                (6, 2018, 60, 900, 0, "Loan"),  # 3 ans, prêt compris
            ]
        )
    )
    dep = academy_departures(moves, ACAD, pd.Index([5, 6]))
    elite = frozenset({(900, 2018), (900, 2019)})
    out = later_value(moves, dep, ACAD, elite=elite)
    assert out.reached_elite.to_dict() == {5: False, 6: True}


def test_pooled_departures_keeps_one_row_per_player():
    a = pd.DataFrame({"year": [2016, 2018]}, index=pd.Index([5, 6], name="player_id"))
    b = pd.DataFrame({"year": [2014]}, index=pd.Index([5], name="player_id"))
    pooled = pooled_departures({"A": a, "B": b})
    assert sorted(pooled.index) == [5, 6]
    assert pooled.loc[5, "year"] == 2014 and pooled.loc[5, "academy"] == "B"
