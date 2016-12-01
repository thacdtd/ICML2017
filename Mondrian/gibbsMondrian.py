
import random
import math
#import util

def binarySearch(elem, sortedLst):
    lb = 0
    ub = len(sortedLst) - 1
    idx = 0
    while lb <= ub:
        idx = lb + (ub - lb)/2
        if sortedLst[idx] == elem:
            return idx
        elif sortedLst[idx] > elem:
            ub = idx - 1
            idx -= 1
        else:
            lb = idx + 1
    return idx


def findIntervalIdx(cutPos, cutLst, intervalLst):
    if cutPos == 0:
        return 0
    elif cutPos == 1:
        return len(intervalLst)-1
    else:
        cutPosIdx = binarySearch(cutPos, cutLst)
        if len(intervalLst) > 1:
            resultIdx = cutPosIdx+1
        else:
            resultIdx = cutPosIdx
        (start, end) = intervalLst[resultIdx]
        if not (start <= cutPos <= end):
            exit('Wrong interval for cut position!')
        return resultIdx


def initialLeafNodeStats(leafNodeLst, data, xi, eta, rowIntervalLeafNodeDic, columnIntervalLeafNodeDic,
                         rowCutLst, rowIntervalLst, columnCutLst, columnIntervalLst):
    countDic = dict([(leafNode, {}) for leafNode in leafNodeLst])
    sumDic = dict([(leafNode, 0) for leafNode in leafNodeLst])
    datumAssignedLeafNodeDic = {}
    rowIdxRowIntervalIdxLst = [findIntervalIdx(rowPos, rowCutLst, rowIntervalLst) for rowPos in xi]
    columnIdxColumnIntervalIdxLst = [findIntervalIdx(columnPos, columnCutLst, columnIntervalLst) for columnPos in eta]
    
    for rowIdx, rowPos in enumerate(xi):
        rowIntervalIdx = rowIdxRowIntervalIdxLst[rowIdx]
        rowIntervalRelatedLeafNodeDic = rowIntervalLeafNodeDic[rowIntervalIdx]
        datumAssignedLeafNodeDic[rowIdx] = {}
        for columnIdx, columnPos in enumerate(eta):
            datum = data[rowIdx][columnIdx]
            datumAssignedLeafNodeDic[rowIdx][columnIdx] = []
            if datum is not None:
                columnIntervalIdx = columnIdxColumnIntervalIdxLst[columnIdx]
                columnIntervalRelatedLeafNodeDic = columnIntervalLeafNodeDic[columnIntervalIdx]
                for leafNode in rowIntervalRelatedLeafNodeDic.iterkeys():
                    if columnIntervalRelatedLeafNodeDic.has_key(leafNode):
                        datumAssignedLeafNodeDic[rowIdx][columnIdx].append(leafNode)
                        if countDic.has_key(leafNode):
                            if countDic[leafNode].has_key(datum):
                                countDic[leafNode][datum] += 1
                            else:
                                countDic[leafNode][datum] = 1
                        else:
                            countDic[leafNode] = {datum:1}
                        sumDic[leafNode] += 1
                
    return [countDic, sumDic, datumAssignedLeafNodeDic, 
            rowIdxRowIntervalIdxLst, columnIdxColumnIntervalIdxLst]
        
def sampleFromDiscreteDist(distDic):
    cdf = []
    sum = 0.0
    idx = 0
    selectedKey = None
    urv = random.random()
    for key, prob in distDic.iteritems():
        sum += prob
        cdf.append((key, sum))
    for i in range(0, len(cdf)):
        prob = cdf[i][1] / sum
        if prob > urv:
            idx = i
            selectedKey = cdf[i][0]
            break
    return selectedKey

def gibbsOneDimensionStep(beta, dimension, data1, leafNodeLst, idx,
                          intervalLst, intervalLeafNodeDic, 
                          otherIdxOtherIntervalIdxLst, #otherIntervalLeafNodeDic,
                          rowIntervalColumnIntervalLeafNodeDic, countDic, sumDic, isRow):
    logLikelihoodDic = {}
    maxLogLikelihood = None
