from unittest import TestCase

from core.composition import Component
from core.exception import ChemicalFormulaParserException


class TestChemicalParser(TestCase):

    def testValidParse(self):

        formula = "H2O"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 2)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

    def testInvalidParse(self):

        formula = "h2o"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

    def testD2OParse(self):

        formula = "D2O"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 2)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 2)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

    def testHardParse(self):

        formula = "H2ONaCl9D2OK"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 7)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

        self.assertEqual(component.elements[2].atomicSymbol, "Na")
        self.assertEqual(component.elements[2].massNo, 0)
        self.assertEqual(component.elements[2].abundance, 1.0)

        self.assertEqual(component.elements[3].atomicSymbol, "Cl")
        self.assertEqual(component.elements[3].massNo, 0)
        self.assertEqual(component.elements[3].abundance, 9.0)

        self.assertEqual(component.elements[4].atomicSymbol, "H")
        self.assertEqual(component.elements[4].massNo, 2.0)
        self.assertEqual(component.elements[4].abundance, 2.0)

        self.assertEqual(component.elements[5].atomicSymbol, "O")
        self.assertEqual(component.elements[5].massNo, 0)
        self.assertEqual(component.elements[5].abundance, 1.0)

        self.assertEqual(component.elements[6].atomicSymbol, "K")
        self.assertEqual(component.elements[6].massNo, 0)
        self.assertEqual(component.elements[6].abundance, 1.0)

    def testParseDecimalAbundance(self):

        formula = "H1.0K1.0Ar33.0Au26.5"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 4)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 1.0)

        self.assertEqual(component.elements[1].atomicSymbol, "K")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

        self.assertEqual(component.elements[2].atomicSymbol, "Ar")
        self.assertEqual(component.elements[2].massNo, 0)
        self.assertEqual(component.elements[2].abundance, 33.0)

        self.assertEqual(component.elements[3].atomicSymbol, "Au")
        self.assertEqual(component.elements[3].massNo, 0)
        self.assertEqual(component.elements[3].abundance, 26.5)

    def testInvalidParse2(self):

        formula = "H2O1./"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

    def testInvalidElements(self):

        formula = "Ng12KThPa"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

        formula = "OgTsLvNoRk"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

        formula = "NdPmZkNeMk"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

    def testParseBasicIsotope(self):

        formula = "H[3]"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 1)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 3)
        self.assertEqual(component.elements[0].abundance, 1.0)

    def testParseDifficultIsotopes(self):

        formula = "H[3]12.0C[13]6.5U[235]K[39]9.1"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 4)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 3)
        self.assertEqual(component.elements[0].abundance, 12.0)

        self.assertEqual(component.elements[1].atomicSymbol, "C")
        self.assertEqual(component.elements[1].massNo, 13)
        self.assertEqual(component.elements[1].abundance, 6.5)

        self.assertEqual(component.elements[2].atomicSymbol, "U")
        self.assertEqual(component.elements[2].massNo, 235)
        self.assertEqual(component.elements[2].abundance, 1.0)

        self.assertEqual(component.elements[3].atomicSymbol, "K")
        self.assertEqual(component.elements[3].massNo, 39)
        self.assertEqual(component.elements[3].abundance, 9.1)

    def testParseInvalidIsotope(self):

        formula = "H[4]"

        component = Component(formula)
        with self.assertRaises(ChemicalFormulaParserException) as cm:
            component.parse()
            self.assertEqual(
                "H_19 is not a valid isotope of H."
                "\nThe following are valid:\n"
                "  -    H_Natural, H[0]\n"
                "  -    H_1, H[1]\n"
                "  -    H_2, H[2]\n"
                "  -    H_3, H[3]\n",
                str(cm.exception)
            )

    def testParseInvalidIsotopes(self):

        formula = "H[4]O[2]99.2"

        component = Component(formula)
        with self.assertRaises(ChemicalFormulaParserException) as cm:
            component.parse()
            self.assertEqual(
                "H_4 is not a valid isotope of H."
                "\nThe following are valid:\n"
                "  -    H_Natural, H[0]\n"
                "  -    H_1, H[1]\n"
                "  -    H_2, H[2]\n"
                "  -    H_3, H[3]\n",
                str(cm.exception)
            )

    def testParseDifficultInvalidIsotopes(self):

        formula = "H[19]12.0C[99]6.5U[345]K[2]9.1"

        component = Component(formula)
        with self.assertRaises(ChemicalFormulaParserException) as cm:
            component.parse()
            self.assertEqual(
                "H_19 is not a valid isotope of H."
                "\nThe following are valid:\n"
                "  -    H_Natural, H[0]\n"
                "  -    H_1, H[1]\n"
                "  -    H_2, H[2]\n"
                "  -    H_3, H[3]\n",
                str(cm.exception)
            )
