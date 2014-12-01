class RecipeTranslation:
    
    milkChunks = [] # stores each MILKChunk
    predMarkers = [] # stores each head position; marker that the HMM took to get here
    totalProb = 0

    def __init__(self, milkchunks=[], predmarkers=[], prob=0):
        self.milkChunks = milkchunks
        self.predMarkers = predmarkers
        self.totalProb = prob

    # NOTE: this expects one to copy a previous RecipeTranslation object
    # then call this method, where passed-in 'prob' corresponds just to
    # the current passed-in mc milkchunk, so it will be multiplied (log added)
    # to the current self.totalProb
    # note: expects the passed-in prob to have already been converted to log form
    def addMILKChunk(self, mc, predMarker, prob):
    	self.milkChunks.append(mc)
    	self.predMarkers.append(predMarker)
    	self.totalProb += prob

    def isEmpty():
        if (len(milkChunks) == 0):
            return true
        return false

    def __str__(self):
        return "RT: # milkChunks: " + str(len(self.milkChunks))