#    logLikelihoodDic2 = {}
#    maxLogLikelihood2 = None
    data = dict(enumerate(data1))
    #print(data)
    if isRow:
        #otherIdxDataDic = data[idx]
        otherIdxDataDic = dict(enumerate(data[idx]))
    else:
        otherIdxDataDic = dict([(rowIdx, data[rowIdx][idx]) for rowIdx in data.iterkeys()])

    #print(otherIdxDataDic)

#    print '# of %s intervals: %s' % (isRow, len(intervalLeafNodeDic))
    for intervalIdx in range(0, len(intervalLst)):
        tmpSumDic = {}
        tmpCountDic = {}
        tmpLeafNodeDic = {}
        for otherIdx, datum in otherIdxDataDic.iteritems():
            if datum is not None:
                otherIntervalIdx = otherIdxOtherIntervalIdxLst[otherIdx]
#                otherIdxRelatedLeafNodeDic = otherIntervalLeafNodeDic[otherIntervalIdx]
#                for leafNode in intervalLeafNodeDic[intervalIdx].iterkeys():
#                    if otherIdxRelatedLeafNodeDic.has_key(leafNode):
                if isRow:
                    rowIntervalIdx = intervalIdx
                    columnIntervalIdx = otherIntervalIdx
                else:
                    rowIntervalIdx = otherIntervalIdx
                    columnIntervalIdx = intervalIdx
                leafNode = rowIntervalColumnIntervalLeafNodeDic[rowIntervalIdx][columnIntervalIdx][0]
                tmpLeafNodeDic[leafNode] = None
                if tmpSumDic.has_key(leafNode):
                    tmpSumDic[leafNode] += 1
                else:
                    tmpSumDic[leafNode] = sumDic[leafNode] + 1
                if tmpCountDic.has_key(leafNode):
                    if tmpCountDic[leafNode].has_key(datum):
                        tmpCountDic[leafNode][datum] += 1
                    else:
                        tmpCountDic[leafNode][datum] = 1
                else:
                    tmpCountDic[leafNode] = {}
                    for otherDatum, count in countDic[leafNode].iteritems():
                        tmpCountDic[leafNode][otherDatum] = count
                    if tmpCountDic[leafNode].has_key(datum):
                        tmpCountDic[leafNode][datum] += 1
                    else:
                        tmpCountDic[leafNode][datum] = 1
        
        tmpLogLikelihood = 0
        for leafNode in tmpLeafNodeDic:
#            if not intervalLeafNodeDic[intervalIdx].has_key(leafNode):
#                exit('Different affected lead nodes!')
            for datum, newCount in tmpCountDic[leafNode].iteritems():
                oldCount = 0
                if countDic[leafNode].has_key(datum):
                    oldCount = countDic[leafNode][datum]
                start = oldCount
#                if start < 0:
#                    exit('Error entry valude count in leaf node!')
                end = newCount
                for item in range(start, end):
                    tmpLogLikelihood += math.log(beta + item)
            newSum = tmpSumDic[leafNode]
            oldSum = sumDic[leafNode]
            start = oldSum
#            if start < 0:
#                exit('Error entry count in leaf node!')
            end = newSum
            for item in range(start, end):
                tmpLogLikelihood += (-1 * math.log(beta + item))
            
        logLikelihoodDic[intervalIdx] = tmpLogLikelihood
        if maxLogLikelihood is None:
            maxLogLikelihood = tmpLogLikelihood
        elif tmpLogLikelihood > maxLogLikelihood:
            maxLogLikelihood = tmpLogLikelihood
            
