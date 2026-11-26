# MarketLights

Daily traffic lights for Bitcoin, Ethereum, Gold and Solana. https://marketlights.net

- `live_light.py` downloads fresh data (Coin Metrics, Alternative.me, FRED) into `data/`.
- `backtest2.py` holds the light rules.
- `build.py` writes the page to `dist/index.html` from `template.html`.
- `.github/workflows/daily.yml` runs all of this every day and saves the new page; Cloudflare Pages publishes `dist`.

Information and education only, not financial advice. © Universum Media LLC
