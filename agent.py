from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import openai
import textwrap


def set_openai_key(api_key):
    """Sets OpenAI key."""
    openai.api_key = api_key


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)


actions = ["LEFT", "RIGHT", "UP", "DOWN"]


class Agent:
    def __init__(self, api_key, verbose):
        self.base_prompt = textwrap.dedent(
            """\
            You're playing a classic snake game. 
            The objective of Snake is to control the movement of a snake on a game board, and eat food to grow longer. 
            The game ends when the snake collides with its own body.
            You will be given a list of coordinates of the snakes body, starting from the head. 
            You'll also have the coordinates of the food and the size of the map. 
            Your task is to write "LEFT", "RIGHT", "UP" or "DOWN" to control the snake. 
            You should aim to collect the food item with the head of the snake, while avoiding going into your own body. 
            Collecting the food item will increase your score and length, which you should maximize. 
            You should try to collect the food as fast as possible, while avoiding going into your body. 
            For each move, explain why it might be a good or a bad move, then pick the best option.
            Coordinates are in (x, y) format.
            Moving up will cause the head of the snake to move to (x, y-1).
            Moving down will cause the head of the snake to move to (x, y+1)
            Moving left will cause the head of the snake to move to (x-1, y).
            Moving right will cause the head of the snake to move to (x+1, y).
            If you try to move into a coordinate taken up by the snakes body, you will lose the game.
            If you move the head of the snake into the coordinate of the food item, you will get a point.
            """
        )
        self.verbose = verbose
        set_openai_key(api_key)

    @staticmethod
    def observation_to_text(observation):
        observation_prompt = "Coordinates of the snake: [("
        for x, y in observation["snake_positions"]:
            observation_prompt += f"{x}, {y}), "
        observation_prompt = observation_prompt[:-2] + "].\n"
        observation_prompt += f"Coordinates of food: {observation['food_position']}.\n"
        observation_prompt += f"Width of the map: {observation['grid_width']}. Height of the map: {observation['grid_height']}."
        return observation_prompt

    def predict(self, observation):
        prompt = self.base_prompt  # Prefix
        prompt += "\n" + self.observation_to_text(observation)  # Add observation

        # Explain the reasoning behind the move
        prompt += "\nLet's break down each possible move:"
        prompt += completion_with_backoff(
            model="text-davinci-003", max_tokens=512, prompt=prompt
        )["choices"][0]["text"]

        # Final choice
        prompt += (
            "\nTherefore out of " + ", ".join(actions) + ", the best option is to go"
        )

        response = completion_with_backoff(model="text-davinci-003", prompt=prompt)[
            "choices"
        ][0]["text"]

        if self.verbose:
            print(50 * "=")
            print(prompt)
            print(response)
        return response
