from ScriptsToFunctions import Example_MessageChat1
from ScriptsToFunctions import Example_GetConfocalHardwareInfo1
from ScriptsToFunctions import Example_AssignJob1
from ScriptsToFunctions import Example_AcquireJob1
from ScriptsToFunctions import Example_LoadExperiment1
from ScriptsToFunctions import Example_StartAFScan1
from SpectralDetectorOptimizationExperiment import RunSpectralDetectorExperiment

Dictionary = {
    "message": Example_MessageChat1,
    "confocal information": Example_GetConfocalHardwareInfo1,
    "assign job": Example_AssignJob1,
    "execute job": Example_AcquireJob1,
    "load experiment": Example_LoadExperiment1,
    "set experiment": Example_LoadExperiment1,
    "autofocus scan": Example_StartAFScan1,
    "spectral detector experiment": RunSpectralDetectorExperiment
    }