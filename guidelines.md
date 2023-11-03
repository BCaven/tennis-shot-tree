# guidelines

DO NOT test your model on the same data that you used to train it!

# problems

This problem is hard, things to look out for:
- different players having different "effective" styles: something that works for one player might not work for another
- look at players that have a *lot* of match data, could you make a model just against them?
- there is a chance that a general model will not work because of the inherent differences between players (what works for Rafa might not work for literally anyone else)

# modifications

Things to think about:
- if you make it interactive: develop a "profile" for the player in question, "people that have weak backhands shouldn't be recommended to just hit backhands"
- lumping players into categories: examples: "heavy hitters", "grinders", "net players", "counter punchers", etc.

# notes from talking to chace:

see if a clustering algorithm can separate data into several different trees (might be able to cluster the trees as well)



# ok so, trying to type while talking to mom...

basic idea is to take the shot data and separate it into probability trees which predict what the best shot is based on what has previously happened in the match

make a distance metric 