#        tmpLogLikelihood = 0
#        for leafNode in leafNodeLst: 
#            if not tmpSumDic.has_key(leafNode):
#                entryNum = sumDic[leafNode]
#                for datum, count in countDic[leafNode].iteritems():
#                    tmpLogLikelihood += util.lgamma(beta + count)
#                tmpLogLikelihood += (dimension - len(countDic[leafNode])) * util.lgamma(beta)
#                tmpLogLikelihood -= util.lgamma(dimension * beta + entryNum)
#            else:
#                entryNum = tmpSumDic[leafNode]
#                for datum, count in tmpCountDic[leafNode].iteritems():
#                    tmpLogLikelihood += util.lgamma(beta + count)
#                tmpLogLikelihood += (dimension - len(tmpCountDic[leafNode])) * util.lgamma(beta)
#                tmpLogLikelihood -= util.lgamma(dimension * beta + entryNum)
#                
#        logLikelihoodDic2[intervalIdx] = tmpLogLikelihood
#        if maxLogLikelihood2 is None:
#            maxLogLikelihood2 = tmpLogLikelihood
#        elif tmpLogLikelihood > maxLogLikelihood2:
#            maxLogLikelihood2 = tmpLogLikelihood
      
    sum = 0.0
    distDic = {}
    for intervalIdx, logLikelihood in logLikelihoodDic.iteritems():
        (start, end) = intervalLst[intervalIdx]
        distDic[intervalIdx] = (end - start) * math.exp(logLikelihood - maxLogLikelihood)
        sum += distDic[intervalIdx]
        
#    sum2 = 0.0
#    distDic2 = {}
#    for intervalIdx, logLikelihood in logLikelihoodDic2.iteritems():
#        (start, end) = intervalLst[intervalIdx]
#        distDic2[intervalIdx] = (end - start) * math.exp(logLikelihood - maxLogLikelihood2)
#        sum2 += distDic2[intervalIdx]
#        
#    for intervalIdx, probability in distDic2.iteritems():
#        prob2 = probability / sum2
#        prob = distDic[intervalIdx] / sum
#        if math.fabs(prob2 - prob) > 1.0e-4:
#            print prob, prob2
#            exit( 'Error Conditional Distribution in Gibbs Sampling!' )
    return sampleFromDiscreteDist(distDic)

