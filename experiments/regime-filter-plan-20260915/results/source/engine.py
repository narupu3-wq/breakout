"""Deterministic research simulator. No order API, credentials, or live mode."""
import math
import statistics


def day_key(ts, offset=1800):
    return int((ts - offset) // 86400)


def signal(history, kind, cfg):
    """Only completed candles supplied by caller. Returned signal is immutable intent."""
    n = cfg['lookback']
    if len(history) < n + 1:
        return None
    past, current = history[-n-1:-1], history[-1]
    closes = [b['close'] for b in past]
    ranges = [max(b['high'] - b['low'], abs(b['high'] - a['close']),
                  abs(b['low'] - a['close'])) for a, b in zip(history[-cfg['atr_period']-1:], history[-cfg['atr_period']:])]
    atr = statistics.mean(ranges)
    if not math.isfinite(atr) or atr <= 0 or current['volume'] <= 0:
        return None
    side = 0
    if kind == 'trend':
        if current['volume'] >= statistics.mean(b['volume'] for b in past):
            side = 1 if current['close'] > max(b['high'] for b in past) else (-1 if current['close'] < min(b['low'] for b in past) else 0)
    elif kind == 'mean_reversion':
        sd = statistics.pstdev(closes)
        z = (current['close'] - statistics.mean(closes)) / sd if sd else 0
        side = -1 if z >= cfg['mean_reversion_z'] else (1 if z <= -cfg['mean_reversion_z'] else 0)
    else:
        raise ValueError('Unknown strategy')
    return {'side': side, 'distance': atr * cfg['stop_atr'], 'signal_ts': current['ts']} if side else None


class Account:
    """One position per candidate across both symbols (no unbounded aggregate risk)."""
    def __init__(self, cfg, risk, state=None, cost_multiplier=1.0):
        self.cfg, self.risk, self.mult = cfg, risk, cost_multiplier
        initial = cfg['account']['initial_balance']
        self.s = state or {'balance': initial, 'day': None, 'day_balance': initial,
                           'position': None, 'halt': None, 'daily_halt': False,
                           'peak': initial, 'max_drawdown': 0.0, 'closed': 0,
                           'wins': 0, 'gross_wins': 0.0, 'gross_losses': 0.0}
        self.events = []

    def event(self, kind, ts, **kw):
        self.events.append({'kind': kind, 'ts': ts, **kw})

    def equity(self, price=None):
        p = self.s['position']
        return self.s['balance'] + (p['qty'] * p['side'] * (price - p['entry']) if p and price is not None else 0)

    def reset_day(self, ts):
        key = day_key(ts, self.cfg['account']['reset_utc_seconds'])
        if key != self.s['day']:
            self.s.update(day=key, day_balance=self.s['balance'], daily_halt=False)
            self.event('daily_reset', ts, baseline=self.s['balance'])

    def floors(self):
        a = self.cfg['account']
        official = max(a['initial_balance'] - a['static_loss'], self.s['day_balance'] * (1-a['daily_loss_fraction']))
        internal = max(a['initial_balance'] - self.risk['total_stop'], self.s['day_balance'] - self.risk['daily_stop'])
        return official, internal

    def check(self, ts, equity):
        self.s['peak'] = max(self.s['peak'], equity)
        self.s['max_drawdown'] = max(self.s['max_drawdown'], self.s['peak'] - equity)
        official, internal = self.floors()
        if equity <= official:
            self.s['halt'] = 'official_breach'
            return 'official_breach'
        if equity <= internal:
            if equity <= self.cfg['account']['initial_balance'] - self.risk['total_stop']:
                self.s['halt'] = 'total_stop'
                return 'total_stop'
            self.s['daily_halt'] = True
            return 'daily_stop'
        return None

    def carry(self, ts):
        p = self.s['position']
        if p:
            # Continuous conservative research approximation; actual platform timing unresolved.
            cost = p['qty'] * p['entry'] * self.cfg['costs']['swap_per_day'] * self.mult * max(0, ts-p['carry_ts']) / 86400
            self.s['balance'] -= cost
            p['carry'] += cost
            p['carry_ts'] = ts

    def open(self, ts, symbol, sig, bid, ask, available=None):
        self.reset_day(ts)
        if self.s['position'] or self.s['halt'] or self.s['daily_halt']:
            return False
        if self.check(ts, self.s['balance']):
            return False
        c = self.cfg['costs']
        side, dist = sig['side'], sig['distance']
        slip = c['slippage_bps'] * self.mult / 10000
        entry = (ask if side == 1 else bid) * (1 + side * slip)
        stop = entry - side * dist
        if stop <= 0:
            return False
        fee = c['fee_per_side'] * self.mult
        exit_worst = stop * (1 - side * slip)
        per_unit = abs(entry-exit_worst) + fee * (entry+abs(exit_worst))
        per_unit += entry * c['swap_per_day'] * self.mult * self.cfg['strategy']['max_hold_bars'] * self.cfg['interval_minutes'] / 1440
        official, internal = self.floors()
        budget = min(self.risk['trade_risk'], max(0, self.s['balance'] - internal) * 0.5,
                     max(0, self.s['balance'] - official) * 0.25)
        if budget < 0.25:
            if self.cfg['account']['initial_balance'] - self.risk['total_stop'] >= self.s['day_balance'] - self.risk['daily_stop']:
                self.s['halt'] = 'risk_budget_exhausted'
            else:
                self.s['daily_halt'] = True
            self.event('risk_budget_exhausted',ts,remaining_budget=budget)
            return False
        qty = min(budget / per_unit, self.s['balance'] / entry) if per_unit else 0
        if qty <= 0:
            return False
        p = {'symbol': symbol, 'side': side, 'qty': qty, 'entry': entry,
             'stop': stop, 'take': entry + side * dist * self.cfg['strategy']['reward_risk'],
             'opened': ts, 'carry_ts': ts, 'carry': 0.0, 'entry_fee': qty * entry * fee}
        self.event('intent', ts, symbol=symbol, signal=sig, bid=bid, ask=ask,
                   qty=qty, stop=p['stop'], take=p['take'], planned_risk=budget,
                   order_type='simulated_market_fok', fill_model='quote_plus_slippage', available=available)
        if available is not None and qty > available:
            self.event('unfilled',ts,symbol=symbol,qty=qty,available=available,reason='insufficient_observed_liquidity')
            return False
        self.s['balance'] -= p['entry_fee']
        self.s['position'] = p
        self.event('paper_fill', ts, **p)
        return True

    def close(self, ts, price, reason):
        p = self.s['position']
        if not p:
            return
        c = self.cfg['costs']
        price *= 1 - p['side'] * c['slippage_bps'] * self.mult / 10000
        fee = p['qty'] * price * c['fee_per_side'] * self.mult
        pnl = p['qty'] * p['side'] * (price-p['entry']) - fee
        self.s['balance'] += pnl
        net = pnl-p['entry_fee']-p['carry']
        self.s['closed'] += 1
        self.s['wins'] += int(net > 0)
        self.s['gross_wins'] += max(net, 0)
        self.s['gross_losses'] += max(-net, 0)
        self.s['position'] = None
        self.event('close', ts, symbol=p['symbol'], price=price, net_pnl=net,
                   reason=reason, balance=self.s['balance'])
        self.check(ts, self.s['balance'])
        if not self.s['halt'] and self.s['balance'] >= self.cfg['account']['initial_balance'] + self.cfg['account']['target_profit']:
            self.s['halt'] = 'simulated_target_reached'
            self.event('simulated_target_reached', ts)

    def quote(self, ts, bid, ask):
        self.reset_day(ts)
        self.carry(ts)
        p = self.s['position']
        if not p:
            self.check(ts, self.s['balance'])
            return
        price = bid if p['side'] == 1 else ask
        reason = self.check(ts, self.equity(price))
        if not reason and (price-p['stop']) * p['side'] <= 0:
            reason = 'stop'
        if not reason and (price-p['take']) * p['side'] >= 0:
            reason = 'take'
        if not reason and ts-p['opened'] >= self.cfg['strategy']['max_hold_bars'] * self.cfg['interval_minutes'] * 60:
            reason = 'time_exit'
        if reason:
            self.close(ts, price, reason)

    def bar(self, b):
        """Conservative OHLC: open gap first, adverse extreme before favorable extreme."""
        ts = b['ts']
        half = self.cfg['costs']['backtest_spread_bps'] * self.mult / 20000
        self.quote(ts, b['open']*(1-half), b['open']*(1+half))
        p = self.s['position']
        if not p:
            return
        end_ts = ts + self.cfg['interval_minutes']*60-1
        self.carry(end_ts)
        side = p['side']
        adverse = b['low']*(1-half) if side == 1 else b['high']*(1+half)
        favorable = b['high']*(1-half) if side == 1 else b['low']*(1+half)
        # Track possible intrabar equity breaches even if the stop would precede the low/high.
        # Stop and internal floor are handled at their first crossed price, not at bar close.
        official, internal = self.floors()
        floor_price = p['entry'] + side * (internal-self.s['balance'])/p['qty']
        exit_level = max(p['stop'], floor_price) if side == 1 else min(p['stop'], floor_price)
        if (adverse-exit_level)*side <= 0:
            self.close(end_ts, exit_level, 'stop_or_risk_floor')
        elif (favorable-p['take'])*side >= 0:
            self.check(end_ts, self.equity(adverse))
            self.close(end_ts, p['take'], 'take')
        else:
            self.check(end_ts, self.equity(adverse))
            self.check(end_ts, self.equity(favorable))
            self.quote(ts + self.cfg['interval_minutes']*60-1,
                       b['close']*(1-half), b['close']*(1+half))

    def summary(self):
        s = self.s
        return {'balance': round(s['balance'], 6), 'closed_trades': s['closed'],
                'profit_factor': s['gross_wins']/s['gross_losses'] if s['gross_losses'] else None,
                'max_drawdown': s['max_drawdown'], 'halt': s['halt'],
                'open_position': s['position'], 'net_realized': s['balance']-self.cfg['account']['initial_balance']}
