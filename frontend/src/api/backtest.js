import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export const api = {
  listStrategies: () => axios.get(`${BASE_URL}/strategies`).then(r => r.data),

  runBacktest: ({ strategyId, universe = 'DOW', start = '2023-01-01', end = '2024-01-01', initialCapital = 100000 }) =>
    axios.get(`${BASE_URL}/run`, {
      params: { strategy_id: strategyId, universe, start, end, initial_capital: initialCapital }
    }).then(r => r.data),

  getOHLC: (symbol, start, end) =>
    axios.get(`${BASE_URL}/data/ohlcv`, {
      params: { symbol, start, end }
    }).then(r => r.data),
};
