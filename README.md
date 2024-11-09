# TicTacGo_AI
A Python script written by M.L. Thompson, with Claude 3.5 Sonnet, for Tic-Tac-Go (12x12 tic-tac-toe) with AI opponent

**Copyright 2024** [Michael L. Thompson](https://www.linkedin.com/in/mlthomps/)


## Introduction

This Python script was inspired by the article, ["ChatGPT coded a game for me in seconds and I am simply astounded – and coders should be very worried"](https://www.techradar.com/computing/artificial-intelligence/chatgpt-coded-a-game-for-me-in-seconds-and-i-am-simply-astounded-and-coders-should-be-very-worried?utm_source=flipboard&utm_content=topic/artificialintelligence), by [Lance Ulanoff](https://www.techradar.com/author/lance-ulanoff) published Nov. 7, 2024 on [TechRadar](https://www.techradar.com/).

## How It Was Done

I entered Ulanoff's prompt into [Anthropic's Claude 3.5 Sonnet](https://claude.ai/chat/). Here's the prompt:

>I want to create a variant on the game tic-tac-toe, but I need it to be more complex. So, the grid should be 12-by-12. It should still use "x" and "o". Rules include that any player can block another by placing their "x" or "o" in any space around the grid, as long as it is in one of the spaces right next to the other player. They can choose to place their "x" or "o" in any space, as well, to block future moves. The goal is to be the first one to have at least six "x" or "o" in any row, column, or diagonal before the other player. Remember, one player is "x" and the other is "o". Please program this in Python. Let's call this game: Tic-Tac-Go.
>

I followed that with this prompt of my own:

>Now, enhance the game so that I can play against a computer component.
>

Then, eventually, this prompt:

>The current version is taking a very long time to think on the AI's turn. Is it possible for it to do some of that thinking in the background when it is the player's turn so that when it then becomes the AI's turn it can respond more quickly?

## Results

After a couple more rounds of back and forth, including getting it to add "." in each available valid move position on the displayed board, I ended up with the following script:

(*In total, this is the 9th version of the code it generated for me. It includes my minor manual code revisions (e.g., ensuring good board spacing & alignment).*)

* [Tic-Tac-Go-threaded3.py](tic-tac-go-threaded3.py)

**NOTE:** You'll have to take it upon yourself to install the necessary packages so that the script's following `import` statements will work:
  
```python
import numpy as np
from typing import Tuple, Optional, List
import threading
import queue
import copy
import time
from dataclasses import dataclass
```

## Conclusions

Of course, playing against the AI opponent is about as productive as playing traditional 3x3 tic-tac-toe.  But, I think it's remarkable that Claude 3.5 Sonnet coded up an [alpha-beta-pruning search strategy](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning#:~:text=Alpha%E2%80%93beta%20pruning%20is%20a,possibly%20influence%20the%20final%20decision.) -- chosen of its own volition. Then when prompted to, it add continuous background thinking.  

Play it. Have fun! (*To be sure, the AI opponent **will** beat you if you aren't diligent!*)

* For another intriguing Generative AI project, see my Github repository ["Proposition-Analysis"](https://github.com/apollostream/Proposition-Analysis).
