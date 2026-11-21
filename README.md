# The World in One Day — 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/SURAXY1/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/SURAXY1/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A program that draws a newspaper front page summing up the world's news
of Saturday 21 November 2026, and writes it to `/output/entry.png`.

The front page leads with the Russian Kh-101 missile that came down in
south-east Poland — Warsaw calling it a deliberate provocation, NATO jets
scrambled — then the overnight bombardment of Ukraine (400+ drones, 110+
missiles), the Wall Street sell-off (S&P 500 down 3.7% into correction,
Nasdaq down 5.3%, Nvidia down 14%), the first-ever Trump–Xi–Putin
trilateral meeting in Shenzhen, the world court's finding that Myanmar
committed genocide against the Rohingya, and the UK–EU deals on food,
carbon and youth mobility — with the rest of the day running in a ticker
along the foot of the page. Every story on it was first reported on
Saturday 21 November 2026.

## Run it

```sh
python3 main.py
```

The program needs only Python 3.13 and its standard library: a small
rasterizer, a 5x7 bitmap font and a PNG encoder, all in one file. It
reads nothing, reaches no network, and writes the same bytes on
every run.

---

Built for the [make.fun](https://make.fun) news-image-20261121 bounty.
