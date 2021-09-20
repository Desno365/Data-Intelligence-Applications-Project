# Data Intelligence Applications Project


## Assignment

We chose the "Advertising and Social influence" project as reported in [project-proposals.pdf](https://github.com/lleugen/data_intelligence_applicationsblob/main/project-proposals.pdf)


## Usage

The runnable scripts used to run analyses and create plots are `step1.py`, `step3.py` and `step4_5_6.py`. Each script comes with a first section called "Constants" that includes variables which are used as settings for that particular analysis.<br>
There are also global settings that are stored in the variables contained in `constants.py`, for example there are stored the number of nodes in the network, the number of categories, the number of slots and many others global variables.

Also, there are runnable scripts in the `tests` folder that are used internally to check the correctness of the algorithms. For example the script `test_vcg_auction.py` contains some unit tests to check the correctness of the VCG Auction.
