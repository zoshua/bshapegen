# BShapeGen
A Simple Toolset for Creating a Model and Predicting 3D Polygon Vertex Data using PyTorch and Maya

## Table of Contents
<!--ts-->
   * [Key Features](#key-features)
   * [Requirements](#requirements)
   * [Setup](#setup)
   * [Step by Step](#step-by-step)
   * [Video Demo](#video-demo)
   * [Results](#results)
   * [Next Steps](#next-steps)

<!--te-->

## Key Features
* Initialize Test Data Scene
* Export Training Data
* Build Model
* Predict and Import Data

## Requirements
* [Anaconda](https://www.anaconda.com/download) Installed
* [Maya](https://www.autodesk.com/products/maya) +2020 Installed

## Setup
1. Clone or Download Source and Unzip to Local Machine
2. Open a Terminal or Command Prompt and Navigate to the top bshagegen directory</br>
   
   Windows ie. `c:/dev/src/bshapegen `

   Mac ie. `~\dev\src\bshapegen`
2. Windows - in command prompt run: 
   ```
   .\cmd\init_env_conda.bat
   ```
   MacOs M1 - in terminal run:
   ```
   source ./sh/init_env_conda_M1.sh
   ```
3. Confirm PyTorch is Installed by running the following from the same shell</br>
   ```
   python -c "import torch;print(torch.__version__)"
   ```
   Successful return should look like this (versions might differ)
   ```
   2.1.0
   ```

## Step by Step
1. Clone Repo Locally
1. Launch Maya
1. Run this in a python tab in the script editor (change `bsg_py_path` to your local machine location)
```py
import os
import sys
#
bsg_py_path = '/Users/zoshua/src/bshapegen/py'
sys.path.append(bsg_py_path)
#
from bshapegen.maya import bsg_ui
#
bsg_ui = bsg_ui.BSG_UI();
bsg_ui.show(dockable=True);
```
4. Dock the `BlendShapeGen` dialog if needed
4. Update the `Work Dir` location if needed
4. Click the `Build Test Scene` button
4. Click the `Export Training Data` button
4. Click the `Build Model` button
4. Click the `Export > Predict > Import Data` button

## Video Demo
[![bshapegen - Demo](https://img.youtube.com/vi/dmpzJW1QcdQ/1.jpg)](https://youtu.be/dmpzJW1QcdQ "bshapegen - Demo - Click to Watch!")

**Color Guide:**
* yellow = training input neutral data (model build)
* orange = training output pose data (model build)
* cyan = neutral input data (model prediction)
* blue = reference pose data (used to measure and visualize model accuracy)
* magenta = pose output data (model prediction)

## Sample Build and Predict Results
| train samples | neurons | epochs | learning rate | loss | validation | predict samples | predict err sum |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 100 | 512 | 150  | 0.001 | 0.007996 | 0.007446 | 5 | 3.16174 |
| 100 | 1024 | 150  | 0.001 | 0.002554 | 0.002974 | 5 | 2.92702 |
| 100 | 1024 | 300  | 0.001 | 0.000129 | 0.000123 | 5 | 2.98027 |

## Next Steps
* Explore alternate model configurations
* Explore higher resolution mesh data
