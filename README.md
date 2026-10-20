# Control system for autonomous microscopy through voice
## Overview
This repository contains the software developed for my Bachelor's Thesis in Biomedical Engineering at Universidad Carlos III de Madrid, in collaboration with the Advanced Optical Microscopy Unit at the Instituto de Salud Carlos III (ISCIII).

The project implements a voice-controlled interface for Leica LAS X microscopy software, allowing users to execute predefined microscope operations through natural-language voice commands. In addition to command execution, the system incorporates an automated spectral detector optimization experiment based on iterative image acquisition and quantitative image analysis.

The software is organized into five main components, separating API communication, user interaction, command interpretation, microscope operations, and experimental automation.

## Software Architecture
The system follows a modular architecture in which the graphical interface coordinates the workflow and delegates command interpretation and execution to specialized modules.
#### 1. InitialConnection.py:
#### 2. DictionaryCode.py
#### 3. ScriptsToFunctions.py
#### 4. SpectralDetectorOptimizationExperiment.py
#### 5. ASRToDictionaryWhisperSpaceBarGUI.py