def Gibbs(beta, dimension, data, xi, eta, root, maxGibbsIteration = 300, isPreGibbsLikelihood=True):
    leafBlockLst = root.getLeafBlockDic().keys()
    rowCutLst = root.getRowCutDic().keys()
    columnCutLst = root.getColumnCutDic().keys()
    print('# of row cuts: %s, # of column cuts: %s' % (len(rowCutLst), len(columnCutLst)))
    rowCutLst.sort()
    columnCutLst.sort()
    rowIntervalLst = [(0,1)]
    if len(rowCutLst) > 0:
        rowIntervalLst = [(0,rowCutLst[0])] + [(rowCutLst[idx], rowCutLst[idx+1]) 
                          for idx in range(0, len(rowCutLst)-1)] + [(rowCutLst[-1],1)]
    columnIntervalLst = [(0,1)]
    if len(columnCutLst) > 0:
        columnIntervalLst = [(0,columnCutLst[0])] + [(columnCutLst[idx], columnCutLst[idx+1])
                             for idx in range(0, len(columnCutLst)-1)] + [(columnCutLst[-1],1)]
    
    # find out row (column) intervals that overlapped with each leaf block
    rowIntervalLeafNodeDic = {}
    columnIntervalLeafNodeDic = {}
    for leafNode in leafBlockLst:
        rowLBIdx = findIntervalIdx(leafNode.rowLB, rowCutLst, rowIntervalLst)
        rowUBIdx = findIntervalIdx(leafNode.rowUB, rowCutLst, rowIntervalLst)
        for rowIntervalIdx in range(rowLBIdx, rowUBIdx+1):
            (start, end) = rowIntervalLst[rowIntervalIdx] 
            if leafNode.rowLB <= start and leafNode.rowUB >= end:
                if rowIntervalLeafNodeDic.has_key(rowIntervalIdx):
                    rowIntervalLeafNodeDic[rowIntervalIdx][leafNode] = 0
                else:
                    rowIntervalLeafNodeDic[rowIntervalIdx] = {leafNode:0}
        
        columnLBIdx = findIntervalIdx(leafNode.columnLB, columnCutLst, columnIntervalLst)
        columnUBIdx = findIntervalIdx(leafNode.columnUB, columnCutLst, columnIntervalLst)
        for columnIntervalIdx in range(columnLBIdx, columnUBIdx+1):
            (start, end) = columnIntervalLst[columnIntervalIdx]
            if leafNode.columnLB <= start and leafNode.columnUB >= end:
                if columnIntervalLeafNodeDic.has_key(columnIntervalIdx):
                    columnIntervalLeafNodeDic[columnIntervalIdx][leafNode] = 0
                else:
                    columnIntervalLeafNodeDic[columnIntervalIdx] = {leafNode:0}
    
    rowIntervalColumnIntervalLeafNodeDic = {}
    for rowIntervalIdx in range(0, len(rowIntervalLst)):
        rowIntervalColumnIntervalLeafNodeDic[rowIntervalIdx] = {}
        for columnIntervalIdx in range(0, len(columnIntervalLst)):
            tmpLst = []
            for leafNode in rowIntervalLeafNodeDic[rowIntervalIdx].iterkeys():
                if columnIntervalLeafNodeDic[columnIntervalIdx].has_key(leafNode):
                    tmpLst.append(leafNode)
            if len(tmpLst) > 1:
                exit('There should be only one leaf block!')
            else:
                leafNode = tmpLst[0]
            rowIntervalColumnIntervalLeafNodeDic[rowIntervalIdx][columnIntervalIdx] = tmpLst
    
    [countDic, sumDic, datumAssignedLeafNodeDic, rowIdxRowIntervalIdxLst, 
     columnIdxColumnIntervalIdxLst] = initialLeafNodeStats(leafBlockLst, data, xi, eta, 
                         rowIntervalLeafNodeDic, columnIntervalLeafNodeDic,
                         rowCutLst, rowIntervalLst, columnCutLst, columnIntervalLst)
    
    if isPreGibbsLikelihood:
        preGibbsLogLikelihood = 0
        for leafNode in leafBlockLst:
            entryNum = sumDic[leafNode]
            if entryNum > 0:
                preGibbsLogLikelihood += (math.lgamma(dimension * beta) - dimension * math.lgamma(beta))
                for datum, count in countDic[leafNode].iteritems():
                    preGibbsLogLikelihood += math.lgamma(beta + count)
    #            if len(countDic[leafNode]) > dimension:
    #                exit('Impossible entry value count!')
                preGibbsLogLikelihood += (dimension - len(countDic[leafNode])) * math.lgamma(beta)
                preGibbsLogLikelihood -= math.lgamma(dimension * beta + entryNum)
        logLikelihood = preGibbsLogLikelihood
            
    for itr in range(0, maxGibbsIteration):
        # sample for rows
        for rowIdx, rowPos in enumerate(xi):
            for columnIdx, columnPos in enumerate(eta):
                datum = data[rowIdx][columnIdx]
                if datum is not None:
                    leafNodes = datumAssignedLeafNodeDic[rowIdx][columnIdx]
                    if len(leafNodes) > 1:
                        exit('One datum can only belong to one leaf block!')
                    else:
                        leafNode = leafNodes[0]
                        countDic[leafNode][datum] -= 1
                        sumDic[leafNode] -= 1
            newRowIntervalIdx = gibbsOneDimensionStep(beta, dimension, data, leafBlockLst, rowIdx, 
                                                      rowIntervalLst, rowIntervalLeafNodeDic,
                                                      columnIdxColumnIntervalIdxLst,
                                                      rowIntervalColumnIntervalLeafNodeDic,
                                                      countDic, sumDic, True)
            rowIdxRowIntervalIdxLst[rowIdx] = newRowIntervalIdx
#            rowIntervalRelatedLeafNodeDic = rowIntervalLeafNodeDic[newRowIntervalIdx]
            (start, end) = rowIntervalLst[newRowIntervalIdx]
            newRowPos = start + (end - start) * random.random()
            xi[rowIdx] = newRowPos
            for columnIdx, columnPos in enumerate(eta):
                columnIntervalIdx = columnIdxColumnIntervalIdxLst[columnIdx]
#                columnIntervalRelatedLeafNodeDic = columnIntervalLeafNodeDic[columnIntervalIdx]
                datum = data[rowIdx][columnIdx]
                datumAssignedLeafNodeDic[rowIdx][columnIdx] = rowIntervalColumnIntervalLeafNodeDic[newRowIntervalIdx][columnIntervalIdx]
                if datum is not None:
