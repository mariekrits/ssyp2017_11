import Measures

def compareWithReferences(vector, references): #references {key:[vectors], ...,key:[]]
    minMeasure = 10000000
    minKey = None
    measures = []
    for key, reference in references.items():
        sm = 0
        measures.append([key,1000000])
        for vec in reference:
            measure = Measures.EuclidianMeasure(vector, vec)#Measures.CosineMeasure(vector, vec)
            sm+= measure
            if measure < minMeasure:
                minMeasure = measure
                minKey = key
            if measure < measures[-1][1]:
                measures[-1][1] = measure
    print(measures)
    return minKey