import modules.scripts as scripts
import gradio as gr

from scripts.slv_logging import logger
from scripts.slv_upscaling import UpscalingParams, request_upscale, PILImage

import gc
import torch
import copy
from typing import List, Tuple, Any
import traceback

from modules.processing import (process_images, Processed, StableDiffusionProcessing, StableDiffusionProcessingImg2Img)
from modules.images import save_image
from modules.shared import opts, cmd_opts, state
from modules.ui_components import InputAccordion


class SupirLowVramScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.save_samples: bool = opts.samples_save

    @property
    def save_samples(self):
        return self._save_samples

    @save_samples.setter
    def save_samples(self, value: bool):
        self._save_samples = value

    @property
    def sd_opt_samples_save(self) -> bool:
        return opts.samples_save

    def title(self):
        return "Supir - Low VRAM"

    def show(self, is_img2img: bool):
        return scripts.AlwaysVisible

    def ui(self, is_img2img: bool):     # TODO: Need to consider whether UI code is worth moving to it's own script
                                        # TODO: Implement reset ui params to default
        """
        def slv_ui_get_defaults(*args):
            outputs = []

            for i, arg in enumerate(args):
                logger.info(f"arg: {type(arg)}")
                outputs.append(opts.data.get(arg, "Error"))
            return outputs
        """
        with InputAccordion(
                value=False,
                label="SUPIR Upscale - Low VRAM",
                visible=True
        ) as slv_enable:
            with gr.Row():
                slv_skip_img2img = gr.Checkbox(value=False, visible=is_img2img, label="Skip Img2Img")
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        slv_upscale_amount = gr.Slider(minimum=2, maximum=8, step=1, value=2, label="Upscale Amount")
                        slv_seed = gr.Number(label="Seed", info="Set to -1 for random seed",
                                             minimum=-1, maximum=2147483647, value=-1, step=1, precision=0)
                    with gr.Row():
                        slv_pos_prompt = gr.Textbox(value=opts.data.get("slv_pos_prompt", ""),
                                                    label="Prompt", lines=2, elem_id="slv_pos_prompt")
                    #with gr.Row():
                    #    slv_reset_prompts_button = gr.Button(value="Reset Text Prompts", size='md')
                    with gr.Row():
                        slv_neg_prompt = gr.Textbox(value=opts.data.get("slv_neg_prompt", ""),
                                                    label="Negative Prompt", lines=2, elem_id="slv_neg_prompt")
                    with gr.Row():
                        slv_steps = gr.Slider(value=opts.data.get("slv_steps", 50),
                                              minimum=20, maximum=200, step=1, label="Steps")
                        slv_prompt_cfg = gr.Slider(value=opts.data.get("slv_prompt_cfg", 7.5),
                                                   minimum=1.0, maximum=15.0, step=0.1, label="Prompt CFG")
                    with gr.Row():
                        slv_ctrl_str = gr.Slider(value=opts.data.get("slv_ctrl_str", 1.0),
                                                 minmum=0.0, maximum=1.0, step=0.05, label="Guidance Strength")
                        slv_noise = gr.Slider(value=opts.data.get("slv_noise", 1.003),
                                              minimum=1.0, maximum=1.1, step=0.001, label="Noise")
                    with gr.Row():
                        slv_client_address = gr.Textbox(value=opts.data.get("slv_client_address", ""),
                                                        label="Upscale Server IP/Port", info="(http://127.0.0.1:6688/)")

            #slv_reset_prompts_button.click(fn=slv_ui_get_defaults, inputs=[slv_pos_prompt, slv_neg_prompt],
            #                               outputs=[slv_pos_prompt, slv_neg_prompt])

        components = [                  # Component order important; if changed post/process() logic need to be updated
            slv_enable,                 # [0]
            slv_skip_img2img,           # [1]
        ]

        sup_params = [                  # Component order important; if changed, parse_ui_params() needs to be updated
            slv_upscale_amount,         # [2]
            slv_seed,                   # [3]
            slv_pos_prompt,             # [4]
            slv_neg_prompt,             # [5]
            slv_steps,                  # [6]
            slv_prompt_cfg,             # [7]
            slv_ctrl_str,               # [8]
            slv_noise,                  # [9]
            slv_client_address          # [10]
        ]

        components = components + sup_params

        return components

    def parse_ui_params(self, *components: Tuple[Any, ...]) -> UpscalingParams:
        upscaling_params = UpscalingParams(     # TODO: This is messy, need to improve it
            upscale_amount=components[2],
            seed=components[3],
            pos_prompt=components[4],
            neg_prompt=components[5],
            steps=components[6],
            prompt_cfg=components[7],
            ctrl_str=components[8],
            noise=components[9],
            client_address=components[10]
        )

        return upscaling_params

    def unload_sd_model(self, p: StableDiffusionProcessing):
        model_name = copy.deepcopy(p.sd_model_name)
        logger.info("SD Model = %s", model_name)
        p.sd_model.cpu()    # Move the sd model out of VRAM and into RAM
        gc.collect()
        torch.cuda.empty_cache()    # Remove any unreferenced torch data in VRAM
        return True, model_name     # VRAM usage won't appear to change, but will be made available for other programs

    def reload_sd_model(self, p: StableDiffusionProcessing, model_name):
        logger.info(f"Reloading {model_name}...")
        p.sd_model.cuda()   # Move the sd model back into VRAM and out of RAM
        del model_name      # Delete model info and garbage collect to prevent bloat in RAM
        gc.collect()
        torch.cuda.empty_cache()    # Unsure whether this is needed, but doesn't cause issues lol
        return

    def process(self, p: StableDiffusionProcessing, *components) -> None:
        try:
            logger.debug("Process:")
            if components[0]:                            # components[0] should be slv_enable in ui()
                logger.info("Enabled")
                if isinstance(p, StableDiffusionProcessingImg2Img):
                    logger.debug("IMG2IMG")
                    if components[1]:                    # components[1] should be slv_skip_img2img in ui()
                        logger.info("Skipping Img2Img")  # 'Skip' Img2Img | Img2Img can't actually be skipped
                        p.steps = 1                      # Instead, make SD generate junk result to discard
                        p.sampler_name = "Euler"         # Same method as adetailer (shouldn't clash)
                        p.width = 64
                        p.height = 64
                        self.save_samples = opts.samples_save       # Store SD option on whether we save generated imgs
                        opts.samples_save = False                   # Set SD option to False, so junk result not saved

        except Exception as e:
            logger.error("SUPIR failed process: %s", e)
            traceback.print_exc()

    def postprocess(self, p: StableDiffusionProcessing, processed: Processed, *components) -> None:
        try:
            logger.debug("Post Process")
            if components[0]:                           # components[0] should be slv_enable in ui()
                logger.debug("Enabled")
                opts.samples_save = self.save_samples   # Set SD option to previously stored value
                is_model_unld, unld_model_name = self.unload_sd_model(p)    # Unload the model to free up VRAM for SUPIR
                upscaler_params = self.parse_ui_params(*components)

                if isinstance(p, StableDiffusionProcessingImg2Img):
                    logger.debug("IMG2IMG")
                    if components[1]:                                       # If we skip img2img, copy the init image(s)
                        orig_images: List[PILImage] = p.init_images[:]      # to orig_images to upscale instead
                        orig_infotexts: List[str] = processed.infotexts[
                                                    processed.index_of_first_image:     # TODO: Fix infotext issues
                                                    ]
                    else:
                        orig_images: List[PILImage] = processed.images[             # If not skipping img2img, get the
                                                   processed.index_of_first_image:  # generated output images to upscale
                                                   ]
                        orig_infotexts: List[str] = processed.infotexts[
                                                    processed.index_of_first_image:
                                                    ]
                else:
                    logger.debug("TXT2IMG")
                    orig_images: List[PILImage] = processed.images[
                                               processed.index_of_first_image:
                                               ]
                    orig_infotexts: List[str] = processed.infotexts[
                                                processed.index_of_first_image:
                                                ]

                upscaled_images = request_upscale(orig_images, upscaler_params)
                logger.info(f"Upscaling Complete. Returned ({len(upscaled_images)}) img(s)")

                try:
                    for i, img in enumerate(upscaled_images):
                        if p.outpath_samples and opts.samples_save:
                            save_image(
                                img,
                                p.outpath_samples,
                                "",
                                p.all_seeds[i],  # type: ignore
                                p.all_prompts[i],  # type: ignore
                                opts.samples_format,
                                info=orig_infotexts[i],
                                p=p,
                                suffix="-upscaled",
                            )
                except Exception as e:
                    logger.error("Could not save results. %s", e)
                    traceback.print_exc()

                processed.images = upscaled_images

                if is_model_unld:   # If the SD model was unloaded, reload it after postprocess is done
                    self.reload_sd_model(p, unld_model_name)

        except Exception as e:
            logger.error("SUPIR failed post-process: %s", e)
            traceback.print_exc()
