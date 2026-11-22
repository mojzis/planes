# Arrow: folding video (scenario)

A short video that shows how to fold the Arrow, step by step, with a friendly voice
telling each step. For starters it shows only the folding: no mascot, no extra
pictures. Every picture comes from the fold model (`planes/models.py`, `arrow()`), so
the video always matches the steps page. Made with cecil; the format follows its
scenario layout (scenes, lines, directions). Decision:
[0003-folding-videos.md](../decisions/0003-folding-videos.md).

Narration is written in Czech and English. **English is voiced first** (the user's
choice, 2026-11-22): cecil can voice it today. The Czech text waits until cecil has a
Czech voice (see "What cecil needs" below).

## The whole video

- **Length:** about 110 s; `limit: 150`. Slower than a story: a child folds along, so
  every fold is shown whole and held before the next step.
- **Frame:** horizontal 16:9, 1920 x 1080, 24 fps.
- **Background:** `paper:cream` in every shot, nothing else. The sheet is white on top,
  pale grey underneath, as on the site.
- **Cast:** one voice, heard and never seen: `Narrator` (`Vypravěčka` in the Czech lines).
- **Voice:** designed once, then cloned for every line (cecil decision 0007).
  Description: *"A friendly girl of about ten, bright and cheerful, speaking clearly
  and a little slowly, like showing a friend how to fold something. A natural girl's
  pitch."* Check the designed sample by pitch (about 280 to 320 Hz) and by what
  Whisper hears before using it.
- **Text layer:** a small step label top left, `1/9` to `9/9`, from the step's first
  line to its end. Nothing else on screen.
- **Music:** a quiet, light bed under the whole video; `tada` when the plane is done.
- **Each fold, the same rhythm:**
  1. The fold line appears on the paper as on the steps page (valley: dashed,
     mountain: dash-dot) on the line's first word, and stays 1 s.
  2. The paper folds along it in about 2 s, eased in and out, with a soft paper
     sound. The fold happens on the word that names it.
  3. The folded paper holds still for at least 1.5 s after the line ends (`tail`).
- **Skipped on purpose:** the optional beak (step 7 on the site). It is the hardest
  step and not needed to fly. A later video can add it.

## Views

The fold model draws a half-done fold at any angle (`iso.step_view(step, angle)`),
so each fold is a run of frames from 0° to 180°. Two fixed views, one cut between
them; within a view the camera and the scale do not change, so the paper never jumps.

- **Table view** (scenes 1 to 6): the sheet lies flat, seen from the front and above
  (pitch about 55°), portrait, its top edge away from us. The whole A4 sheet fills
  about 70 % of the frame height.
