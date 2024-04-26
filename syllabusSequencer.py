class sequencer():
    def containsAlphaLower(self,entity):
        alpha_lower = ["a.","b.","c.","d.","e.","f.","g.","h.","i.","j.","k.","l."]
        if entity.startswith(alpha_lower[self.getCount("alpha_lower")]):
            self.updateTerm(entity,"alpha_lower")
    def containsAlphaUpper(self,entity):
        alpha_upper = alpha_upper = ["A.","B.","C.","D.","E.","F.","G.","H.","I.","J.","K.","L."]
        if entity.startswith(alpha_upper[self.getCount("alpha_upper")]):
            self.updateTerm(entity,"alpha_upper")
    def containsNumLead(self,entity):
        num_lead =  ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12."]
        if entity.startswith(num_lead[self.getCount("num_lead")]):
            self.updateTerm(entity,"num_lead")
    def containsRomanLower(self,entity):
        roman_lower = ["i.", "ii.", "iii.", "iv.", "v.", "vi.", "vii.", "viii.", "ix.", "x.", "xi.", "xii."]
        if entity.startswith(roman_lower[self.getCount("roman_lower")]):
            self.updateTerm(entity,"roman_lower")
    def containsRomanUpper(self,entity):
        roman_upper =["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X.", "XI.", "XII."]
        if entity.startswith(roman_upper[self.getCount("roman_upper")]):
            self.updateTerm(entity,"roman_upper")
    def containsTermSequence(self,entity,term):
        if entity.lower().startswith(term.lower()):
            self.updateTerm(entity,term)
    def getCount(self,term):
        result = 0
        if term in self.termCounter.keys():
            result = self.termCounter[term]
        return result
    def updateTerm(self,entity,term):
        if self.getCount(term) == 0:
            self.termDict[term] ={entity: self.checkIndex(entity,term)}
            self.termCounter[term] = 1
        else:
            self.termDict[term] = self.termDict[term] | {entity: self.checkIndex(entity,term)}
            self.termCounter[term] = self.getCount(term) + 1         
    def checkIndex(self,entity,term):
        hits = [i for i in self.fullText if i.startswith(entity.strip())]
        if len(hits) >0:
            result = self.sequentialIndex(hits)
            return(result[0])
        else:
            pass
    def sequentialIndex(self, hitList):
        result =[0]
        for item in hitList:
            result.append(self.fullText.index(item, result[-1], len(self.fullText)))
        return result[1:]
    def runSequencer(self):
        for entity in self.entityList:
            self.containsAlphaLower(entity)
            self.containsAlphaUpper(entity)
            self.containsNumLead(entity)
            self.containsRomanLower(entity)
            self.containsRomanUpper(entity)
            self.containsTermSequence(entity, "week")
            self.containsTermSequence(entity, "class")
            self.containsTermSequence(entity, "session")
            self.containsTermSequence(entity, "readings")
            self.containsTermSequence(entity, "assigment")
            self.containsTermSequence(entity, "course")
            self.containsTermSequence(entity, "accomodations")
    def makeSections(self):
        linear = []
        for keyItem in self.termDict.keys():
            linear+=list(self.termDict[keyItem].items())
        linear = [i for i in linear if type(i[1])==int]
        linear.sort(key=lambda linear: linear[1])
        self.slotter(linear)
    def slotter(self, linear):
        results={}
        for slot in range(len(linear)):
            if slot == 0:
                results["Start of Document"] = self.fullText[0:linear[slot][1]]
            elif slot == len(linear)-1:
                results[linear[slot-1][0]] = self.fullText[linear[slot-1][1]:linear[slot][1]]
                results[linear[slot][0]] = self.fullText[linear[slot][1]:]
            else:
                results[linear[slot-1][0]] = self.fullText[linear[slot-1][1]:linear[slot][1]]
        self.sections=results
    def __init__(self, entityList, fullText):
        self.entityList = entityList
        self.fullText = fullText
        self.termCounter={}
        self.termDict={}
        self.runSequencer()
        self.makeSections()