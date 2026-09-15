import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("regime_compare", ROOT / "compare.py")
compare = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(compare)


def bars(count=96, start=0, scale=1.0):
    result = []
    for i in range(count):
        close = scale * (100.0 + (10.0 if i % 25 == 10 else 0.0)
                         - (10.0 if i % 25 == 18 else 0.0))
        result.append({"ts": start + i * 900, "open": close,
                       "high": close + scale, "low": close - scale,
                       "close": close, "volume": 100.0})
    return result


def load_reference_research():
    """Load the frozen history_run with its own engine/module bindings."""
    source = compare.SOURCE_ROOT
    saved = {name: sys.modules.get(name) for name in ("engine", "market_data")}
    try:
        loaded = {}
        for name in ("engine", "market_data"):
            module_spec = importlib.util.spec_from_file_location(
                name, source / (name + ".py"))
            module = importlib.util.module_from_spec(module_spec)
            assert module_spec.loader is not None
            module_spec.loader.exec_module(module)
            sys.modules[name] = module
            loaded[name] = module
        research_spec = importlib.util.spec_from_file_location(
            "frozen_reference_research", source / "research.py")
        research = importlib.util.module_from_spec(research_spec)
        assert research_spec.loader is not None
        research_spec.loader.exec_module(research)
        return research
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


class CompareTests(unittest.TestCase):
    def test_direction_filter_is_symmetric_and_zero_is_allowed(self):
        up = bars(33)
        up[0]["close"], up[-1]["close"] = 100.0, 110.0
        down = bars(33)
        down[0]["close"], down[-1]["close"] = 100.0, 90.0
        self.assertTrue(compare.should_block_btc_mean_reversion(
            "BTCUSD", "mean_reversion", {"side": -1}, up))
        self.assertTrue(compare.should_block_btc_mean_reversion(
            "BTCUSD", "mean_reversion", {"side": 1}, down))
        self.assertFalse(compare.should_block_btc_mean_reversion(
            "BTCUSD", "mean_reversion", {"side": -1}, down))
        self.assertFalse(compare.should_block_btc_mean_reversion(
            "BTCUSD", "mean_reversion", {"side": 1}, up))
        flat = bars(33)
        flat[-1]["close"] = flat[0]["close"]
        self.assertFalse(compare.should_block_btc_mean_reversion(
            "BTCUSD", "mean_reversion", {"side": 1}, flat))
        self.assertFalse(compare.should_block_btc_mean_reversion(
            "ETHUSD", "mean_reversion", {"side": -1}, up))
        self.assertFalse(compare.should_block_btc_mean_reversion(
            "BTCUSD", "trend", {"side": -1}, up))

    def test_gap_validation_rejects_missing_or_misaligned_grid(self):
        btc = bars(4)
        eth = bars(4)
        eth.pop(2)
        with self.assertRaises(compare.DataGapError) as caught:
            compare.validate_timestamps({"BTCUSD": btc, "ETHUSD": eth},
                                        start=0, end=3600, interval=900)
        self.assertFalse(caught.exception.details["identical_timestamps"])
        self.assertEqual(caught.exception.details["missing"]["ETHUSD"], [1800])

    def test_run_writes_halted_result_for_gap_without_running_arms(self):
        with tempfile.TemporaryDirectory() as temp:
            db_path = Path(temp) / "source.sqlite3"
            db = sqlite3.connect(db_path)
            db.execute("CREATE TABLE candles(symbol TEXT, ts INTEGER, payload TEXT, PRIMARY KEY(symbol,ts))")
            btc, eth = bars(4), bars(4)
            eth.pop(2)
            for symbol, candles in (("BTCUSD", btc), ("ETHUSD", eth)):
                db.executemany("INSERT INTO candles VALUES(?,?,?)",
                               [(symbol, bar["ts"], json.dumps(bar)) for bar in candles])
            db.commit()
            db.close()
            result = compare.run_comparison(db_path, Path(temp) / "results",
                                            start=0, end=3600)
            self.assertEqual(result["status"], "halted_data_gap")
            self.assertEqual(result["arms"], {})
            self.assertEqual(json.loads((Path(temp) / "results" / "comparison.json").read_text())["status"],
                             "halted_data_gap")

    def test_baseline_arm_matches_frozen_history_run(self):
        cfg = compare.load_config()
        markets = {"BTCUSD": bars(scale=1.0), "ETHUSD": bars(scale=0.5)}
        engine = compare._load_engine(compare.SOURCE_ROOT / "engine.py")
        actual = compare.simulate_arm(cfg, markets, engine, filtered=False,
                                      start=0, end=96 * 900)
        reference = load_reference_research()
        with tempfile.TemporaryDirectory() as temp:
            db = reference.connect(Path(temp) / "reference.sqlite3")
            reference_markets = {symbol: {"candles": candles}
                                 for symbol, candles in markets.items()}
            _, expected = reference.history_run(db, cfg, reference_markets)
        self.assertEqual(list(actual), list(expected))
        for name in expected:
            self.assertEqual(actual[name]["summary"], expected[name])
            self.assertEqual(actual[name]["filtered_signals"], 0)


if __name__ == "__main__":
    unittest.main()