#                    for leafNode in datumAssignedLeafNodeDic[rowIdx][columnIdx]:
#                        if columnIntervalRelatedLeafNodeDic.has_key(leafNode):
#                            datumAssignedLeafNodeDic[rowIdx][columnIdx].append(leafNode)
                            leafNode = datumAssignedLeafNodeDic[rowIdx][columnIdx][0]
                            if countDic.has_key(leafNode):
                                if countDic[leafNode].has_key(datum):
                                    countDic[leafNode][datum] += 1
                                else:
                                    countDic[leafNode][datum] = 1
                            else:
                                countDic[leafNode] = {datum:1}
                            if sumDic.has_key(leafNode):
                                sumDic[leafNode] += 1
                            else:
                                sumDic[leafNode] = 1
        # sample for columns
        for columnIdx, columnPos in enumerate(eta):
            for rowIdx, rowPos in enumerate(xi):
                datum = data[rowIdx][columnIdx]
                if datum is not None:
                    leafNodes = datumAssignedLeafNodeDic[rowIdx][columnIdx]
                    if len(leafNodes) > 1:
                        exit('One datum can only belong to one leaf block!')
                    else:
                        leafNode = leafNodes[0]
                        countDic[leafNode][datum] -= 1
                        sumDic[leafNode] -= 1
            newColumnIntervalIdx = gibbsOneDimensionStep(beta, dimension, data, leafBlockLst, columnIdx, 
                                                         columnIntervalLst, columnIntervalLeafNodeDic,
                                                         rowIdxRowIntervalIdxLst,
                                                         rowIntervalColumnIntervalLeafNodeDic,
                                                         countDic, sumDic, False)
            columnIdxColumnIntervalIdxLst[columnIdx] = newColumnIntervalIdx
#            columnIntervalRelatedLeafNodeDic = columnIntervalLeafNodeDic[newColumnIntervalIdx]
            (start, end) = columnIntervalLst[newColumnIntervalIdx]
            newColumnPos = start + (end - start) * random.random()
            eta[columnIdx] = newColumnPos
            for rowIdx, rowPos in enumerate(xi):
                rowIntervalIdx = rowIdxRowIntervalIdxLst[rowIdx]
#                rowIntervalRelatedLeafNodeDic = rowIntervalLeafNodeDic[rowIntervalIdx]
                datum = data[rowIdx][columnIdx]
                datumAssignedLeafNodeDic[rowIdx][columnIdx] = rowIntervalColumnIntervalLeafNodeDic[rowIntervalIdx][newColumnIntervalIdx]
                if datum is not None:
#                    for leafNode in rowIntervalRelatedLeafNodeDic:
#                        if columnIntervalRelatedLeafNodeDic.has_key(leafNode):
#                            datumAssignedLeafNodeDic[rowIdx][columnIdx].append(leafNode)
                            leafNode = datumAssignedLeafNodeDic[rowIdx][columnIdx][0]
                            if countDic.has_key(leafNode):
                                if countDic[leafNode].has_key(datum):
                                    countDic[leafNode][datum] += 1
                                else:
                                    countDic[leafNode][datum] = 1
                            else:
                                countDic[leafNode] = {datum:1}
                            if sumDic.has_key(leafNode):
                                sumDic[leafNode] += 1
                            else:
                                sumDic[leafNode] = 1
                            
    if not isPreGibbsLikelihood:
        postGibbsLogLikelihood = 0
        for leafNode in leafBlockLst:
            entryNum = sumDic[leafNode]
            if entryNum > 0:
                postGibbsLogLikelihood += (math.lgamma(dimension * beta) - dimension * math.lgamma(beta))
                for datum, count in countDic[leafNode].iteritems():
                    postGibbsLogLikelihood += math.lgamma(beta + count)
    #            if len(countDic[leafNode]) > dimension:
    #                exit('Impossible entry value count!')
                postGibbsLogLikelihood += (dimension - len(countDic[leafNode])) * math.lgamma(beta)
                postGibbsLogLikelihood -= math.lgamma(dimension * beta + entryNum)
        logLikelihood = postGibbsLogLikelihood
            
    return [xi, eta, logLikelihood, data]