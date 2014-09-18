# $Id: bleu.py 1307 2007-03-14 22:22:36Z hieuhoang1972 $
# Revised by Qi Xin

# Refer to,
# https://code.google.com/p/smt/source/browse/trunk/moses64/tools/moses-scripts/training/cmert-0.5/bleu.py?r=2
# for its original version

'''
tests: a list of test sentences
refss: a list of reference lists
n: up to n-gram

To get the bleu score, run with
score_set(tests, refss, n)
'''

import sys, math, re, xml.sax.saxutils

eff_ref_len = "shortest"

normalize2 = [
    (r'([\{-\~\[-\` -\&\(-\+\:-\@\/])',r' \1 '), # tokenize punctuation. apostrophe is missing
    (r'([^0-9])([\.,])',r'\1 \2 '),              # tokenize period and comma unless preceded by a digit
    (r'([\.,])([^0-9])',r' \1 \2'),              # tokenize period and comma unless followed by a digit
    (r'([0-9])(-)',r'\1 \2 ')                    # tokenize dash when preceded by a digit
    ]

normalize2 = [(re.compile(pattern), replace) for (pattern, replace) in normalize2]

def normalize(s):
    '''Normalize and tokenize text. This is lifted from NIST mteval-v11a.pl.'''
    # Added to bypass NIST-style pre-processing of hyp and ref files -- wade
    for (pattern, replace) in normalize2:
        s = re.sub(pattern, replace, s)
    return s.split()


def count_ngrams(words, n=4):
    counts = {}
    for k in xrange(1,n+1):
        for i in xrange(len(words)-k+1):
            ngram = tuple(words[i:i+k])
            counts[ngram] = counts.get(ngram, 0)+1
    return counts
        

def cook_refs(refs, n=4):
    '''
    maxcounts record, for each ngram, the max occurring counts in any ref
    Return a tuple of (list of ref length, maxcounts)
    '''
    
    refs = [normalize(ref) for ref in refs]
    maxcounts = {}
    for ref in refs:
        counts = count_ngrams(ref, n)
        for (ngram,count) in counts.iteritems():
            maxcounts[ngram] = max(maxcounts.get(ngram,0), count)
    return ([len(ref) for ref in refs], maxcounts)
                                                

def cook_test(test, (reflens, refmaxcounts), n=4):
    '''
    result is a dict of the counts
    '''

    test = normalize(test)
    result = {}
    result["testlen"] = len(test)
    
    # Calculate effective reference sentence length.
    
    if eff_ref_len == "shortest":
        result["reflen"] = min(reflens)
    elif eff_ref_len == "average":
        result["reflen"] = float(sum(reflens))/len(reflens)
    elif eff_ref_len == "closest":
        min_diff = None
        for reflen in reflens:
            if min_diff is None or abs(reflen-len(test)) < min_diff:
                min_diff = abs(reflen-len(test))
                result['reflen'] = reflen

    result["guess"] = [max(len(test)-k+1,0) for k in xrange(1,n+1)]

    # result['correct'] records, for each n (gram #),
    # the total count of n-gram overlaps between test and refs
    
    result['correct'] = [0]*n
    counts = count_ngrams(test, n)
    for (ngram, count) in counts.iteritems():
        result["correct"][len(ngram)-1] += min(refmaxcounts.get(ngram,0), count)
        
    return result

def score_cooked(allcomps, n=4):
    totalcomps = {'testlen':0, 'reflen':0, 'guess':[0]*n, 'correct':[0]*n}
    for comps in allcomps:
        for key in ['testlen','reflen']:
            totalcomps[key] += comps[key]
        for key in ['guess','correct']:
            for k in xrange(n):
                totalcomps[key][k] += comps[key][k]

    logbleu = 0.0
    for k in xrange(n):
        if totalcomps['correct'][k] == 0:
            return 0.0
        print("%d-grams: %f\n" % (k,float(totalcomps['correct'][k])/totalcomps['guess'][k]))
        logbleu += math.log(totalcomps['correct'][k])-math.log(totalcomps['guess'][k])
    logbleu /= float(n)
    print("Effective reference length: %d test length: %d\n" % (totalcomps['reflen'], totalcomps['testlen']))
    logbleu += min(0,1-float(totalcomps['reflen'])/totalcomps['testlen'])
    return math.exp(logbleu)

def score_set(tests, refss, n=4):
    alltest = []
    testslen = len(tests)
    refsslen = len(refss)
    assert testslen == refsslen
    
    for i in xrange(testslen):
        test = tests[i]
        refs = refss[i]
        refs = cook_refs(refs, n)
        alltest.append(cook_test(test, refs, n))
        
    print("%d sentences\n" % len(alltest))
    return score_cooked(alltest, n)
        

if __name__ == "__main__":

    # E.g
    e0 = '1 (15 ounce) can no-salt-added black beans'
    g0 = '1 can black beans'
    e1 = 'Heat oil in a large pot; brown chicken.'
    g1 = 'Heat oil in a pot'
    tests = [g0, g1]
    refss = [[e0], [e1]]
    score = score_set(tests, refss, 4)
    print (score)
    