- **Plane view** (scenes 7 to 11): the folded body seen from the side and a little
  above (yaw 120°, pitch 35°, as on the site's 3D pictures), nose to the left.

## Scenes

Lines follow cecil's script format: one breath per line, numbers as words, directions
in brackets. Each line gives the Czech text, then the English one.

### Scene 1: What we fold (≈9 s)

**Background:** cream paper. **On stage:** nothing, then the A4 sheet in the table view,
centre.
**Action:**
1. The sheet appears on the first word (`show`, a soft `pop`).

**Lines:**
- [1] **Vypravěčka:** Ahoj! Dneska si složíme Šipku. Je to letadlo, které doletí hodně daleko.
  - en: Hi! Today we're folding the Arrow. It's a paper plane that flies really far.
- [1] **Vypravěčka:** Stačí ti jeden list papíru á čtyři. Nůžky nepotřebuješ. (pic: the empty sheet)
  - en: All you need is one sheet of A four paper. No scissors.

**Sound:** music bed starts, `pop` with the sheet. **Text layer:** none.

### Scene 2: Step 1, the middle crease (≈11 s)

**On stage:** the sheet, table view.
**Action:**
1. A dashed line from top to bottom down the middle.
2. The right half folds over onto the left, then opens again (the model's unfold step:
   0° to 180° and back).
3. The crease stays as a thin line.

**Lines:**
- [2] **Vypravěčka:** Přelož papír napůl podél, hranu na hranu. Přehyb pořádně přejeď a zase ho rozlož.
  - en: Fold the paper in half the long way, edge to edge. Crease it well and open it again.
- [2] **Vypravěčka:** Každý přehyb přejeď nehtem. Ostré přehyby letí dál. (pic: no hand; the crease line turns darker)
  - en: Run your fingernail along every fold. Sharp folds fly further.

**Text layer:** `1/9`.

### Scene 3: Step 2, corners to the middle (≈9 s)

**Action:**
1. Two dashed lines from the top middle out to the sides.
2. Both top corners fold down at the same time and lie on the middle crease.

**Lines:**
- [3] **Vypravěčka:** Teď přehni oba horní rohy dolů, aby jejich hrany ležely na prostředním přehybu.
  - en: Now fold both top corners down so their edges lie on the middle crease.

**Text layer:** `2/9`.

### Scene 4: Step 3, the top triangle down (≈8 s)

**Action:**
1. A dashed line across the sheet where the corners ended.
2. The whole top triangle folds down over the sheet.

**Lines:**
- [4] **Vypravěčka:** Celý horní trojúhelník přelož dolů. Přehyb je přesně tam, kde skončily rohy.
  - en: Fold the whole top triangle down. The fold goes right where the corners ended.

**Text layer:** `3/9`.

### Scene 5: Step 4, corners to the middle again (≈8 s)

**Action:**
1. Two dashed lines from the middle of the top edge out to the sides.
2. The two new top corners fold to the middle and meet above the point.

**Lines:**
- [5] **Vypravěčka:** Nové horní rohy zase přelož ke středu. Potkají se nad špičkou.
  - en: Fold the two new top corners to the middle again. They meet above the point.

**Text layer:** `4/9`.

### Scene 6: Step 5, the heavy nose (≈12 s)

**Action:**
1. Two long dashed lines from the top point down to the bottom edge.
2. Both slanted edges fold to the middle line.
3. Hold: the nose is now many layers thick.

**Lines:**
- [6] **Vypravěčka:** A ještě jednou: šikmé hrany přelož ke střední čáře.
  - en: And once more: fold the slanted edges to the middle line.
- [6] **Vypravěčka:** Teď je špička tlustá a těžká. To je ten trik, proč Šipka letí tak daleko. (pic: the thick nose, held still)
  - en: Now the nose is thick and heavy. That's the trick that makes the Arrow fly so far.

**Text layer:** `5/9`.

### Scene 7: Step 6, fold in half (≈9 s)

**On stage:** table view to start; the cut to the plane view comes at the end of the
fold.
**Action:**
1. A dash-dot line down the middle (a mountain fold).
2. The left half folds behind the right one, so all the folds stay outside.
3. Cut to the plane view: the body lies on its side, nose left.

**Lines:**
- [7] **Vypravěčka:** Přelož ji napůl podél středu, dozadu, aby všechny přehyby zůstaly venku.
  - en: Fold it in half along the middle, backwards, so all the folds stay on the outside.

**Text layer:** `6/9`.

### Scene 8: Step 7, the wings (≈12 s)

**On stage:** the body, plane view.
**Action:**
1. A dashed line along the body, 1.5 cm above the bottom fold.
2. The near wing folds down towards us; then the far wing folds down behind.

**Lines:**
- [8] **Vypravěčka:** Přehni křídla dolů, jeden a půl centimetru od spodního přehybu. Jedno dopředu, druhé dozadu.
  - en: Fold the wings down, one and a half centimetres from the bottom fold. One to the front, one behind.
- [8] **Vypravěčka:** Přehyb drž rovnoběžně se spodní hranou.
  - en: Keep the fold parallel to the bottom edge.

**Text layer:** `7/9`.

### Scene 9: Step 8, open the wings (≈8 s)

**Action:**
1. Both wings swing up from hanging down to flat, in a very shallow V (the model's
   `dihedral` from about -89° to 6°).

**Lines:**
- [9] **Vypravěčka:** Roztáhni křídla, ať jsou rovná, nebo jen do malého V. Tělo pod nimi drž stisknuté.
  - en: Open the wings so they're flat, or in a very shallow V. Pinch the body together underneath.

**Text layer:** `8/9`.

### Scene 10: Step 9, stabilizers (≈10 s)

**Action:**
1. The outer centimetre at the back of each wing bends straight up (the model's
   `winglet_angle` from 0° to 80°), both at once.

**Lines:**
- [10] **Vypravěčka:** A teď stabilizátory: vzadu na kraji každého křídla ohni jeden centimetr nahoru.
  - en: Now the stabilizers: at the back of each wing, bend the outer centimetre straight up.
- [10] **Vypravěčka:** Díky nim letí Šipka rovně.
  - en: They keep the Arrow flying straight.

**Text layer:** `9/9`.

### Scene 11: Done (≈12 s)

**On stage:** the finished plane, plane view, centre.
**Action:**
1. On "Hotovo" the plane turns slowly once round (yaw 0° to 360° in about 5 s), with
   `tada`.
2. It ends nose left, still, until the end.

**Lines:**
- [11] **Vypravěčka:** Hotovo! (sfx: tada)
  - en: Done!
- [11] **Vypravěčka:** Hoď ji silně a rovně, trochu nahoru. Nejlíp venku, nebo na dlouhé chodbě.
  - en: Throw it hard and straight, a little upwards. Outdoors is best, or down a long hallway.
- [11] **Vypravěčka:** Jak daleko doletí ta tvoje?
  - en: How far does yours fly?

**Sound:** `tada` on "Hotovo", the music ends with the last line. **Text layer:** none.

## Pictures: frames from the fold model

What the planes repo has to produce for cecil (not built yet):

- One run of transparent PNG frames per scene action, at 12 drawings a second (cecil
  films are animated on twos), named `<scene>-<nnn>.png`.
- Folds: `iso.step_view(step, angle)` with the angle eased in and out from 0° to 180°.
  The unfold of step 1 goes 0° to 180° and back. The fold line is drawn on the paper
  for the frames before the fold starts.
- Wings opening: `iso.plane3d(..., dihedral=d)` with `d` from -89° to 6°.
  Stabilizers: `winglet_angle` from 0° to 80°. The turn: the camera's yaw, 0° to 360°.
- **Fixed camera and fixed scale per view.** `iso.svg` fits each picture to its box,
  so frames drawn one by one would grow and shrink. The frame exporter needs one scale
  and one origin for the whole view (from the bounding box of all its frames).
- Checked on 2026-11-22: `step_view` draws steps 1 to 6 cleanly at 0°, 45°, 90°, 135°
  and 178°, with nothing torn or missing.

## What cecil needs

cecil cannot make this film yet. Two things are missing (filed as cecil feature ideas):

1. **Pictures from a program, played as frames.** cecil's pictures are rolled by an
   image model, or brought in one at a time as photos (with a credit, no poses). This
   video needs a few hundred frames from the fold model, played at 12 a second on one
   actor.
2. **A Czech voice.** cecil's voice model (Qwen3-TTS) speaks ten languages, Czech not
   among them. The English version, which goes first, can be voiced today.

Also small: a paper-crease sound in cecil's `sfx` list (a soft `whoosh` until then),
and a per-language `say` (so "A4" can be shown and "á čtyři" spoken).
