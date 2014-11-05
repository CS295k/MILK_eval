from glob import glob
from JITDecoder import JITDecoder
from group_tagger import group_tagger
from sklearn.cross_validation import train_test_split

if __name__ == "__main__":
    
    data_files = glob("../annotated_recipes/*.xml")
    train_paths, test_paths = train_test_split(data_files, test_size=0.25) 

    tagger = group_tagger(train_paths, test_paths)
    jit_decoder = tagger.get_JITDecoder(0, 4, 100)

    jit_decoder.ping()
    jit_decoder.select(2)
    jit_decoder.ping()
    jit_decoder.select(1)
    jit_decoder.ping()
    jit_decoder.select(3)
    jit_decoder.ping()
                  
