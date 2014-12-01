class MILKChunk:
    predNames = []
    predNums = [] # corresponds w/ the names above (e.g., 0,1,2 might be put, combine, mix)
    prob = 0
    verbMarkers = "" # provided by eugene
    verbs = [] # the length corresponds to the # of 1's in the verbMarkers array

    def __init__(self, pNames, pNums, prob, vMarkers, v):
        self.predNames = pNames
        self.predNums = pNums
        self.prob = prob
        self.verbMarkers = vMarkers
        self.verbs = v

    def __str__(self):
        return "milkchunk:" + str(self.predNames) + " => " + str(self.verbMarkers) + "; " + str(self.verbs) + " = " + str(self.prob)

    #def dostuff(self):
    #    self.newvar = 919

    
