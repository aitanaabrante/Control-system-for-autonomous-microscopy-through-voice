# Control system for autonomous microscopy through voice
## Overview
This repository contains the software developed for my Bachelor's Thesis in Biomedical Engineering at Universidad Carlos III de Madrid, in collaboration with the Advanced Optical Microscopy Unit at the Instituto de Salud Carlos III (ISCIII).

The project implements a voice-controlled interface for Leica LAS X microscopy software, allowing users to execute predefined microscope operations through natural-language voice commands. In addition to command execution, the system incorporates an automated spectral detector optimization experiment based on iterative image acquisition and quantitative image analysis.

The software is organized into five main components, separating API communication, user interaction, command interpretation, microscope operations, and experimental automation.

## Software Architecture
The system follows a modular architecture in which the graphical interface coordinates the workflow and delegates command interpretation and execution to specialized modules.
#### 1. InitialConnection.py
Establishes and maintains communication between Python and the Leica LAS X API through the API connector. This component provides the connection required by the other modules to interact with LAS X, avoiding the need to establish a separate connection for each microscope operation.
#### 2. DictionaryCode.py
Interprets the transcribed voice commands and maps them to the corresponding predefined microscope actions. This module acts as the intermediate layer between the graphical interface and the executable microscope functions, separating natural-language input from the underlying implementation.
#### 3. ScriptsToFunctions.py
Contains the executable functions responsible for performing microscope operations through the LAS X API. The command interpretation module delegates the requested actions to this component, which communicates with LAS X to execute the corresponding operations.
#### 4. SpectralDetectorOptimizationExperiment.py
Implements an automated microscopy experiment that extends the system beyond individual voice-command execution.

The experiment iteratively modifies the spectral detector configuration, acquires images, and evaluates image similarity using the Structural Similarity Index Measure (SSIM). By comparing consecutive images, the algorithm identifies changes consistent with spectral contamination and can revert to a previously valid configuration when the similarity falls below the defined threshold.

The experiment combines API-based microscope control, automated image acquisition, quantitative image analysis, and decision-making based on experimental results.
#### 5. ASRToDictionaryWhisperSpaceBarGUI.py
Provides the graphical user interface (GUI) through which the user interacts with the system. It manages user interaction, audio acquisition, and speech recognition. 

## System Workflow
The main interaction loop connects the five components as follows:
1. First, the user activates audio recording by pressing the space bar through #### ASRToDictionaryWhisperSpaceBarGUI.py. Whisper
3. 
