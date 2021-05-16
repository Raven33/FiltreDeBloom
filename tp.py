#DELON ARTHUR, BOUIN ANTOINE
import random
import time

filterSizeRange = (100,1000)
HashFnctRange = (2,8)
thetaSeeds = (0.6180,0.3819) #seeds for generating thetas
primingDatasetSize = 1000
testDatasetSize = 1000

primingDataset = [random.randint(0,9999999999) for _ in range(primingDatasetSize)]
testDataset = []
for i in range(testDatasetSize):
    errorcounter = 0
    testData = random.randint(0,9999999999)
    while testData in primingDataset or testData in testDataset:
        testData =  random.randint(0,9999999999)
        if errorcounter > 1000:
            raise Exception("Could not create word that is not in the priming dataset")
        errorcounter += 1
    testDataset.append(testData)


#Theta generator
def generateTheta():
    return random.choice(thetaSeeds) + random.uniform(-0.02,0.02)

def hash(e, theta, filterSize):
    return int((((e*theta) % 1)*filterSize)//1)

def test():
    res = []
    for N in range(filterSizeRange[0],filterSizeRange[1]):
        resultString = ""
        for j in range(HashFnctRange[0],HashFnctRange[1]+1):
            bloomFilter = [False]*N
            thetas = [generateTheta() for _ in range(j)]
            for a in primingDataset: #priming bloom filter
                for b in thetas:
                    index = hash(a,b,N)
                    bloomFilter[index] = True

            nbFalsePositive = 0
            for c in testDataset:
                test = True
                for d in range(j):
                    index = hash(c,thetas[d],N)
                    test = test and bloomFilter[index]
                if test:
                    nbFalsePositive +=1 

            resultString += str(nbFalsePositive/testDatasetSize) + ", "
        res.append(resultString)
    return res

print("Starting tests...")
start = time.time()
res = test()
print("Executed {} tests in {:.2f} seconds".format(len(res),time.time()-start))
print("Writting results to file")
resultFile = open("./results.csv","w")
for s in res:
    resultFile.write(s[0:-2]+"\n")
resultFile.flush()
resultFile.close()
print("Results written to ./results.csv")
