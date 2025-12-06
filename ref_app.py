import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import List

import gradio as gr
from google import genai
from google.genai import types


GEMINI_3_MODEL_ID = "gemini-3-pro-image-preview"
GEMINI_25_MODEL_ID = "gemini-2.5-flash-image"
DEFAULT_MODEL_ID = GEMINI_3_MODEL_ID
MODEL_CHOICES = [GEMINI_3_MODEL_ID, GEMINI_25_MODEL_ID]
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "1K"
MAX_IMAGES = 4
EXAMPLE_PROMPTS = [
    "Create a textural, earthy fashion moodboard for a women's sustainable luxury dress collection, Lagos Spring/Summer 2026. The aesthetic is 'Modern Heritage meets Zero-Waste'.",
    "Create a layered fashion moodboard collage for a contemporary Indian bridal collection for the 2025-2026 season. The aesthetic theme is 'The Modern Minimalist Bride: Ethereal Lightness'.",
    "A moodboard for a Rococo era ballgown with accurate embroidery patterns.",
]


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise gr.Error("Set the GOOGLE_API_KEY environment variable with your Gemini API key.")
    return genai.Client(api_key=api_key)


def _generate_single_image(prompt: str, model_id: str, thinking_level: str = "high"):
    client = _get_client()
    image_config = {"aspect_ratio": DEFAULT_ASPECT_RATIO}
    config_kwargs = {}

    if model_id == GEMINI_3_MODEL_ID:
        image_config["image_size"] = DEFAULT_IMAGE_SIZE

    image_config = types.ImageConfig(**image_config)
    config_kwargs["image_config"] = image_config

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    for part in response.parts:
        if part.inline_data:
            return part.as_image()
    return None


def generate_images(prompt: str, num_images: int, model_id: str) -> List:
    # TODO: we could try to detect if `prompt` contains date/place info and decide to
    # include search grounding in the process. I think this detection can be implemented
    # using `nltk`.
    prompt = prompt.strip()
    if not prompt:
        raise gr.Error("Prompt cannot be empty.")

    images = []
    max_workers = min(num_images, MAX_IMAGES)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_generate_single_image, prompt, model_id=model_id) for _ in range(num_images)]
        for future in as_completed(futures):
            image = future.result()
            if image:
                images.append(image._pil_image)

    if not images:
        raise gr.Error("The model did not return any image data. Please try again.")

    return images


def _select_example_prompt(example: str) -> str:
    return example or ""


with gr.Blocks(title="Fashion Moodboard") as demo:
    gr.Markdown(
        """
        # Fashion Moodboard with Gemini

        Describe the image you want to see and pick how many variations to generate.
        """
    )

    model_selector = gr.Radio(
        choices=MODEL_CHOICES,
        value=DEFAULT_MODEL_ID,
        label="Model ID",
    )
    prompt_input = gr.Textbox(
        label="Prompt",
        placeholder="e.g. Generate an infographic of the current weather in Tokyo.",
        lines=4,
    )
    example_selector = gr.Radio(
        choices=EXAMPLE_PROMPTS,
        value=None,
        label="Example prompts (select to populate the prompt field)",
    )
    images_slider = gr.Slider(
        minimum=1,
        maximum=MAX_IMAGES,
        value=2,
        step=1,
        label="Number of Images",
    )
    generate_button = gr.Button("Generate")
    gallery = gr.Gallery(label="Generated Images", columns=2, height="auto")

    generate_button.click(
        fn=generate_images,
        inputs=[prompt_input, images_slider, model_selector],
        outputs=gallery,
    )
    example_selector.change(
        fn=_select_example_prompt,
        inputs=example_selector,
        outputs=prompt_input,
    )


if __name__ == "__main__":
    demo.launch()
