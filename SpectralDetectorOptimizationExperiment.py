import subprocess
import xml.etree.ElementTree as ET
import time
import os
import glob
import json
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np

# ==================================================
# CONFIG
# ==================================================

CONFIG_FILE = r"C:\LasX-API\config_paths.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# ==================================================
# PARAMS
# ==================================================

MAX_WAVELENGTH = 800
SSIM_THRESHOLD = 0.90
STEP = 15
WAIT_TIMEOUT = 30

# ==================================================
# PRINT HELPERS
# ==================================================

def SEP():
    print("======================================")

def OK():
    print("OK")

# ==================================================
# SILENT RUNNER
# ==================================================

def run_script(script_path):
    subprocess.run(
        ["python", script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

# ==================================================
# WAIT FOR FILE
# ==================================================

def wait_for_new_image(folder, previous):

    start = time.time()

    while True:

        current = set(glob.glob(os.path.join(folder, "*.tif")))
        new = current - previous

        if new:
            newest = max(new, key=os.path.getctime)

            # ensure file is fully written
            s1 = os.path.getsize(newest)
            time.sleep(1)
            s2 = os.path.getsize(newest)

            if s1 == s2:
                return newest

        if time.time() - start > WAIT_TIMEOUT:
            raise TimeoutError("WAIT FILE TIMEOUT")

        time.sleep(0.5)

# ==================================================
# IMAGE FLOW (INLINE, NO WRAPPER)
# ==================================================

def acquire_image(paths):

    before = set(glob.glob(os.path.join(paths["IMAGE_FOLDER"], "*.tif")))

    print("--- ACQUIRING IMAGE --- ", end="")
    run_script(paths["ACQUIRE_SCRIPT"])
    OK()

    print("--- SAVING IMAGE --- ", end="")
    run_script(paths["SAVE_IMAGE_SCRIPT"])
    OK()

    print("--- WAITING FOR FILE --- ", end="")
    img = wait_for_new_image(paths["IMAGE_FOLDER"], before)
    OK()

    return img

# ==================================================
# SSIM
# ==================================================

def compute_ssim(a, b):
    img1 = np.array(Image.open(a).convert("L"))
    img2 = np.array(Image.open(b).convert("L"))
    return ssim(img1, img2)

# ==================================================
# LRP CONTROL
# ==================================================

def get_value(lrp):
    tree = ET.parse(lrp)
    root = tree.getroot()

    for e in root.iter():
        a = e.attrib
        if e.tag.endswith("MultiBand") and a.get("Channel") == "2":
            return float(a["RightWorld"])

def set_value(lrp, val):
    tree = ET.parse(lrp)
    root = tree.getroot()

    for e in root.iter():
        a = e.attrib
        if e.tag.endswith("MultiBand") and a.get("Channel") == "2":
            e.set("RightWorld", str(val))
            e.set("TargetWaveLengthEnd", str(val))

    tree.write(lrp)

# ==================================================
# MAIN
# ==================================================

def RunSpectralDetectorExperiment():

    config = load_config()

    paths = {
        "LOAD_INITIAL_SCRIPT": os.path.join(config["script_folder"], "Example_LoadExperiment.py"),
        "SAVE_SCRIPT": os.path.join(config["script_folder"], "Example_SaveExperiment.py"),
        "LOAD_NEW_SCRIPT": os.path.join(config["script_folder"], "Example_LoadNewExperiment.py"),
        "ACQUIRE_SCRIPT": os.path.join(config["script_folder"], "Example_AcquireSingleImage.py"),
        "SAVE_IMAGE_SCRIPT": os.path.join(config["script_folder"], "Example_SaveCurrentSelectedImage.py"),
        "IMAGE_FOLDER": config["image_folder"],
    }

    SEP()
    print("SPECTRAL DETECTOR EXPERIMENT")
    print("         REMEMBER!           ")
    print("1. Select Detector Channel #2")
    print("2. Set experiment template file name EXACTLY to SpectralDetectorExperiment")
    SEP()



    # LOAD
    print("--- LOADING ORIGINAL EXPERIMENT --- ", end="")
    run_script(paths["LOAD_INITIAL_SCRIPT"])
    OK()

    # SAVE TEMPLATE
    print("--- SAVING TEMPLATE EXPERIMENT --- ", end="")
    run_script(paths["SAVE_SCRIPT"])
    OK()

    SEP()
    current = get_value(os.path.join(
        config["template_folder"],
        "{ScanningTemplate}NewSpectralDetectorExperiment.lrp"
    ))

    print(f"INITIAL DETECTOR VALUE: {current}")
    print(f"STEP SIZE: {STEP}")
    SEP()

    # REFERENCE
    ref = acquire_image(paths)

    last_valid = current
    iteration = 1

    while True:

        new_val = last_valid + STEP

        SEP()
        print(f"ITERATION {iteration}")
        print(f"CURRENT VALID VALUE : {last_valid}")
        print(f"PROPOSED NEW VALUE  : {new_val}")
        SEP()

        if new_val > MAX_WAVELENGTH:
            break

        # UPDATE
        print("--- UPDATING DETECTOR VALUE --- ", end="")
        set_value(
            os.path.join(config["template_folder"], "{ScanningTemplate}NewSpectralDetectorExperiment.lrp"),
            new_val
        )
        OK()

        # RELOAD
        print("--- RELOADING EXPERIMENT --- ", end="")
        run_script(paths["LOAD_NEW_SCRIPT"])
        OK()

        # IMAGE FLOW
        img = acquire_image(paths)

        score = compute_ssim(ref, img)

        SEP()
        print(f"SSIM SCORE: {score:.4f}")

        if score < SSIM_THRESHOLD:

            print("!!! SPECTRAL CONTAMINATION DETECTED !!!")
            print(f"SSIM {score:.4f} < threshold {SSIM_THRESHOLD}")

            print("--- ROLLBACK TO LAST VALID VALUE --- ", end="")
            set_value(
                os.path.join(config["template_folder"], "{ScanningTemplate}NewSpectralDetectorExperiment.lrp"),
                last_valid
            )
            run_script(paths["LOAD_NEW_SCRIPT"])
            OK()
            break

        last_valid = new_val
        ref = img
        iteration += 1

    SEP()
    print("EXPERIMENT FINISHED")
    print(f"FINAL VALID DETECTOR VALUE: {last_valid}")
    SEP()

# ==================================================
# ENTRY
# ==================================================

if __name__ == "__main__":
    RunSpectralDetectorExperiment()