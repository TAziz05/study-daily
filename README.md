# Study Daily

A personal daily study quiz. Each day it gives one question per class: Philosophy, Data Mining, Data Visualization and Japanese.

- **Today**: four questions, one per class. They stay the same all day on a given device.
- **Review**: missed questions come back 1, 3, 7 and 16 days later.
- **Practice**: unlimited questions for any class. Pick a lesson (or reading), then the entire lesson or a single topic. Japanese lessons split into grammar, kanji and vocabulary, plus a Katakana section.
- **Sync devices**: progress lives in each browser. Copy the sync code to move it to another device.

## Adding questions

Questions live in `data/src/*.json`. The file prefix sets the class: `phil_`, `dm_`, `dv_` or `jp_`. Each question looks like:

```json
{"t": "Topic", "s": "Source (lecture/reading + section)", "q": "Question", "a": "Correct answer", "w": ["Wrong 1", "Wrong 2", "Wrong 3"], "e": "Explanation"}
```

Japanese kanji questions are generated from `build/kanji_data.txt`, vocabulary from `build/vocab_genki1.txt` and `build/vocab_genki2.txt` (`lesson|word|reading|meaning`), and katakana practice from `build/katakana.py`. On the daily quiz, Japanese rotates through grammar, kanji, vocabulary and katakana. After editing, rebuild `questions.js` with:

```
python3 build/build.py
```

## Credits

Coded with [Claude](https://claude.ai) (Opus 5.5) by Anthropic. Questions were written by Claude from my own lecture notes and readings, plus the Genki I/II and Quartet I textbooks for Japanese.
