import random
import time
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

charset = ["01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F","10","11","12","13","14","15","16","17","18","19","1A"]
BITSWIDTH = 5 #size of each letter in bits (here 5 because 1A = 26 = 11010 which is 5 bit long)


filterSizeRange = (100,1000)
HashFnctRange = (2,8)
wordSize = (2,16) #min and max word size
thetaSeeds = (0.6180,0.3819) #seeds for generating thetas
primingDatasetSize = 10
testDatasetSize = 1000

#Generate datasets for priming and testing
primingDataset = ["".join(random.choice(charset) for x in range(random.randint(wordSize[0],wordSize[1]))) for _ in range(primingDatasetSize)]
testDataset = []
for i in range(testDatasetSize):
    errorcounter = 0
    testData = "".join(random.choice(charset) for _ in range(random.randint(wordSize[0],wordSize[1])))
    while testData in primingDataset or testData in testDataset:
        testData =  "".join(random.choice(charset) for _ in range(random.randint(wordSize[0],wordSize[1])))
        if errorcounter > 1000:
            raise Exception("Could not create word that is not in the priming dataset")
        errorcounter += 1
    testDataset.append(testData)


#Theta generator
def generateTheta():
    return random.choice(thetaSeeds) + random.uniform(-0.02,0.02)

#Shif bits to the right with wraparound (circular)
def ror(n, k):
    return (2**BITSWIDTH-1)&(n>>(k%BITSWIDTH)|n<<((BITSWIDTH-k)%BITSWIDTH)) #based on https://www.falatic.com/index.php/108/python-and-bitwise-rotation

#Hash function with result mapped to the size of the filter
def hash(string, theta, filterSize):
    result = 0
    for i in range(int(len(string)/2)):
        result ^= ror(int("0x"+string[i*2:i*2+2],16),i+1)
    return int((((result*theta) % 1)*filterSize)//1)

def test(i):
    resultString = ""
    for j in range(HashFnctRange[0],HashFnctRange[1]+1):
        bloomFilter = [False]*i
        thetas = [generateTheta() for _ in range(j)]
        print(thetas)
        for a in primingDataset: #priming bloom filter
            for b in thetas:
                index = hash(a,b,i)
                bloomFilter[index] = True

        nbFalsePositive = 0
        for c in testDataset:
            test = True
            for d in range(j):
                index = hash(c,thetas[d],i)
                test = test and bloomFilter[index]
            if test:
                nbFalsePositive +=1 

        resultString += str(nbFalsePositive) + ", " 

    return resultString

def multiprocessing(func, args, workers):
    with ProcessPoolExecutor(workers) as ex:
        res = ex.map(func, args)
    return list(res)

print("Starting tests...")
start = time.time()
res = multiprocessing(test, range(filterSizeRange[0],filterSizeRange[1]), cpu_count())
print("Executed {} tests in {:.2f} seconds".format(len(res),time.time()-start))
print("Writting results to file")
resultFile = open("./results.csv","w")
for s in res:
    resultFile.write(s[0:-2]+"\n")
resultFile.flush()
resultFile.close()
print("Results written to ./results.csv")
