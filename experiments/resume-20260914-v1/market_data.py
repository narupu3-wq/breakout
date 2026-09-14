"""Read-only public market data access for Kraken.

Only the public Time, OHLC, and Ticker endpoints are exposed.  The module
intentionally uses only the Python standard library so it can run in the
project's Python 3.9 environment without credentials or extra dependencies.
"""

from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any, Dict, List, Optional


KRAKEN_PUBLIC_URL = "https://api.kraken.com/0/public/"
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 3
# Kraken's OHLC interval parameter is expressed in minutes.
SUPPORTED_INTERVAL = 15
INTERVAL_SECONDS = SUPPORTED_INTERVAL * 60
SUPPORTED_SYMBOLS = {"BTCUSD": "XBTUSD", "ETHUSD": "ETHUSD"}
SUPPORTED_ENDPOINTS = {"Time", "OHLC", "Ticker"}


class MarketDataError(ValueError):
    """Raised when Kraken data cannot be safely used as market data."""


def _reject_json_constant(value: str) -> None:
    """Reject JSON extensions such as NaN and Infinity."""

    raise ValueError("non-finite JSON number: %s" % value)


def _ensure_finite_tree(value: Any, path: str = "response") -> None:
    """Reject non-finite floats anywhere in a decoded JSON response."""

    if isinstance(value, float) and not math.isfinite(value):
        raise MarketDataError("non-finite number at %s" % path)
    if isinstance(value, Mapping):
        for key, child in value.items():
            _ensure_finite_tree(child, "%s.%s" % (path, key))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _ensure_finite_tree(child, "%s[%d]" % (path, index))


def _validated_result(payload: Any, endpoint: str) -> Dict[str, Any]:
    """Validate and unwrap a Kraken response envelope."""

    if not isinstance(payload, Mapping):
        raise MarketDataError("%s response must be an object" % endpoint)

    _ensure_finite_tree(payload)
    if "error" not in payload or not isinstance(payload["error"], list):
        raise MarketDataError("%s response has malformed error field" % endpoint)
    if payload["error"]:
        raise MarketDataError("Kraken %s error: %s" % (endpoint, payload["error"]))
    if "result" not in payload or not isinstance(payload["result"], Mapping):
        raise MarketDataError("%s response has malformed result field" % endpoint)
    return dict(payload["result"])


def _build_query(params: Optional[Mapping[str, Any]]) -> str:
    if params is None:
        return ""
    if not isinstance(params, Mapping):
        raise MarketDataError("params must be a mapping")

    query: Dict[str, Any] = {}
    for key, value in params.items():
        if not isinstance(key, str) or not key:
            raise MarketDataError("parameter names must be non-empty strings")
        if isinstance(value, (Mapping, list, tuple, set)):
            raise MarketDataError("parameter %s has an unsupported value" % key)
        query[key] = value
    return urllib.parse.urlencode(query)


