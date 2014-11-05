from glob import glob
from JITDecoders import JITDecoder, JITDecoder2
from group_tagger import group_tagger
from sklearn.cross_validation import train_test_split

if __name__ == "__main__":
    
    data_files = glob("../annotated_recipes/*.xml")
    train_paths, test_paths = train_test_split(data_files, test_size=0.25) 

    tagger = group_tagger(train_paths, test_paths)
    #jit_decoder = tagger.get_JITDecoder(0, 4, 100)
    jit_decoder2 = tagger.get_JITDecoder2(0, 4)

    jit_decoder2.ping()
    jit_decoder2.select(2)
    jit_decoder2.ping()
    jit_decoder2.select(1)
    jit_decoder2.ping()
    jit_decoder2.select(3)
    jit_decoder2.ping()
                  
