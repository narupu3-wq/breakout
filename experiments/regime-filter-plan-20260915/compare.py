#!/usr/bin/env python3
"""Run the pre-registered BTC direction-filter comparison offline.

The source experiment is treated as read-only.  This module freezes the
selected candles, configuration, and source hashes below a new results
directory, then runs the two paper arms with the frozen ``engine.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple


EXPERIMENT_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EXPERIMENT_ROOT.parent / "resume-20260914-v1"
DEFAULT_DB = SOURCE_ROOT / "data" / "research.sqlite3"
DEFAULT_CONFIG = SOURCE_ROOT / "config" / "research-v1.json"
DEFAULT_RESULTS = EXPERIMENT_ROOT / "results"
DEFAULT_START = 1788732000
DEFAULT_END = 1789380000
SYMBOLS = ("BTCUSD", "ETHUSD")
BAR_SECONDS = 900
SOURCE_FILES = ("engine.py", "research.py", "market_data.py")


def encoded(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class DataGapError(ValueError):
    """The selected symbols do not share the required contiguous candle grid."""

    def __init__(self, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.details = dict(details)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(path: Path = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Load the already validated source config without contacting any API."""
    cfg = load_json(path)
    if cfg.get("mode") != "paper_only" or cfg.get("breakout_execution_verified") is not False:
        raise ValueError("source config is not the paper-only configuration")
    if cfg.get("symbols") != list(SYMBOLS) or cfg.get("interval_minutes") != 15:
        raise ValueError("source config has an unsupported symbol or interval")
    if len(cfg.get("risk_candidates", [])) != 2:
        raise ValueError("comparison requires the two pre-registered risk candidates")
    if cfg.get("strategy", {}).get("lookback") != 32:
        raise ValueError("comparison requires the pre-registered 32-bar lookback")
    return cfg


