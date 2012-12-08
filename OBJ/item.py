# A dictionary assigning item ID numbers to functions which
# carry out the effects of the items

from UTIL import const
from SCRIPTS import itemScr

class Item():
    
    def __init__(self, type, num=None):
        self.type = type
        if type == const.GOLD:
            self.qty = num
            self.name = 'gold'
        if self.type == const.SPELLBOOK:
            from SCRIPTS import spellScr
            self.name = 'spellbook'
            self.spellNum = num
            self.descrip = itemScr.descDict[self.type] + ': ' + spellScr.descDict[num]
            self.ID = num + 40
        elif self.type == const.PARCHMENT:
            from SCRIPTS import spellScr
            self.name = 'parchment'
            self.spellNum = num
            self.descrip = itemScr.descDict[self.type] + ': ' + spellScr.descDict[num]
            self.ID = num + 70
        else: 
            self.name = 'item'
            self.descrip = itemScr.descDict[self.type]
            self.ID = type - const.FRUIT1
        self.img = type
    
    def getType(self):
        return self.type
    
    def getImg(self):
        return self.img
    
    def setQty(self, qty):
        self.qty = qty
    def getQty(self):
        if self.qty == 0:
            return 999
        else: return self.qty
    
    def getID(self):
        return self.ID
    
    def getName(self):
        return self.name
    def getLevel(self):
        return self.level
    def getSpellNum(self):
        return self.spellNum
    def getDesc(self):
        return self.descrip
    
    def execute(self, hero):
        if self.name == 'spellbook':
            hero.learnSpell( self.spellNum )
            return
        [cHP, mHP, cMP, mMP, sth, dex, itl, scr, kys, cEX, nEX, psn] = hero.getPlayerStats()
        stats = [cHP, mHP, cMP, mMP, sth, dex, itl, scr, kys, cEX, nEX, psn]
        fn = itemScr.itemDict[self.getType()]
        stats = fn(stats)
        [cHP, mHP, cMP, mMP, sth, dex, itl, scr, kys, cEX, nEX, psn] = stats
        hero.setPlayerStats( (cHP, mHP, cMP, mMP, sth, dex, itl, scr, kys, cEX, nEX, psn) )