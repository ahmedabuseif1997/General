# NeverEnding.Kicks

A cinematic, scroll-driven product showcase for a running-shoe concept
store — kinetic type hero, pinned horizontal "featured" scroller, an
interactive 20-shoe collection rail with a hover-swapping preview panel,
animated stat counters, and a custom cursor. Pure HTML/CSS/vanilla JS,
no build step, no dependencies.

## Run it

```
cd neverending-kicks
python3 -m http.server 8000
# open http://localhost:8000
```

## Structure

```
index.html      markup + page sections
css/style.css   theme, layout, motion (reveal-on-scroll, marquee, pinning)
js/shoes.js     the 20-shoe / 12-brand product data
js/main.js      interactions: cursor, magnetic buttons, scroll reveals,
                counters, pinned scroller, collection preview, cart/toast
```

All product artwork is an original hand-drawn SVG silhouette tinted per
colorway — no photos or brand logos. Brand names are real running-shoe
makers; specific 2026 model names/specs are an illustrative concept
lineup, not official releases.
