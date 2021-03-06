import unittest
from xml.etree.ElementTree import XML

from rdf.namespace import Namespace, TEST
from rdf.testcases.document import Document
from rdf.testcases.manifest import Manifest
from rdf.testcases.test import Test
from rdf.testcases.unittest import RDFTestCase, RDFTestSuite
from util import open_data_file, EX, TESTS, TEST_OPENER, NULL_OPENER


class TestRDFTestCase(unittest.TestCase):
    def setUp(self):
        if getattr(self, 'test', None) is not None:
            self.test_case = RDFTestCase.from_test(self.test)
            self.test_case.opener = TEST_OPENER
            self.result = self.test_case.defaultTestResult()
            self.test_case.run(self.result)
        else:
            self.skipTest("'test' attribute not set. abstract test case?")

    def test_is_test_case(self):
        self.assert_(isinstance(self.test_case, RDFTestCase))

    def test_is_unittest_test_case(self):
        self.assert_(isinstance(self.test_case, unittest.TestCase))

    def test_id_is_test_uri(self):
        self.assertEqual(self.test_case.id(), str(self.test.uri))

class TestUnboundTestCase(unittest.TestCase):
    def setUp(self):
        self.test_case = RDFTestCase()
        self.test_case.opener = TEST_OPENER
        self.result = self.test_case.defaultTestResult()
        self.test_case.run(self.result)

    def test_is_test_case(self):
        self.assert_(isinstance(self.test_case, RDFTestCase))

    def test_is_unittest_test_case(self):
        self.assert_(isinstance(self.test_case, unittest.TestCase))

    def test_id_uses_default_implementation(self):
        self.assertEqual(self.test_case.id(),
                         unittest.TestCase.id(self.test_case))

    def test_short_description_uses_default_implementation(self):
        self.assertEqual(self.test_case.shortDescription(),
                         unittest.TestCase.shortDescription(self.test_case))

class TestWithdrawnTestCase(TestRDFTestCase):
    test = Test(TEST.PositiveParserTest, EX.test)
    test.status = 'WITHDRAWN'

    def test_is_skipped_due_to_status(self):
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.failures, [])
        self.assertEqual(self.result.skipped,
                         [(self.test_case, "test status is WITHDRAWN")])
        self.assertEqual(self.result.testsRun, 1)

    def test_short_description_is_uri(self):
        self.assertEqual(self.test_case.shortDescription(),
                         "http://example.org/test")

class TestObsoleteTestCase(TestRDFTestCase):
    test = Test(TEST.PositiveParserTest, EX.test)
    test.status = 'OBSOLETE'
    test.description = "Obsolete test case!"

    def test_is_skipped_due_to_status(self):
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.failures, [])
        self.assertEqual(self.result.skipped,
                         [(self.test_case, "test status is OBSOLETE")])
        self.assertEqual(self.result.testsRun, 1)

    def test_docstring_is_test_description(self):
        self.assertEqual(self.test_case.runTest.__doc__,
                         "Obsolete test case!")

    def test_short_description_is_test_uri_and_description(self):
        self.assertEqual(self.test_case.shortDescription(),
            "http://example.org/test\nObsolete test case!")

class TestPositiveParserTestCase(TestRDFTestCase):
    test = Test(TEST.PositiveParserTest, EX.test)
    test.status = 'APPROVED'
    test.input_documents = {Document(TEST['NT-Document'],
                                     TESTS['datatypes/test001.nt'])}
    test.output_document = Document(TEST['NT-Document'],
                                    TESTS['datatypes/test001.nt'])

    def test_runs_without_errors(self):
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.skipped, [])
        self.assertEqual(self.result.testsRun, 1)

class TestNegativeParserTestCase(TestRDFTestCase):
    test = Test(TEST.NegativeParserTest, EX.test)
    test.status = 'APPROVED'
    test.input_document = Document(TEST['NT-Document'],
                                   TESTS['datatypes/test001.nt'])
    
    def test_runs_without_errors(self):
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.skipped, [])
        self.assertEqual(self.result.testsRun, 1)

class TestPositiveEntailmentTestCase(TestRDFTestCase):
    pass

class TestNegativeEntailmentTestCase(TestRDFTestCase):
    pass

class TestMiscellaneousTestCase(TestRDFTestCase):
    test = Test(TEST.MiscellaneousTest, EX.test)
    test.status = 'APPROVED'

    def test_run_raises_exception(self):
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.failures, [])
        self.assertEqual(self.result.skipped, [])
        self.assertEqual(self.result.testsRun, 1)
        self.assertEqual(self.result.wasSuccessful(), False)

class TestRDFTestSuite(unittest.TestCase):
    def setUp(self):
        self.file = open_data_file('manifest.rdf')
        self.manifest = Manifest(self.file)
        self.suite = RDFTestSuite.from_manifest(self.manifest,
                                                opener=NULL_OPENER)
        self.result = unittest.TestResult()
        self.suite.run(self.result)

    def test_has_same_length_as_manifest(self):
        tests = list(self.suite)
        self.assertEqual(len(self.manifest), len(tests))

    def test_runs_tests(self):
        self.assertEqual(self.result.testsRun, 266)
    
    def test_skips_tests_without_approved_status(self):
        self.assertEqual(len(self.result.skipped), 54)

