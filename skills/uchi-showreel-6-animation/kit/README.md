# Набор Remotion для роликов Учи.ру

`python3 skills/uchi-showreel-6-animation/scripts/scaffold.py showreel/<slug>` копирует набор в `showreel/<slug>/src/`, шрифты, логотип и озвучку в `public/`, и готовит `timing.json` и `words.json` (из `build_audio.py`).

- `brand.tsx`: палитра `C`, шрифты `HEAD`/`BODY`, загрузчик `Fonts`, облака бренда `Cloud` (из шаблона 02).
- `kit.tsx`: время (`B`, `TOTAL`, `wf`, `prog`, `eo`, `eio`), приёмы текста (`blurIn`), движение (`drift`), `Pop`, `Img`, `Svg`, `Layer`, переходы `Wipe` (шторка-облако) и `WordT` (слово-переход).
- `fx.tsx`: эффекты типографики и анимации (`Letters`, `Shiver`, `Snow`, `Pulse`, `revealX`).
- `Main.tsx`: каркас монтажа. Сцены правь, помощников и переходы не пиши заново.
- Границы сцен и слова берутся только из `timing.json` и `words.json`. При смене голоса запусти `build_audio.py` заново, код не трогай.
- Другие переходы (push, круговая шторка, блюр-морф) смотри как образцы в готовых роликах и в `references/transitions.md`.
