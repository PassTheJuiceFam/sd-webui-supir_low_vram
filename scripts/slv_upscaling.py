import os
from dataclasses import dataclass
from typing import List
from scripts.slv_logging import logger
from gradio_client import Client, handle_file
import tempfile
from PIL import Image
PILImage = Image.Image


@dataclass
class UpscalingParams:

    upscale_amount: int = 2
    seed: int = -1
    pos_prompt: str = ""
    neg_prompt: str = ""
    steps: int = 50
    prompt_cfg: float = 7.5
    ctrl_str: float = 1.0
    noise: float = 1.003
    client_address: str = "http://127.0.0.1:6688/"


def request_upscale(images: List[PILImage], slv_params: UpscalingParams) -> List[PILImage]:
    logger.info(f"Attempting to upscale {len(images)} image(s) by {UpscalingParams.upscale_amount}...")
    path = "./extensions/sd-webui-supir_low_vram/cache"
    logger.debug(f"Path: {path}")
    if not os.path.isdir(path):
        try:
            logger.info(f"No cache folder, attempting to create one...")
            os.mkdir(path)
        except Exception as e:
            logger.info(f"Failed to make {path}. {e}")
    path = path + "/tmp"
    os.mkdir(path)
    logger.debug(f"Temp path: {path}")
    for i, image in enumerate(images):
        if min(image.width, image.height) * slv_params.upscale_amount < 1024:
            logger.warning(f"One or more upscaled img dimensions would be less than SUPIR's minimum output resolution:"
                           f" [1024x1024]\n"
                           f"SUPIR will instead upscale to the closest minimum value: "
                           f"~({round(1024 / min(image.width, image.height),1)}x)\n")
        with tempfile.NamedTemporaryFile(
                dir=path, delete=False, suffix=f".png"
        ) as temp_file:
            img_path = temp_file.name
            image.save(img_path)
        try:
            client = Client(UpscalingParams.client_address)
            logger.info("Waiting for SUPIR server to finish upscale...")
            result_image = client.predict(
                input_image=handle_file(img_path),
                upscale=slv_params.upscale_amount,
                seed=slv_params.seed,
                steps=slv_params.steps,
                prompt_cfg=slv_params.prompt_cfg,
                s2_str=slv_params.ctrl_str,
                noise=slv_params.noise,
                a_prompt=slv_params.pos_prompt,
                n_prompt=slv_params.neg_prompt,
                api_name="/call_upscaler"
            )
            logger.info(f"Received from client: {result_image}")
            result_image = Image.open(fr"{result_image}")
            images[i] = result_image
            # Clean up
            os.remove(img_path)
            os.rmdir(path)
        except Exception as e:
            logger.error("Failed to upscale: %s", e)
            logger.info(os.remove(img_path))
            logger.info(os.rmdir(path))
    return images
