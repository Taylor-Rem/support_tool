# support_tool

A desktop app I wrote to automate my own job on the support team at Kingsley Management, a
property-management company. Support staff fixed residents' ledgers, credits and tickets by hand in the
company's web portal; this tool does those steps for them by driving the browser.

Built August 2023 – November 2024, hand-written in Python. Not maintained: the work it automated was later
rebuilt as features of the company's own platform, which I wrote as a developer there, and this tool was
the functional spec for that rewrite.

## What it does

- **Ledger and transaction fixes**: opens a resident's ledger, finds the charges, credits or allocations
  to correct, and applies the change through the portal's own forms.
- **Credits**: adds the credit or concession a ticket asks for, with the right comment.
- **Support tickets**: walks the open tickets on the support desk, works out which operation each needs,
  runs it and records the result.
- **One-off batches**: runs an operation over a list of residents from a CSV.

## How it is built

- `front_end/` — the PyQt5 window: pick an operation, start it, watch progress. Work runs on a thread so
  the window stays responsive.
- `general_tools/browser.py` — a Selenium wrapper with the waits, retries and alert handling the portal
  needs.
- `resmap/` — one module per area of the portal: navigation, ledger, credit, transaction.
- `manage_portal/` — the support desk and its tickets.
- `main_tools/` — the operations and the loop that drives them.

## Running it

Python 3 with PyQt5, Selenium and pandas. Copy `config.example.py` to `config.py` and fill in the portal
addresses, the login and a data folder; `config.py` is gitignored. Then `python main.py`. It only works
against that company's portal.
