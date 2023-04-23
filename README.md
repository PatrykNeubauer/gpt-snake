# gpt-snake
Trying out using GPT-3 as an agent to play Snake, 99% of the code is made with it too.

Quite literally a 1-hour project, but a fun one to experiment with prompting and coding capabilities of GPT.
The model does this surprisingly well for how basic the prompt is, most of its bad decisions come down to failing spectacularly at math with coordinates sometimes, which GPT is known for.

Prompt lacks information about not being able to move in the opposite direction or about moving from one edge to another, but it got quite expensive to experiment with since the model is prompted at each move - planning how many tiles to move in that direction could probably help with that a bit.

Example of bad coordinate math:
```moving right will cause the head of the snake to move to (18, 11). The food coordinate is (17, 17), which means the food is 1 block away. Moving right is the best move since it gets the snake the closest to the food.```

Also tried passing the state of the game with ASCII representation like below, but it worked way worse this way.
```
XXX_____
X_______
X_______
O_______
________
________
________
_____F__
```

```python snake.py --api_key <openai_api_key>``` - launch the game with GPT-3 playing, add ```--verbose``` to see the prompts and answers, ```--manual``` to launch a normal game. 