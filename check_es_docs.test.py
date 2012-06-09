#!/usr/bin/python

import mox, unittest
import check_es_insert, check_es_docs

class Main(unittest.TestCase):
    '''To test our one and only function'''
    def test_main_returnsUnknown_ifCalculator_returnsMinus1(self):
        '''If it can't get the current value from ES, print an error message and exit 3'''
        m=mox.Mox()
        #mock an argument parser
        m.StubOutWithMock(check_es_insert,"getArgs")
        #expect to be called properly and return some command-line options
        check_es_insert.getArgs(\
            'Nagios plugin for checking the total number of documents stored in Elasticsearch')\
            .AndReturn({ 'critical' : 7, 'warning' : 5, 'address' : 'myhost:1234', 'file' : '/tmp/bla'})
        #mock a Calculator instance
        m.StubOutClassWithMocks(check_es_insert,'Calculator')
        #mock a dummy Calculator
        dummy_calculator=check_es_insert.Calculator(warn=5,crit=7,myaddress='myhost:1234', myfile='/tmp/bla')
        #make getCurrent return -1
        dummy_calculator.getCurrent().AndReturn((-1,1338558185.54))
        #mock printer()
        m.StubOutWithMock(check_es_insert,"printer")
        #expect to print "Can't get number of documents from Elasticsearch"
        check_es_insert.printer("Can't get number of documents from Elasticsearch")
        #mock exiter()
        m.StubOutWithMock(check_es_insert,"exiter")
        #expect to exit with 3
        check_es_insert.exiter(3)
        #replay all mocks
        m.ReplayAll()
        #now let's test
        check_es_docs.main()
        #verify that all mocks were called as expected
        m.UnsetStubs()
        m.VerifyAll()
        #clean up
        m.ResetAll()
    def test_main_doesWhatPrintAndExitSays_inNormalConditions(self):
        '''If getCurrent returns a positive value, main() should print the text and exit with the code Calculator.printandexit() says'''
        m=mox.Mox()
        #mock an argument parser
        m.StubOutWithMock(check_es_insert,"getArgs")
        #expect to be called properly and return some command-line options
        check_es_insert.getArgs(\
            'Nagios plugin for checking the total number of documents stored in Elasticsearch')\
            .AndReturn({ 'critical' : 7, 'warning' : 5, 'address' : 'myhost:1234', 'file' : '/tmp/bla'})
        #mock a Calculator instance
        m.StubOutClassWithMocks(check_es_insert,'Calculator')
        #mock a dummy Calculator
        dummy_calculator=check_es_insert.Calculator(warn=5,crit=7,myaddress='myhost:1234', myfile='/tmp/bla')
        #make getCurrent return -1
        dummy_calculator.getCurrent().AndReturn((3,1338558185.54))
        #make printandexit expect to be called with the result and return something
        dummy_calculator.printandexit(3).AndReturn(("This is really cool",2))
        #mock printer()
        m.StubOutWithMock(check_es_insert,"printer")
        #expect to print "Can't get number of documents from Elasticsearch"
        check_es_insert.printer("Total number of documents in Elasticsearch is %d | 'es_docs'=%d;%d;%d;;" % (3,3,5,7))
        #mock exiter()
        m.StubOutWithMock(check_es_insert,"exiter")
        #expect to exit with 2
        check_es_insert.exiter(2)
        #replay all mocks
        m.ReplayAll()
        #now let's test
        check_es_docs.main()
        #verify that all mocks were called as expected
        m.UnsetStubs()
        m.VerifyAll()
        #clean up
        m.ResetAll()
        
if __name__ == "__main__":
    main_tests = unittest.TestLoader().loadTestsFromTestCase(Main)
    all_tests = unittest.TestSuite([main_tests])
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
