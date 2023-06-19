from typing import Optional
import openai
import logging

logger = logging.getLogger(__name__)


def get_completion(
    prompt: str,
    system_message: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.5,
    presence_penalty: float = 0,
) -> str:
    """Get the completion from the OpenAI API.

    Args:
        prompt (str): Prompt to send to the API.
        system_message (str, optional): System message to add before the prompt.
        model (str, optional): OpenAI model. Defaults to "gpt-3.5-turbo".
        temperature (float): Sampling temperature between 0 and 2. Higher values
            like 0.8 will make the output more random, while lower values like
            0.2 will make it more focused and deterministic.
        presence_penalty (float): Presence penalty between -2.0 and 2.0.
            Positive values penalize new tokens based on whether they appear in
            the text so far, increasing the model's likelihood to talk about new
            topics.

    Returns:
        str: Completion from the OpenAI API.
    """
    if not 0 <= temperature <= 2:
        raise ValueError("Temperature must be between 0 and 2.")
    if not -2 <= presence_penalty <= 2:
        raise ValueError("Presence penalty must be between -2 and 2.")
    logger.info(f"Prompt: {prompt}")
    response = _make_openai_request(
        prompt, system_message, model, temperature, presence_penalty
    )
    response_text = response.choices[0].message["content"]
    logger.info(f"Response: {response_text}")
    return response_text


def _make_openai_request(
    prompt: str,
    system_message: Optional[str],
    model: str,
    temperature: float,
    presence_penalty: float,
) -> dict:
    """Make request to OpenAI API."""
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        presence_penalty=presence_penalty,
    )
    logger.debug(f"OpenAI response: {response}")
    return response
