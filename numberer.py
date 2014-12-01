inputfile = 'NP_list.txt'
filenameformat = 'train_test_NP_list.txt'

def newfout(filenum):
    filename = filenameformat.replace('#',str(filenum) )
    fout=open(filename,'w')
    return fout


file = open( inputfile )
lines = file.readlines()
    
testnumber = 0
fout = open(filenameformat, 'w')

for line in lines:
    fout.write(str(testnumber) + " # "+ line)
    testnumber += 1
    if testnumber == 10:
    	testnumber = 0
        
fout.close()