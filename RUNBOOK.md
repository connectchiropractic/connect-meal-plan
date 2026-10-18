# Weekly flyer update

Flyers for the Flipp chains (Zehrs, Superstore, No Frills, Food Basics, FreshCo,
Walmart, Metro, Sobeys, Foodland, Your Independent Grocer) run Thursday to
Wednesday. Mercato Fresh runs Friday to Thursday. Costco savings run in two-
and four-week blocks; update Costco only when its block has ended.

## The one-flyer-per-chain rule

The app shows one list of deals per chain in every town. Several chains print
different regional versions of their flyer (this has been true for Zehrs,
Superstore, No Frills and Walmart). Prices for the same item have matched
across versions, but some versions carry extra pages (international foods,
Diwali, Halloween, home goods) that other towns do not get.

**A deal goes in the app only if it is in every regional version of that
chain's flyer at the same price.** That way no town is shown a deal its store
is not running. `tools/flyer_versions.py` does this check.

## Steps

1. Run the check (writes the shared deals to a scratch file, not the repo):

   ```
   python3 tools/flyer_versions.py /path/to/scratch/common.json
   ```

   It prints which towns get which version of each chain's flyer and what was
   left out because it is only in some versions. Read the left-out list; if a
   price for the same item differs between versions, that item is left out
   automatically.

2. Pick the deals for each chain from its shared list, following
   "Picking deals" below, and replace that store's `items`, `validFrom`,
   `validTo` and `source` in `data/stores.json`. Use the `source` the script
   gives. Keep each store's `id`, `name`, `order`, `searchUrl` and `storeNote`
   unless something changed (update `storeNote` if it no longer applies).
   Remove any `checkedTowns` field: the version check replaces it.

3. Mercato Fresh is not on Flipp. Read the flyer pictures at
   https://mercatofresh.com/weekly-flyer/ and pick deals the same way. If the
   new flyer is not posted yet, leave Mercato as is.

4. Set the top-level `updated` date. Check the JSON parses, every tag is in
   `depts`, and open the app to see the deals show up.

5. Commit and push to `main`. GitHub Pages publishes in about a minute.

## Picking deals

Each deal in `data/stores.json`:

- `item`: short, readable, sentence case, with size (e.g. "Pork tenderloin,
  package of 2").
- `price` (number) and `unit`: `lb` if sold by the pound (convert from kg only
  when no per-lb price is given: lb price = kg price / 2.2046), otherwise
  `each`, `bag` or `pack`.
- `tags`: recipe ingredient names spelled exactly as in the `depts` keys of
  `data/stores.json`. Only tags that truly match. `[]` is allowed for a useful
  staple that matches nothing.
- `dept`: one of `Meat & seafood`, `Produce`, `Dairy & eggs`, `Pantry`,
  `Frozen`.
- Optional: `note` (plain English: member-only price, multi-buy, limits),
  `shared: true` for staples bought once a week (eggs, milk, yogurt, broth),
  `minLb` for whole birds, roasts and hams sold by the pound, `packLb` for
  fixed-weight packs of meat or seafood, `perServLb` for bone-in cuts (the app
  otherwise plans 0.4 lb per serving): 0.6 for drumsticks, legs, thighs and
  bone-in chops, 0.75 for wings, 1.0 for shanks and ribs, `verify: true` plus a note when the
  price or unit looks wrong, `ends: "YYYY-MM-DD"` when a deal ends before the
  flyer does. Leave out deals that have already ended by the day you publish.
- Multi-buys ("2 for $5") are entered as the price for one (2.50) with the
  multi-buy in the note.

Pick whole foods for healthy home cooking: fresh meat, poultry, fish and
seafood, eggs, plain dairy, fresh produce, and plain staples (rice, canned
tomatoes and beans, broth, olive oil, plain frozen vegetables and fruit, nuts).
Skip chips, cookies, candy, soda, cereal, frozen dinners, breaded or heavily
processed meats, desserts, non-food, and deals with no real price ("% off"
only). Aim for about 20 to 35 of the best deals per store, meat and produce
first. Never invent an item or a price.
