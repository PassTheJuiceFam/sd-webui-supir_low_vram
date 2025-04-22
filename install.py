import launch
from importlib import metadata
from packaging.version import parse
from pathlib import Path

ext_root = Path(__file__).parent
requirements_file = ext_root / "requirements.txt"

def install_requirements(req_file):
    with open(requirements_file) as file:
        print("SUPIR: Checking and Installing requirements...")
        for package in file:
            try:
                package = package.strip()
                if "==" in package:
                    package_name, package_version = package.split("==")
                    installed_version = metadata.version(package_name)
                    if installed_version != package_version:
                        print(f"Installing {package}...")
                        launch.run_pip(
                            f'install -U "{package}"',
                            f"sd-webui-supir_low_vram requirement: changing {package_name} version from {installed_version} to {package_version}",
                        )
                    else: print(f"SUPIR: {package} already installed")
                elif ">=" in package:
                    package_name, package_version = package.split(">=")
                    installed_version = metadata.version(package_name)
                    if not installed_version or parse(
                        installed_version
                    ) < parse(package_version):
                        print(f"Installing {package}...")
                        launch.run_pip(
                            f'install -U "{package}"',
                            f"sd-webui-supir_low_vram: changing {package_name} version from {installed_version} to {package_version}",
                        )
                    else: print(f"SUPIR: {package} is already installed")
            except Exception as e:
                print(e)
                print(
                    f"sd-webui-supir_low_vram Warning: Failed to install {package}, likely won't work."
                )

install_requirements(requirements_file)

