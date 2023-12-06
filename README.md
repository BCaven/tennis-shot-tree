# tennis-shot-tree

    Blake Caven
Prediction algorithm that determines next best shot based on current rally

# training data:
https://github.com/JeffSackmann/tennis_MatchChartingProject

Due to space concerns, the raw data is excluded from this git repo.

# setting up the project:
Source code is stored in the ```src/``` directory.

Data is stored in ```data/``` with each category of data being stored in its own subfolder.

- For example: raw data is stored in ```data/raw/```

All files should be run from the parent directory, not the ```src/``` folder.

- For example: ```usr@tennis-shot-tree: python3 src/parse-raw-data.py``` 

# Building the project

After cloning the repo, run `./set-up-project` to download the data
It is recommended to use `./parse-data` to create smaller datasets that are limited to specific players, but it is not required.

Once the data has been downloaded, run `./demo` to see a demonstration of two different algorithms playing each other.

Alternatively, you can use `./tennis-shot-tree` to create your own scenarios

All scripts (excuding `./demo`) have documentation that can be accessed via the `--help` flag.

# Supported algorithms and modes:

At the moment, the project supports human vs human, human vs ai, and ai vs ai.

There are four different AI models to choose from:
- maximize one of your own stats
- minimize one of your own stats
- maximize one of the opponent's stats
- minimize one of the opponent's stats

More detail can be found by running `./tennis-shot-tree --help` and an example can be found in `./demo`


# original project proposal:

    So far, most of the work on this project has been thinking about how to use the data that has been collected. Tennis is a complex sport, and unlike a game like Chess, a simple decision tree is unlikely to yield satisfactory results. Due to this, it is tempting to make many assumptions about the player’s ability - primarily, assuming that the player is able to perfectly execute the shot being recommended to them. So, obviously, this is not realistic because every player (even professional players) often make mistakes. Instead I am going to try to model the algorithm around this, so the recommended best shot is not a general thing, but is instead what is recommended for the current player. For example, if the player has not made any backhands so far in the match, the algorithm should not recommend that they only hit backhands.
    The dataset being used for this project is very detailed (it can be found here: https://github.com/JeffSackmann/tennis_MatchChartingProject) and I have written a program to parse the data into more manageable chunks. This data will be first compiled into general statistics about the matches recorded, and will likely be split into separate categories based on playstyles and court surfaces (what works on a grass court might not work on a hard court). I am hoping that this data can be used to create algorithms to generate the “best next shot” for each surface and playstyle and once these smaller algorithms have been created, they can either be combined into one larger algorithm, or I can write a broader algorithm that picks which of the smaller algorithms to use. Once written, I will train the models on the dataset collected and test the models on a combination of current matches and old matches that are not included in the dataset.

# pivots that were made:

The project was shifted to focus on comparatively simpler (static) models instead of trying to make dynamic models. This was due largely to time constraints and not realizing how much work was required to format the dataset in a useful way.

# self-evaluation:

I was very happy with how this project turned out. The project ended up being a lot more work to set up than I anticipated but I attempted to make the project as flexible as possible and give the user as much control as I could by avoiding hardcoded values.
I was also happy with the documentation that I made as I went along because it was extremely helpful when returning to the project to check in on what I was doing and what needed to be done.
I was also pleased with how the minmax algorithms ended up working, although it took a lot of time to fine-tune the algorithms to not go for 'stupid' shots that were actually just data outliers.


# Running the demo:

```sh
git clone https://github.com/BCaven/tennis-shot-tree.git # clone the repo
cd tennis-shot-tree # go to the repo
./set-up-project    # set up the data folder and download the data
./demo              # run the demo
```
