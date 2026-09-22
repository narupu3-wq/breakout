"""Read-only event diagnosis; hourly totals come exclusively from saved reports.

Run from the project root. Output goes to stdout; fixed as-of excludes later data.
Signal grouping removes candidate duplicates, not temporal market dependence.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = "experiments/resume-20260914-v1/reports/hourly/20260922T010219396702Z-02e2e838/report.json"
PREVIOUS = "experiments/resume-20260914-v1/reports/hourly/20260921T220153985269Z-96096dd0/report.json"


def main():
    current = json.loads((ROOT / CURRENT).read_text())
    previous = json.loads((ROOT / PREVIOUS).read_text())
    assert current["run"] == previous["run"]
    db = ROOT / "experiments/resume-20260914-v1/data/research.sqlite3"
    con = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    con.execute("BEGIN")
    cfg = json.loads(con.execute("SELECT manifest FROM runs WHERE id=?",
                                (current["run"],)).fetchone()[0])["config"]
    rows = [dict(id=i, candidate=n, ts=t, kind=k, payload=json.loads(p))
            for i, n, t, k, p in con.execute(
                "SELECT id,candidate,ts,kind,payload FROM events "
                "WHERE run=? AND ts<=? AND kind IN ('intent','paper_fill','close') "
                "ORDER BY id", (current["run"], current["as_of"]))]
    con.close()
    intents, positions, last_close, trades = {}, {}, {}, []
    for row in rows:
        n, p = row["candidate"], row["payload"]
        if row["kind"] == "intent":
            intents[n] = row
        elif row["kind"] == "paper_fill":
            assert n not in positions
            intent = intents.pop(n)
            assert intent["ts"] == row["ts"]
            positions[n] = (intent, row, last_close.get(n))
        else:
            intent, fill, prior = positions.pop(n)
            e = fill["payload"]
            assert e["symbol"] == p["symbol"]
            mult = 2 if n.endswith("-stress") else 1
            gross = e["qty"] * e["side"] * (p["price"] - e["entry"])
            exit_fee = e["qty"] * p["price"] * cfg["costs"]["fee_per_side"] * mult
            carry = gross - exit_fee - e["entry_fee"] - p["net_pnl"]
            assert carry >= -1e-8
            trades.append(dict(
                candidate=n, symbol=e["symbol"],
                signal_ts=intent["payload"]["signal"]["signal_ts"], side=e["side"],
                intent=intent, fill=fill, close=row, previous_close=prior,
                seconds_after_candle_close=fill["ts"]-intent["payload"]["signal"]["signal_ts"]-900,
                hold_seconds=row["ts"]-fill["ts"],
                reentry_seconds=None if prior is None else fill["ts"]-prior["ts"],
                gross_after_slippage=gross, entry_fee=e["entry_fee"],
                exit_fee=exit_fee, carry_inferred=carry, net=p["net_pnl"]))
            last_close[n] = row
    groups = {}
    for trade in trades:
        if trade["symbol"] == "BTCUSD" and trade["candidate"].startswith("trend-"):
            key = (trade["symbol"], trade["signal_ts"], trade["side"])
            groups.setdefault(key, []).append(trade)
    selected = [dict(symbol=k[0], signal_ts=k[1], side=k[2], variants=groups[k])
                for k in sorted(groups, key=lambda k: k[1])[-3:]]
    old = {x["candidate"]: x for x in previous["candidates"]}
    result = dict(
        run=current["run"], as_of=current["as_of"],
        previous_report=PREVIOUS, current_report=CURRENT,
        previous_as_of=previous["as_of"],
        event_delta={k: current["events"].get(k, 0)-previous["events"].get(k, 0)
                     for k in sorted(set(current["events"]) | set(previous["events"]))},
        candidate_delta=[dict(candidate=x["candidate"],
                              closed=x["closed_total"]-old[x["candidate"]]["closed_total"],
                              net=x["net_total"]-old[x["candidate"]]["net_total"])
                         for x in current["candidates"]],
        btc_ask_change_percent=(current["quotes"]["BTCUSD"]["ask"] /
                                previous["quotes"]["BTCUSD"]["ask"]-1)*100,
        last_three_closed_btc_trend_signal_groups=selected,
        closes_since_previous=[t for t in trades if t["close"]["ts"] > previous["as_of"]],
        limitations=[
            "Retrospective diagnosis of used forward evidence, not an untouched holdout.",
            "Grouping by symbol/signal_ts/side removes variants, not serial dependence.",
            "Gross includes modeled slippage; inferred carry uses the frozen accounting identity.",
            "Previous close may concern a different symbol; inspect its payload before interpreting re-entry.",
            "No strategy change, counterfactual performance claim, or live execution."])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