def fetch_json(endpoint: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Fetch one validated Kraken public endpoint result.

    ``endpoint`` is deliberately restricted to Kraken's public Time, OHLC,
    and Ticker endpoints.  Transport failures are retried at most
    ``MAX_RETRIES`` times; the timeout is kept below the 15 second contract.
    The returned mapping is the API envelope's ``result`` value.
    """

    if endpoint not in SUPPORTED_ENDPOINTS:
        raise MarketDataError("unsupported public endpoint: %r" % (endpoint,))

    query = _build_query(params)
    url = KRAKEN_PUBLIC_URL + endpoint
    if query:
        url += "?" + query

    last_error: Optional[BaseException] = None
    for _attempt in range(MAX_RETRIES):
        try:
            # Passing a URL string to urlopen uses its safe default GET method;
            # no credentials or request body are ever attached.
            response = urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT)
            try:
                status = getattr(response, "status", None)
                if status is not None and int(status) >= 400:
                    raise urllib.error.HTTPError(
                        url, int(status), "HTTP error", hdrs=None, fp=None
                    )
                body = response.read()
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()

            if isinstance(body, bytes):
                try:
                    body = body.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise MarketDataError("%s response is not UTF-8" % endpoint) from exc
            if not isinstance(body, str):
                raise MarketDataError("%s response body is not text" % endpoint)
            try:
                payload = json.loads(body, parse_constant=_reject_json_constant)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise MarketDataError("%s response is not valid JSON" % endpoint) from exc
            return _validated_result(payload, endpoint)
        except MarketDataError:
            raise
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            last_error = exc

    detail = "unknown transport error" if last_error is None else str(last_error)
    raise MarketDataError("Kraken %s request failed after %d attempts: %s" % (
        endpoint,
        MAX_RETRIES,
        detail,
    )) from last_error


def _result_mapping(payload: Any, endpoint: str) -> Dict[str, Any]:
    """Accept either a fetch_json result or a full envelope from a test seam."""

    if isinstance(payload, Mapping) and "error" in payload and "result" in payload:
        return _validated_result(payload, endpoint)
    if not isinstance(payload, Mapping):
        raise MarketDataError("%s result must be an object" % endpoint)
    _ensure_finite_tree(payload)
    return dict(payload)


def _number(value: Any, label: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise MarketDataError("%s must be numeric" % label)
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MarketDataError("%s must be numeric" % label) from exc
    if not math.isfinite(number):
        raise MarketDataError("%s must be finite" % label)
    if positive and number <= 0:
        raise MarketDataError("%s must be positive" % label)
    if nonnegative and number < 0:
        raise MarketDataError("%s must be non-negative" % label)
    return number


def _timestamp(value: Any, label: str) -> int:
    number = _number(value, label)
    if not number.is_integer():
        raise MarketDataError("%s must be an integer timestamp" % label)
    return int(number)


def _pair_value(result: Mapping[str, Any], pair: str, endpoint: str) -> Any:
    """Get a pair value despite Kraken's alternate internal pair key."""

    if pair in result:
        return result[pair]

    candidates = [
        value
        for key, value in result.items()
        if key != "last" and isinstance(value, (Mapping, list))
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise MarketDataError("%s result has no unambiguous %s pair" % (endpoint, pair))


def _parse_time(result: Mapping[str, Any]) -> int:
    if "unixtime" not in result:
        raise MarketDataError("Time result has no unixtime")
    server_time = _timestamp(result["unixtime"], "server_time")
    if server_time <= 0:
        raise MarketDataError("server_time must be positive")
    return server_time


def _parse_candles(
    result: Mapping[str, Any],
    pair: str,
    server_time: int,
    interval_minutes: int,
) -> List[Dict[str, Any]]:
    interval_seconds = interval_minutes * 60
    rows = _pair_value(result, pair, "OHLC")
    if not isinstance(rows, list):
        raise MarketDataError("OHLC pair value must be a list")
    if len(rows) < 2:
        raise MarketDataError("OHLC result has no closed candle")

    # Kraken documents the final OHLC row as the current, uncommitted candle.
    # Drop it before applying the server-time closed-candle check as well.
    closed_rows = []
    for index, row in enumerate(rows[:-1]):
        if not isinstance(row, (list, tuple)) or len(row) < 7:
            raise MarketDataError("OHLC row %d is malformed" % index)
        timestamp = _timestamp(row[0], "OHLC[%d].timestamp" % index)
        if timestamp + interval_seconds > server_time:
            continue
        closed_rows.append((timestamp, row, index))

    if not closed_rows:
        raise MarketDataError("OHLC result has no closed candle")

    candles: List[Dict[str, Any]] = []
    previous_timestamp: Optional[int] = None
    for timestamp, row, index in closed_rows:
        if previous_timestamp is not None:
            if timestamp <= previous_timestamp:
                raise MarketDataError("OHLC timestamps are not increasing")
            if timestamp - previous_timestamp != interval_seconds:
                raise MarketDataError("OHLC candles are not continuous")
        previous_timestamp = timestamp

        opening = _number(row[1], "OHLC[%d].open" % index, positive=True)
        high = _number(row[2], "OHLC[%d].high" % index, positive=True)
        low = _number(row[3], "OHLC[%d].low" % index, positive=True)
        closing = _number(row[4], "OHLC[%d].close" % index, positive=True)
        volume = _number(row[6], "OHLC[%d].volume" % index, nonnegative=True)
        if low > high or not (low <= opening <= high) or not (low <= closing <= high):
            raise MarketDataError("OHLC[%d] violates price relation" % index)
        candles.append({
            "ts": timestamp,
            "open": opening,
            "high": high,
            "low": low,
            "close": closing,
            "volume": volume,
        })

    if server_time - candles[-1]["ts"] > 2 * interval_seconds:
        raise MarketDataError("OHLC data is stale")
    return candles


def _parse_quote(result: Mapping[str, Any], pair: str) -> Dict[str, float]:
    ticker = _pair_value(result, pair, "Ticker")
    if not isinstance(ticker, Mapping) or "a" not in ticker or "b" not in ticker:
        raise MarketDataError("Ticker pair value is malformed")
    ask_values = ticker["a"]
    bid_values = ticker["b"]
    if not isinstance(ask_values, (list, tuple)) or len(ask_values) < 3:
        raise MarketDataError("Ticker ask is malformed")
    if not isinstance(bid_values, (list, tuple)) or len(bid_values) < 3:
        raise MarketDataError("Ticker bid is malformed")
    ask = _number(ask_values[0], "Ticker.ask", positive=True)
    bid = _number(bid_values[0], "Ticker.bid", positive=True)
    ask_size = _number(ask_values[2], "Ticker.ask_size", nonnegative=True)
    bid_size = _number(bid_values[2], "Ticker.bid_size", nonnegative=True)
    if bid > ask:
        raise MarketDataError("Ticker bid exceeds ask")
    return {"bid": bid, "ask": ask, "bid_size": bid_size, "ask_size": ask_size}


def fetch_market(symbol: str, interval: int = SUPPORTED_INTERVAL) -> Dict[str, Any]:
    """Return one validated, read-only market snapshot for ``symbol``.

    Supported user-facing symbols are BTCUSD and ETHUSD.  Kraken's BTC pair
    is requested as XBTUSD.  The quote has no exchange timestamp, so
    ``observed_at`` is the local Unix timestamp captured after the Ticker call.
    """

    if symbol not in SUPPORTED_SYMBOLS:
        raise MarketDataError("unsupported symbol: %r" % (symbol,))
    if isinstance(interval, bool) or not isinstance(interval, int) or interval != SUPPORTED_INTERVAL:
        raise MarketDataError("only a 15 minute interval is supported")

    kraken_pair = SUPPORTED_SYMBOLS[symbol]
    fetch_started_at = time.time()
    if not math.isfinite(fetch_started_at):
        raise MarketDataError("local fetch start time is not finite")

    time_result = _result_mapping(fetch_json("Time", {}), "Time")
    initial_local_at = time.time()
    if not math.isfinite(initial_local_at):
        raise MarketDataError("local observation time is not finite")
    server_time = _parse_time(time_result)
    if abs(float(server_time) - initial_local_at) > 60.0:
        raise MarketDataError("Kraken server time differs from local time")

    ohlc_result = _result_mapping(
        fetch_json("OHLC", {"pair": kraken_pair, "interval": interval}),
        "OHLC",
    )
    ticker_result = _result_mapping(fetch_json("Ticker", {"pair": kraken_pair}), "Ticker")
    observed_at = time.time()
    if not math.isfinite(observed_at):
        raise MarketDataError("local observation time is not finite")
    fetch_duration = observed_at - fetch_started_at
    if fetch_duration > 30.0:
        raise MarketDataError("market data fetch exceeded 30 seconds")

    candles = _parse_candles(ohlc_result, kraken_pair, server_time, interval)
    quote = _parse_quote(ticker_result, kraken_pair)
    return {
        "observed_at": float(observed_at),
        "server_time": server_time,
        "bid": quote["bid"],
        "ask": quote["ask"],
        "bid_size": quote["bid_size"],
        "ask_size": quote["ask_size"],
        "candles": candles,
    }


__all__ = ["MarketDataError", "fetch_json", "fetch_market"]