def _read_window(db_path: Path, start: int, end: int,
                 symbols: Sequence[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Read candles in one read-only SQLite transaction."""
    uri = "file:" + str(db_path.resolve()) + "?mode=ro"
    db = sqlite3.connect(uri, uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        result: Dict[str, List[Dict[str, Any]]] = {}
        for symbol in symbols:
            rows = db.execute(
                "SELECT ts,payload FROM candles "
                "WHERE symbol=? AND ts>=? AND ts<? ORDER BY ts",
                (symbol, start, end),
            ).fetchall()
            candles = []
            for row_ts, raw in rows:
                bar = json.loads(raw)
                if bar.get("ts") != row_ts:
                    raise ValueError("candle payload timestamp disagrees with its key")
                candles.append(bar)
            result[symbol] = candles
        db.rollback()
        return result
    finally:
        db.close()


def validate_timestamps(markets: Mapping[str, Sequence[Mapping[str, Any]]],
                        start: int = DEFAULT_START, end: int = DEFAULT_END,
                        interval: int = BAR_SECONDS,
                        symbols: Sequence[str] = SYMBOLS) -> Dict[str, Any]:
    """Require identical, complete, contiguous timestamps for both symbols."""
    expected = list(range(start, end, interval))
    timestamps = {s: [int(bar["ts"]) for bar in markets.get(s, ())] for s in symbols}
    ranges = {
        s: {"count": len(ts), "first": ts[0] if ts else None,
            "last": ts[-1] if ts else None}
        for s, ts in timestamps.items()
    }
    missing = {s: [ts for ts in expected if ts not in set(values)]
               for s, values in timestamps.items()}
    unexpected = {s: [ts for ts in values if ts not in set(expected)]
                  for s, values in timestamps.items()}
    gaps = {
        s: [[a, b] for a, b in zip(values, values[1:]) if b - a != interval]
        for s, values in timestamps.items()
    }
    identical = len({tuple(values) for values in timestamps.values()}) == 1
    valid = (all(not missing[s] and not unexpected[s] and not gaps[s]
                 for s in symbols)
             and identical and all(timestamps[s] == expected for s in symbols))
    details = {
        "start": start,
        "end_exclusive": end,
        "interval_seconds": interval,
        "expected_count": len(expected),
        "identical_timestamps": identical,
        "ranges": ranges,
        "missing": missing,
        "unexpected": unexpected,
        "gaps": gaps,
    }
    if not valid:
        raise DataGapError("BTCUSD/ETHUSD timestamps are not identical and contiguous",
                           details)
    return details


def _frozen_json(path: Path, value: Any) -> str:
    """Write a canonical JSON file once and return its byte hash."""
    data = encoded(value).encode("utf-8")
    if path.exists() and path.read_bytes() != data:
        raise ValueError("frozen input changed: {}".format(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    return sha256_bytes(data)


def _freeze_source_and_config(results: Path, config_path: Path) -> Tuple[Path, Path, Dict[str, str]]:
    frozen_source = results / "source"
    frozen_source.mkdir(parents=True, exist_ok=True)
    source_hashes: Dict[str, str] = {}
    for name in SOURCE_FILES:
        source = SOURCE_ROOT / name
        target = frozen_source / name
        if not target.exists():
            shutil.copyfile(source, target)
        if target.read_bytes() != source.read_bytes():
            raise ValueError("source changed after it was frozen: {}".format(name))
        source_hashes[name] = sha256_file(target)

    frozen_config = results / "config.json"
    cfg = load_config(config_path)
    config_hash = _frozen_json(frozen_config, cfg)
    source_hashes["config.json"] = config_hash
    return frozen_source, frozen_config, source_hashes


def _load_engine(path: Path):
    module_name = "breakout_frozen_engine_" + sha256_file(path)[:16]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load frozen engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _candidate_specs(cfg: Mapping[str, Any]) -> Iterable[Tuple[str, str, Mapping[str, Any], float]]:
    for risk in cfg["risk_candidates"]:
        for kind in ("trend", "mean_reversion"):
            for multiplier in (1.0, float(cfg["gates"]["required_stress_cost_multiplier"])):
                suffix = "-stress" if multiplier > 1 else ""
                yield kind + "-" + risk["name"] + suffix, kind, risk, multiplier


def should_block_btc_mean_reversion(symbol: str, kind: str,
                                     sig: Mapping[str, Any],
                                     history: Sequence[Mapping[str, Any]]) -> bool:
    """Apply only the pre-registered BTC mean-reversion direction rule."""
    if symbol != "BTCUSD" or kind != "mean_reversion" or not sig:
        return False
    if len(history) < 33:
        raise ValueError("direction filter requires 33 completed bars")
    current = history[-1]
    move = current["close"] / history[-33]["close"] - 1
    return sig["side"] * move < 0


def simulate_arm(cfg: Mapping[str, Any],
                 markets: Mapping[str, Sequence[Mapping[str, Any]]],
                 engine: Any, filtered: bool,
                 start: int = DEFAULT_START, end: int = DEFAULT_END) -> Dict[str, Any]:
    """Run the exact history_run loop in a private, non-SQLite wrapper."""
    validation = validate_timestamps(markets, start, end, BAR_SECONDS, SYMBOLS)
    common = [int(ts) for ts in range(validation["start"], validation["end_exclusive"],
                                      validation["interval_seconds"])]
    histories = {symbol: list(markets[symbol]) for symbol in SYMBOLS}
    indices = {symbol: {bar["ts"]: i for i, bar in enumerate(histories[symbol])}
               for symbol in SYMBOLS}
    results: Dict[str, Any] = {}
    Account, make_signal = engine.Account, engine.signal
    for name, kind, risk, multiplier in _candidate_specs(cfg):
        account = Account(cfg, risk, cost_multiplier=multiplier)
        signals_seen = 0
        filtered_signals = 0
        open_attempts = 0
        for ts in common:
            account.reset_day(ts)
            position = account.s["position"]
            if position:
                account.bar(histories[position["symbol"]][indices[position["symbol"]][ts]])
            else:
                for symbol in SYMBOLS:
                    i = indices[symbol][ts]
                    history = histories[symbol][:i]
                    sig = make_signal(history, kind, cfg["strategy"])
                    bar = histories[symbol][i]
                    if sig:
                        signals_seen += 1
                        if (filtered and should_block_btc_mean_reversion(symbol, kind, sig, history)):
                            filtered_signals += 1
                            continue
                        open_attempts += 1
                        half = cfg["costs"]["backtest_spread_bps"] * multiplier / 20000
                        available = histories[symbol][i - 1]["volume"] * 0.01 if i else 0
                        if account.open(ts, symbol, sig,
                                        bar["open"] * (1 - half),
                                        bar["open"] * (1 + half), available):
                            account.bar(bar)
                            break
            account.events = []
        if account.s["position"]:
            position = account.s["position"]
            bar = histories[position["symbol"]][indices[position["symbol"]][common[-1]]]
            half = cfg["costs"]["backtest_spread_bps"] * multiplier / 20000
            account.close(common[-1] + 899,
                          bar["close"] * (1 - half * position["side"]),
                          "end_of_sample")
            account.events = []
        results[name] = {
            "summary": account.summary(),
            "signals_seen": signals_seen,
            "filtered_signals": filtered_signals,
            "open_attempts": open_attempts,
        }
    return results


def _comparison_deltas(baseline: Mapping[str, Any], filtered: Mapping[str, Any]) -> Dict[str, Any]:
    deltas: Dict[str, Any] = {}
    for name in baseline:
        before = baseline[name]["summary"]
        after = filtered[name]["summary"]
        deltas[name] = {
            "net_realized": after["net_realized"] - before["net_realized"],
            "max_drawdown": after["max_drawdown"] - before["max_drawdown"],
            "closed_trades": after["closed_trades"] - before["closed_trades"],
            "halt_changed": after["halt"] != before["halt"],
        }
    return deltas


def _write_sha(path: Path, digest: str) -> None:
    _frozen_json(path, digest) if path.suffix == ".json" else _write_text_once(path, digest + "\n")


def _write_text_once(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if path.exists() and path.read_bytes() != data:
        raise ValueError("frozen result changed: {}".format(path))
    if not path.exists():
        path.write_bytes(data)


def _report_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# BTC方向フィルター比較結果",
        "",
        "status: ``{}``".format(payload["status"]),
        "",
        "期間: {} <= ts < {}（{}本、15分足）".format(
            payload["window"]["start"], payload["window"]["end_exclusive"],
            payload["validation"].get("expected_count", 0)),
        "",
    ]
    if payload["status"] != "complete":
        lines += ["比較は停止しました。", "", payload.get("error", "unknown error"), ""]
        return "\n".join(lines)
    lines += ["| candidate | arm | net realized | max DD | closed | halt |", "|---|---|---:|---:|---:|---|"]
    for name in payload["candidate_order"]:
        for arm in ("baseline", "btc_mean_reversion_filter"):
            summary = payload["arms"][arm][name]["summary"]
            lines.append("| {} | {} | {:.6f} | {:.6f} | {} | {} |".format(
                name, arm, summary["net_realized"], summary["max_drawdown"],
                summary["closed_trades"], summary["halt"] or ""))
    return "\n".join(lines) + "\n"


def run_comparison(db_path: Path = DEFAULT_DB, output_dir: Path = DEFAULT_RESULTS,
                   start: int = DEFAULT_START, end: int = DEFAULT_END) -> Dict[str, Any]:
    if end <= start or (end - start) % BAR_SECONDS:
        raise ValueError("comparison window must be a positive whole number of 15-minute bars")
    results = Path(output_dir)
    frozen_source, frozen_config_path, source_hashes = _freeze_source_and_config(results, DEFAULT_CONFIG)
    cfg = load_config(frozen_config_path)
    engine = _load_engine(frozen_source / "engine.py")

    data_path = results / "input-data.json"
    data_sha_path = results / "input-data.sha256"
    if data_path.exists():
        data_payload = load_json(data_path)
        input_hash = sha256_file(data_path)
        recorded = data_sha_path.read_text(encoding="utf-8").strip() if data_sha_path.exists() else ""
        if recorded != input_hash:
            raise ValueError("input-data.sha256 does not match frozen input-data.json")
        markets = {s: data_payload["candles"][s] for s in SYMBOLS}
    else:
        markets = _read_window(Path(db_path), start, end, SYMBOLS)
        data_payload = {
            "schema": 1,
            "source_db": str(Path(db_path).resolve()),
            "window": {"start": start, "end_exclusive": end, "interval_seconds": BAR_SECONDS},
            "symbols": list(SYMBOLS),
            "candles": markets,
        }
        input_hash = _frozen_json(data_path, data_payload)
        _write_text_once(data_sha_path, input_hash + "\n")

    window = data_payload.get("window", {})
    if (window.get("start"), window.get("end_exclusive"), window.get("interval_seconds")) != (start, end, BAR_SECONDS):
        raise ValueError("frozen input window differs from requested window")

    provenance = {
        "schema": 1,
        "experiment": "regime-filter-plan-20260915",
        "registered_hypothesis": "BTC mean_reversion entries are skipped when side*(current.close/history[-33].close-1)<0",
        "source_db": str(Path(db_path).resolve()),
        "window": window,
        "symbols": list(SYMBOLS),
        "input_data": {"path": str(data_path), "sha256": input_hash},
        "source_hashes": source_hashes,
    }
    try:
        validation = validate_timestamps(markets, start, end, BAR_SECONDS, SYMBOLS)
    except DataGapError as exc:
        provenance["validation"] = exc.details
        provenance["status"] = "halted_data_gap"
        provenance_hash = _frozen_json(results / "provenance.json", provenance)
        _write_text_once(results / "provenance.sha256", provenance_hash + "\n")
        halted = {
            "schema": 1, "status": "halted_data_gap", "window": window,
            "validation": exc.details, "error": str(exc), "arms": {},
        }
        _frozen_json(results / "comparison.json", halted)
        _write_text_once(results / "comparison.md", _report_markdown(halted))
        return halted

    provenance["validation"] = validation
    provenance["status"] = "complete"
    provenance_hash = _frozen_json(results / "provenance.json", provenance)
    _write_text_once(results / "provenance.sha256", provenance_hash + "\n")

    baseline = simulate_arm(cfg, markets, engine, filtered=False, start=start, end=end)
    filtered = simulate_arm(cfg, markets, engine, filtered=True, start=start, end=end)
    order = list(baseline)
    payload = {
        "schema": 1,
        "status": "complete",
        "window": window,
        "validation": validation,
        "candidate_order": order,
        "arms": {"baseline": baseline, "btc_mean_reversion_filter": filtered},
        "deltas_filter_minus_baseline": _comparison_deltas(baseline, filtered),
        "promotion": {"eligible": False, "reason": "pre-registered exploratory comparison; no promotion"},
    }
    _frozen_json(results / "comparison.json", payload)
    _write_text_once(results / "comparison.md", _report_markdown(payload))
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--start", type=int, default=DEFAULT_START)
    parser.add_argument("--end", type=int, default=DEFAULT_END)
    args = parser.parse_args(argv)
    try:
        payload = run_comparison(args.db, args.output_dir, args.start, args.end)
    except (DataGapError, ValueError, sqlite3.Error) as exc:
        print("comparison failed: {}".format(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
