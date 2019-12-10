# -*- coding: utf-8 -*-
from transition import *
from state import *
import os
import copy
from sp import *
from parser import *
from itertools import product
from automateBase import AutomateBase


#TEST DE MODIF D'UN FICHIER ...

class Automate(AutomateBase):
        
    def succElem(self, state, lettre):
        """State x str -> list[State]
        rend la liste des états accessibles à partir d'un état
        state par l'étiquette lettre
        """
        successeurs = []
        # t: Transitions
        for t in self.getListTransitionsFrom(state):
            if t.etiquette == lettre and t.stateDest not in successeurs:
                successeurs.append(t.stateDest)
        return successeurs


    def succ(self, listStates, lettre):
        """list[State] x str -> list[State]
        rend la liste des états accessibles à partir de la liste d'états
        listStates par l'étiquette lettre
        """
        successeurs = []
        # # s: Etats
        for state in listStates:
            for t in self.getListTransitionsFrom(state):
                if t.etiquette == lettre and t.stateDest not in successeurs:
                    successeurs.append(t.stateDest)
        return successeurs



    """ Définition d'une fonction déterminant si un mot est accepté par un automate.
    Exemple :
            a=Automate.creationAutomate("monAutomate.txt")
            if Automate.accepte(a,"abc"):
                print "L'automate accepte le mot abc"
            else:
                print "L'automate n'accepte pas le mot abc"
    """
    @staticmethod
    def accepte(auto,mot) :
        """ Automate x str -> bool
        rend True si auto accepte mot, False sinon
        """        
        res = auto.getListInitialStates()

        for l in mot:
            res = auto.succ(res, l)

        return State.isFinalIn(res)

    @staticmethod
    def estComplet(auto,alphabet) :
        """ Automate x str -> bool
         rend True si auto est complet pour alphabet, False sinon
        """
        for state in auto.listStates:
            for a in alphabet:
                if auto.succElem(state, a) == []:
                    return False
        return True


    @staticmethod
    def estDeterministe(auto) :
        """ Automate  -> bool
        rend True si auto est déterministe, False sinon
        """
        alphabet = auto.getAlphabetFromTransitions()
        for a in alphabet:
            for state in auto.listStates:
                if len(auto.succElem(state,a)) > 1:
                    return False
        return True
        

       
    @staticmethod
    def completeAutomate(auto,alphabet) :
        """ Automate x str -> Automate
        rend l'automate complété d'auto, par rapport à alphabet
        """
        autocopy = copy.deepcopy(auto)
        puitId = 0
        for state in auto.listStates:
            if puitId <= state.id:
                puitId = state.id + 1

        puit = State(puitId, False, False, "puit")
        autocopy.addState(puit)

        for state in autocopy.listStates:
            for a in alphabet:
                if autocopy.succElem(state, a) == []:
                    t = Transition(state, a, puit)
                    autocopy.addTransition(t)
            
        return autocopy



    @staticmethod
    def determinisation(auto) :
        """ Automate  -> Automate
        rend l'automate déterminisé d'auto
        """
        alphabet = auto.getAlphabetFromTransitions()

        etatsInit = set(auto.getListInitialStates())
        etatsATraiter = [ etatsInit ]
        dejaTraites = []

        listeEtats = [ State(0, True, State.isFinalIn(etatsInit), str(etatsInit)) ]
        listeTrans = []

        while etatsATraiter != []:
            setSrc = etatsATraiter.pop()
            dejaTraites.append(setSrc)
            for etat in listeEtats:
                if str(etat.label) == str(setSrc):
                    idSrc = listeEtats.index(etat)

            for lettre in alphabet:
                isIn = False
                setDst = set(auto.succ(setSrc, lettre))
                if setDst != set():
                    if setDst not in dejaTraites:
                        etatsATraiter.append(setDst)

                    for etat in listeEtats:
                        if str(etat.label) == str(setDst):
                            isIn = True
                            listeTrans.append(Transition(listeEtats[idSrc], lettre, listeEtats[listeEtats.index(etat)]))

                    if not isIn:
                        listeEtats.append(State(len(listeEtats), False, State.isFinalIn(setDst), str(setDst)))
                        listeTrans.append(Transition(listeEtats[idSrc], lettre, listeEtats[-1]))

        return Automate(listeTrans)


    @staticmethod
    def complementaire(auto,alphabet):
        """ Automate -> Automate
        rend  l'automate acceptant pour langage le complémentaire du langage de a
        """
        autoComplementaire = Automate.completeAutomate(Automate.determinisation(auto),alphabet)
        for state in autoComplementaire.listStates:
            state.fin = not state.fin

        return autoComplementaire
     

    @staticmethod
    def intersection (auto0, auto1):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """
        inits = list(product(auto0.getListInitialStates(), auto1.getListInitialStates()))
        finals = list(product(auto0.getListFinalStates(), auto1.getListFinalStates()))

        cpt = 0
        cptToTuple = inits
        Ss = []
        Ts = []
        for cpt in range(0, len(inits)):
            Ss.append(State(cpt, True, inits[cpt] in finals, inits[cpt]))


        print(cptToTuple, cptToTuple[0], cptToTuple[0][0], cptToTuple[0][1])
        print(auto0.getListTransitionsFrom(cptToTuple[0][0])[0])

        cpt = 0
        for S in Ss:
            tempLeft = [(t.etiquette, t.stateDest) for t in auto0.getListTransitionsFrom(cptToTuple[cpt][0])]
            tempRight = [(t.etiquette, t.stateDest) for t in auto1.getListTransitionsFrom(cptToTuple[cpt][1])]

            tempDLeft = dict()
            tempDRight = dict()
            for (k, v) in tempLeft:
                if k not in tempDLeft:
                    tempDLeft[k] = {v}
                else:
                    tempDLeft[k].add(v)
            for (k, v) in tempRight:
                if k not in tempDRight:
                    tempDRight[k] = {v}
                else:
                    tempDRight[k].add(v)
            print(tempDLeft, tempDRight)
            for (k, v) in tempDLeft.items():
                if k not in tempDRight: continue
                prod = list(product(list(v), list(tempDRight[k])))
                #print(prod)
                for label in prod:
                    if label not in cptToTuple:
                        cptToTuple.append(label)
                        Ss.append(State(len(Ss), False, label in finals, label))
                        Ts.append(Transition(S, k, Ss[-1]))
                    else:
                        Ts.append(Transition(S, k, Ss[cptToTuple.index(label)]))
            cpt += 1

        return Automate(Ts)


    @staticmethod
    def etoile (auto):
        """ Automate  -> Automate
        rend l'automate acceptant pour langage l'étoile du langage de a
        """
        autoEtoile = Automate.concatenation(auto, auto)
        autoEtoile.addState(State(len(autoEtoile.listStates) + 1, True, True, "Eps"))
        return autoEtoile


