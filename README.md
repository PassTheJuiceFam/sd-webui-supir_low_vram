# SUPIR - Low VRAM for AUTOMATIC1111

An extension for AUTOMATIC1111, allowing the use of SUPIR upscaling within the web-ui. This extension requires my SUPIR_Low_VRAM_Backend and will not function without it - [the repo can be found here.](https://github.com/PassTheJuiceFam/SUPIR_Low_VRAM_Backend/)
Specifically designed for low-VRAM systems, this extension allows users to integrate SUPIR upscaling into their txt2img and img2img workflows, requiring only around 10-12GB VRAM.

## Disclaimer

- I'm happy for anyone to use/alter any part of this extension for any non-commercial projects, excluding political/scientific disinformation, or purposes that infringe on the privacy of or defame another person or otherwise cause harm to an individual or group.
- Although this extension was written by myself, the use of SUPIR is subject to the open-source licensing restrictions stipulated in the [SUPIR repo by Fanghua-Yu.](https://github.com/Fanghua-Yu/SUPIR).

## Installation & Requirements

- To run SUPIR, you'll need approx ~64GB of memory available. 32GB RAM + 32GB pagefile is sufficient on my machine. This may be more or less depending on the Stable Diffusion checkpoints/VAEs you use to generate outputs, as this extension caches models not currently being used in memory to free VRAM.
- SUPIR requires CUDA, meaning your GPU must be CUDA compatible.
- [SUPIR_Low_VRAM_Backend](https://github.com/PassTheJuiceFam/SUPIR_Low_VRAM_Backend/).
  
To install, simply clone this repo and place the entire "sd-webui-supir_low_vram" folder in your ".../stable-diffusion-webui/extensions/" folder, the same as you'd do with any other extension. The only requirement the extension has is gradio_client>=1.0.1 - the web-ui should install this automatically on launch once you've moved the cloned repo into your extensions folder.

## Usage

Ensure both Auto1111 and SUPIR_Low_VRAM_Backend are running. The backend will listen for requests on the IP/Port displayed on the console. When enabled in the Auto1111 web-ui, the extension will call the backend to upscale your image - you can observe this in the console windows of both programs. When the upscale is complete, the backend will send the upscaled image back to Auto1111 and the generation process will continue as usual.

![image](https://github.com/user-attachments/assets/f19e4826-0f68-4e7b-b54f-5d2b39680ecf)

SUPIR - Low VRAM UI is automatically added to both txt2img and img2img when installed. The extension runs in Stable Diffusion's postprocess and requests an upscale from the back-end, submitting the image and parameters specified in the UI before recieving the upscaled image and passing it back to Stable Diffusion. Result images will appear in the respective txt2img/img2img output directories and the web ui output.
- The Skip Img2Img option is available in the img2img UI and upscales the original input image. As this causes the extension to ignore the generated image, extensions that apply before the upscaler likely won't have any effect on the final result.
- SUPIR's minimum output resolution is 1024x1024, if an upscale value is chosen that would produce an image with either dimension < 1024, the SUPIR model automatically raises the upscale amount to meet the minimum required resolution.
- The extension currently only includes SUPIR's 'Stage 2' process (the upscale), I hope to eventually include 'Stage 1' & Llava, however there is no guarantee on this.

## Thanks
- Thank you to the SUPIR team for both their incredible work with SUPIR and for releasing the project as open-source
- Thank you to all the developers of AUTO1111 extensions, whose code I spent time digging around through to learn how AUTO1111 extensions work 
