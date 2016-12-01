'''
Created on Oct 29, 2010

@author: nicolas
'''

import time
import random
import math
from Mondrian import gibbsMondrian
from Mondrian import loadData
from Mondrian import mondrianTree
from Mondrian import mondrianBlock

def rjmcmc(maxIteration = 2000, likelihoodFileName=None, partitionFileName=None,
           acceptActionFileName = None, representationFileName=None):
     
    #[data, beta, dimension] = loadData.syntheticData()
    data = loadData.load_data("../data/Synthetic/synthetic1.txt")
    dimension = 2
    beta = 0.1

    maxGibbsIteration = 5
    tree = mondrianTree.MondrianTree(1, 0, 1, 0, 1)
    xi = [random.random() for item in data]
    eta = [random.random() for item in data[0] if len(data) > 0]
    [xi, eta, logLikelihood, data2] = gibbsMondrian.Gibbs(beta, dimension, data, xi, eta, tree, maxGibbsIteration)
    
    acceptedNum = 0
    if likelihoodFileName is None:
        likelihoodFileName = 'RJMCMC.txt'
    if representationFileName is None:
        representationFileName = 'Representation.txt'
    fLogLikelihood = open(likelihoodFileName, 'w')
    fRepresentation = open(representationFileName, 'w')
    startTime = time.time()
    
    for itr in range(0, maxIteration):
        print('iteration: %d' % itr)
        if random.randint(0, 1) == 0: # add cut
            print('try to add cut')
            leafBlock = tree.getRandomLeafBlock()

            length = leafBlock.rowUB - leafBlock.rowLB
            width = leafBlock.columnUB - leafBlock.columnLB
            cost = random.expovariate(length + width)
            if cost > leafBlock.budget:
                print('no enough budget, cost: %s, budget: %s' % (cost, leafBlock.budget))
            else:
                leftChild = None
                rightChild = None
                cutPos = None
                cutDir = None
                if random.random() < length/(length + width):
                    cutDir = 0
                    print('try to add row cut')
                else:
                    cutDir = 1
                    print('try to add column cut')
                if cutDir == 0:
                    intervalLength = length
                    cutPos = leafBlock.rowLB + random.random() * length
                    leftChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, leafBlock.rowLB, cutPos,
                                     leafBlock.columnLB, leafBlock.columnUB, None, None,
                                     None, None, leafBlock)
                    rightChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, cutPos, leafBlock.rowUB,
                                     leafBlock.columnLB, leafBlock.columnUB, None, None,
                                     None, None, leafBlock)
                else:
                    intervalLength = width
                    cutPos = leafBlock.columnLB + random.random() * width
                    leftChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, 
                                                  leafBlock.rowLB, leafBlock.rowUB,
                                         leafBlock.columnLB, cutPos, None, None,
                                         None, None, leafBlock)
                    rightChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, 
                                                   leafBlock.rowLB, leafBlock.rowUB,
                                         cutPos, leafBlock.columnUB, None, None,
                                         None, None, leafBlock) 
                    
                leafBlockLogLikelihood = leafBlock.computeLogLikelihood(data, xi, eta, beta, dimension)
                leftChildLogLikelihood = leftChild.computeLogLikelihood(data, xi, eta, beta, dimension)
                rightChildLogLikelihood = rightChild.computeLogLikelihood(data, xi, eta, beta, dimension)
                
                likelihoodRatio = math.exp(leftChildLogLikelihood + 
                                           rightChildLogLikelihood - 
                                           leafBlockLogLikelihood)
                
                proposalRatio = (len(tree.getLeafBlockDic())/(len(tree.getLeafCutDic())+1.0))
                if tree.getLeafCutDic().has_key(leafBlock.getParent()):
                    proposalRatio = (len(tree.getLeafBlockDic())/len(tree.getLeafCutDic()))
                    
                leafBlockHalfPerimeter = (leafBlock.rowUB - leafBlock.rowLB + 
                                          leafBlock.columnUB - leafBlock.columnLB)
                leftChildHalfPerimeter = (leftChild.rowUB - leftChild.rowLB + 
                                          leftChild.columnUB - leftChild.columnLB)
                rightChildHalfPerimeter = (rightChild.rowUB - rightChild.rowLB + 
                                          rightChild.columnUB - rightChild.columnLB)
                priorRatio = ((math.exp(-1 * leftChildHalfPerimeter * 
                                            leftChild.budget) * 
                                   math.exp(-1 * rightChildHalfPerimeter * 
                                            rightChild.budget)) /
                                (math.exp(-1 * leafBlockHalfPerimeter * leafBlock.budget) ) )
                
                acceptRatio = priorRatio * proposalRatio * likelihoodRatio
                print('prior ratio: %s, proposal ratio: %s, likelihood ratio: %s' % (priorRatio, proposalRatio, likelihoodRatio))
                print('add ratio: %s' % acceptRatio)
                
                if (acceptRatio >= random.random()): # accept adding a cut
                    print('add cut accepted!')
                    acceptedNum += 1
                    
                    tree.addCut(leafBlock, cutDir, cutPos, leftChild, rightChild)
        else: # remove cut
            print('try to remove a cut')
            leafCut = tree.getRandomLeafCut()
            if leafCut is not None:
                leafCutLogLikelihood = leafCut.computeLogLikelihood(data, xi, eta, beta, dimension)
                leftChildLogLikelihood = leafCut.leftChild.computeLogLikelihood(data, 
                                                                               xi, eta, beta, dimension)
                rightChildLogLikelihood = leafCut.rightChild.computeLogLikelihood(data, 
                                                                               xi, eta, beta, dimension)
                likelihoodRatio = math.exp(leafCutLogLikelihood - leftChildLogLikelihood - 
                                           rightChildLogLikelihood)
                
                proposalRatio = len(tree.getLeafBlockDic()) / (len(tree.getLeafBlockDic())-1.0)
                
                if leafCut.cutDir == 0:
                    print('try to remove a row cut')
                    intervalLength = leafCut.rowUB - leafCut.rowLB
                else:
                    print('try to remove a column cut')
                    intervalLength = leafCut.columnUB - leafCut.columnLB
                
                leafCutHalfPerimeter = (leafCut.rowUB - leafCut.rowLB + 
                                          leafCut.columnUB - leafCut.columnLB)
                leftChildHalfPerimeter = (leafCut.leftChild.rowUB - leafCut.leftChild.rowLB + 
                                          leafCut.leftChild.columnUB - leafCut.leftChild.columnLB)
                rightChildHalfPerimeter = (leafCut.rightChild.rowUB - leafCut.rightChild.rowLB + 
                                          leafCut.rightChild.columnUB - leafCut.rightChild.columnLB)
                priorRatio = (math.exp(-1 * leafCutHalfPerimeter * leafCut.budget) /
                                  (math.exp(-1 * leftChildHalfPerimeter * 
                                            leafCut.leftChild.budget) * 
                                   math.exp(-1 * rightChildHalfPerimeter * 
                                            leafCut.rightChild.budget)) )
                
                acceptRatio = priorRatio * proposalRatio * likelihoodRatio
                print('prior ratio: %s, proposal ratio: %s, likelihood ratio: %s' % (priorRatio, proposalRatio, likelihoodRatio))
                print('remove ratio: %s' % acceptRatio)
                
                if (acceptRatio >= random.random()): # accept removing a leaf cut
                    print('remove cut accepted!')
                    acceptedNum += 1
                    
                    tree.removeLeafCut(leafCut)
                        
        [xi, eta, logLikelihood, data2] = gibbsMondrian.Gibbs(beta, dimension,
                                               data, xi, eta, tree, 
                                               maxGibbsIteration, False)
        print('log-likelihood: %s' % logLikelihood)
        fLogLikelihood.write('%s\n' % logLikelihood)
        fRepresentation.write('Iteration: %d\n' % itr)
        tree.representation(fRepresentation)
        fRepresentation.write('%s\n' % xi)
        fRepresentation.write('%s\n' % eta)
        if itr % 10 == 0:
            fLogLikelihood.flush()
            fRepresentation.flush()
        
    print('Running Time: %s' % (time.time() - startTime))
    fLogLikelihood.close()
    fRepresentation.close()

    print('accept ratio: %s' % (1.0 * acceptedNum / maxIteration))
    print(data2)

def load():
    data = loadData.load_data("../data/Synthetic/synthetic1.txt")
    print(data)

if __name__ == '__main__':
    rjmcmc()
    #load()
