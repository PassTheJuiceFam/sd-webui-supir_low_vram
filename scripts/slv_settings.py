import gradio as gr
from modules import shared, script_callbacks


def on_ui_settings():
    section = ('slv', "Supir - Low VRAM")
    shared.opts.add_option(
        "slv_pos_prompt",
        shared.OptionInfo(
            f"Cinematic, High Contrast, highly detailed, taken using a Canon EOS R camera, hyper detailed photo"
            f" - realistic maximum detail, 32k, Color Grading, ultra HD, extreme meticulous detailing, "
            f"skin pore detailing, hyper sharpness, perfect without deformations.",
            "Default SUPIR Prompt",
            gr.Textbox,
            {"interactive": True},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_neg_prompt",
        shared.OptionInfo(
            f"painting, oil painting, illustration, drawing, art, sketch, oil painting, cartoon, CG Style, 3D render, "
            f"unreal engine, blurring, dirty, messy, worst quality, low quality, frames, watermark, signature, "
            f"jpeg artifacts, deformed, lowres, over-smooth",
            "Default SUPIR Negative Prompt",
            gr.Textbox,
            {"interactive": True},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_steps",
        shared.OptionInfo(
            50,
            "Default SUPIR Steps",
            gr.Slider,
            {"minimum": 20, "maximum": 200, "step": 1},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_prompt_cfg",
        shared.OptionInfo(
            7.5,
            "Default SUPIR Prompt CFG",
            gr.Slider,
            {"minimum": 1.0, "maximum": 15.0, "step": 0.1},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_ctrl_str",
        shared.OptionInfo(
            1.0,
            "Default SUPIR Guidance",
            gr.Slider,
            {"minimum": 0.0, "maximum": 1.0, "step": 0.05},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_noise",
        shared.OptionInfo(
            1.003,
            "Default SUPIR Noise",
            gr.Slider,
            {"minimum": 1.0, "maximum": 1.1, "step": 0.001},
            section=section,
        )
    )
    shared.opts.add_option(
        "slv_client_address",
        shared.OptionInfo(
            "http://127.0.0.1:6688/",
            "Default SUPIR Server IP/Port",
            gr.Textbox,
            {"lines": 1, "max_lines": 1, "info": "Enter in the format: http://127.0.0.1:6688/"},
            section=section,
        )
    )


script_callbacks.on_ui_settings(on_ui_settings)
