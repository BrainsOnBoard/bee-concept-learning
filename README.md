# Bee concept-learning
A model of how honey bees learn the concept of sameness and difference

## Running the model
Install SpineML_2_BRAHMS as detailed [here](http://spineml.github.io/simulators/BRAHMS/ "S2B Installation"). We recommend using Ubuntu Linux for ease.

Clone this repository, and edit the scripts/setup.py file, adding the path to the repository and the paths to your SpineML toolchain.

The model can be run using the batch_X.py scripts to run the vaious experiments - data can be analysed using the process_data.py script.

The model can be viewed in the SpineCreator GUI. For installation of Spinecreator see [here](http://spineml.github.io/spinecreator/sourcelin/ "SC Installation"). Then open the .proj file in the /model directory using the File/Open Project menu item from SpineCreator. Individual runs of the model can be performed from within SpineCreator, however you need to be sure to run the correct scripts/world_X.py file before launching from SpineCreator.

The reduced model can be found in the matlab_model directory and can be run in GNU Octave or MATLAB.
