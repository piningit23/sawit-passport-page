# sawit-passport-page

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/piningit23/sawit-passport-page/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/piningit23/sawit-passport-page/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A make.fun competition entry for
[the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318):
"The Passport Page of a Country That Isn't There".

One image: an invented passport spread for the **Republic of Zaloria**
(capital Port Meridian, currency the taler).

## What the image shows

- Data page: holder Elena Mara Voss, born 12 Jun 1994 in Port Meridian;
  passport ZL 0048217, issued 14 Mar 2023, expiry 14 Mar 2033; portrait,
  signature, and a two-line machine-readable zone (MRZ) with check digits.
- Visas page: a Kestrel Republic visa (single entry, 30 days, fee 40
  talers paid) plus six entry/exit stamps from three neighbouring
  countries, all in chronological order after the issue date:
  Kestrel Republic (Jun 2023), United Provinces of Tarn (Sep 2024),
  Free State of Velmar (Feb–Mar 2026).

## How it is built

- `main.py` (Python 3.13, standard library only, no network) draws the
  whole spread with its own bitmap font and its own PNG encoder and
  writes `/output/entry.png` (1024×1024, deterministic — two runs are
  byte-identical).
