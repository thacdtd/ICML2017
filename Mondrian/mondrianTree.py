import random
from Mondrian import mondrianBlock

class MondrianTree(object):
    '''
    the class used to represent a Mondrian tree
    '''

    budget = None
    rowLB = None
    rowUB = None
    columnLB = None
    columnUB = None
    root = None
    leafBlockDic = None
    leafCutDic = None
    rowCutDic = None
    columnCutDic = None
    
    def __init__(self, budget, rowLB, rowUB, columnLB, columnUB):
        self.root = mondrianBlock.MondrianBlock(budget, rowLB, rowUB, columnLB, columnUB, None, None, None, None, None)
        self.leafBlockDic = {self.root: True}
        self.leafCutDic = {}
        self.rowCutDic = {}
        self.columnCutDic = {}
        
        leafBlockLst = self.leafBlockDic.keys()
        
        cutNum = 0
        level = 0
        while len(leafBlockLst) > 0:
            level += 1
            newLeafBlockLst = []
            for leafBlock in leafBlockLst:
                
                length = leafBlock.rowUB - leafBlock.rowLB
                width = leafBlock.columnUB - leafBlock.columnLB
                cost = random.expovariate(length + width)
        #        cost = (-1/(length + width)) * math.log(random.random())
                if not cost > leafBlock.budget:
                    leftChild = None
                    rightChild = None
                    cutPos = None
                    cutDir = None
                    if random.random() < length/(length + width):
                        cutDir = 0
                    else:
                        cutDir = 1
                    if cutDir == 0:
                        cutPos = leafBlock.rowLB + random.random() * length
                        leftChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, leafBlock.rowLB, cutPos,
                                         leafBlock.columnLB, leafBlock.columnUB, None, None,
                                         None, None, leafBlock)
                        rightChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, cutPos, leafBlock.rowUB,
                                         leafBlock.columnLB, leafBlock.columnUB, None, None,
                                         None, None, leafBlock)
                    else:
                        cutPos = leafBlock.columnLB + random.random() * width
                        leftChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, leafBlock.rowLB, leafBlock.rowUB,
                                             leafBlock.columnLB, cutPos, None, None,
                                             None, None, leafBlock)
                        rightChild = mondrianBlock.MondrianBlock(leafBlock.budget-cost, leafBlock.rowLB, leafBlock.rowUB,
                                             cutPos, leafBlock.columnUB, None, None,
                                             None, None, leafBlock)
            
                    cutNum += 1
                    
                    self.addCut(leafBlock, cutDir, cutPos, leftChild, rightChild)
                    newLeafBlockLst.append(leftChild)
                    newLeafBlockLst.append(rightChild)
#                    leafBlock.setCut(cutDir, cutPos, leftChild, rightChild)
#                    if leafBlock.cutDir == 0:
#                        self.rowCutDic[cutPos] = leafBlock
#                    else:
#                        self.columnCutDic[cutPos] = leafBlock
#                    
#                    
#                    self.leafCutDic[leafBlock] = True
#                    if self.leafBlockDic.has_key(leafBlock):
#                        self.leafBlockDic.pop(leafBlock)
#                    
#                    self.leafBlockDic[leftChild] = True
#                    self.leafBlockDic[rightChild] = True
#                    
#                    if self.leafCutDic.has_key(leafBlock.getParent()):
#                        self.leafCutDic.pop(leafBlock.getParent())
                else:
                    self.leafBlockDic[leafBlock] = True
                
            leafBlockLst = newLeafBlockLst
    
#        print 'cutNum = %d, level = %d, leafNum = %d, leafCutNum = %d' % (cutNum, level, 
#                                                                          len(self.leafBlockDic), len(self.leafCutDic))
    
    def getRandomLeafBlock(self):
        leafBlock = self.leafBlockDic.keys()[random.randint(0, len(self.leafBlockDic)-1)]
        return leafBlock
    
    def getRandomLeafCut(self):
        leafCut = None
        if len(self.leafCutDic) > 0:
            leafCut = self.leafCutDic.keys()[random.randint(0, len(self.leafCutDic)-1)]
        return leafCut
    
    def addCut(self, leafBlock, cutDir, cutPos, leftChild, rightChild):
        self.leafBlockDic.pop(leafBlock)
        
        if not leftChild.isLeaf() or not rightChild.isLeaf():
            exit('this block should have two leaves as children!')
        leafBlock.setCut(cutDir, cutPos, leftChild, rightChild)
            
        self.leafBlockDic[leafBlock.leftChild] = True
        self.leafBlockDic[leafBlock.rightChild] = True
        
        if self.leafCutDic.has_key(leafBlock.getParent()):
            self.leafCutDic.pop(leafBlock.getParent())
        self.leafCutDic[leafBlock] = True
        
        if leafBlock.cutDir == 0:
            self.rowCutDic[leafBlock.cutPos] = leafBlock
        else:
            self.columnCutDic[leafBlock.cutPos] = leafBlock

    def removeLeafCut(self, leafCut):
        self.leafBlockDic.pop(leafCut.leftChild)
        self.leafBlockDic.pop(leafCut.rightChild)
        self.leafBlockDic[leafCut] = True
        
        if leafCut.getParent() is not None:
            if ((leafCut.getParent().leftChild is not None) 
                and (leafCut.getParent().rightChild is not None) 
                and leafCut.getParent().leftChild.isLeaf() 
                and leafCut.getParent().rightChild.isLeaf()):
                self.leafCutDic[leafCut.getParent()] = True
        
        if leafCut.cutDir == 0:
            self.rowCutDic.pop(leafCut.cutPos)
        else:
            self.columnCutDic.pop(leafCut.cutPos)
        
        self.leafCutDic.pop(leafCut)
        
        leafCut.removeCut()

    def getRowCutDic(self):
        return self.rowCutDic
    
    def getColumnCutDic(self):
        return self.columnCutDic
        
    def getLeafBlockDic(self):
        return self.leafBlockDic
    
    def getLeafCutDic(self):
        return self.leafCutDic
        
    def representation(self, fOutput=None):
        blockLst = [self.root]
        level = 0
#        leafCutNum = 0
        while len(blockLst) > 0:
            level += 1
            outputLine = 'Level %s:\t' % level
            newBlockLst = []
            for block in blockLst:
#                if not (block.leftChild is None) and not (block.rightChild is None) and block.leftChild.isLeaf() and block.rightChild.isLeaf():
#                    leafCutNum += 1
                if not (block.leftChild is None):
                    newBlockLst.append(block.leftChild)
                if not (block.rightChild is None):
                    newBlockLst.append(block.rightChild)
                if not (block.cutPos is None):
                    if block.cutDir == 0:
                        outputLine += ('row cut at %s from %s to %s\t' % (block.cutPos, 
                                                                      block.columnLB, block.columnUB))
                    else:
                        outputLine += ('column cut at %s from %s to %s\t' % (block.cutPos,
                                                                        block.rowLB, block.rowUB))
            if fOutput is None:
                print(outputLine)
            else:
                fOutput.write(outputLine + '\n')
            blockLst = newBlockLst
#        print leafCutNum
            
if __name__ == '__main__':
    tree = MondrianTree(1, 0, 1, 0, 1)
    tree.representation()
    leafCut = tree.getRandomLeafCut()
    if leafCut is not None:
        print(leafCut)
        print(leafCut.leftChild.isLeaf())
        print(leafCut.rightChild.isLeaf())
        print(leafCut.leftChild)
        print(leafCut.rightChild)
        tree.removeLeafCut(leafCut)
        tree.representation()
