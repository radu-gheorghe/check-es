#!/usr/bin/python

import mox, unittest
import check_es_insert
import sys,time,pyes,__builtin__

class Calculator(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        self.mox.ResetAll()

    def test_calculate_returns_documentspersecond(self):
        '''Let's see if it can do some math'''
        my_calculator=check_es_insert.Calculator(warn=5,crit=7)
        result=my_calculator.calculate(old_value=7,new_value=37,old_time=1338558183.7,new_time=1338558193.7)
        self.assertEqual(result,3.0)
    def printandexit_runner(self,value,expected_code,index='all'):
        my_calculator=check_es_insert.Calculator(warn=7,crit=20)
        (text,exit_code)=my_calculator.printandexit(result=value)
        self.assertEqual(text,"Number of documents inserted per second (index: %s) is %f | 'es_insert'=%f;7;20;;" % (index,value,value))
        self.assertEqual(exit_code,expected_code)
    def test_printandexit_withOK_returns_expectedTextAndExpectedCode(self):
        '''Given a set of values, it should return the correct exit codes for OK,WARNING,CRITICAL,UNKNOWN, and also the correct text'''
        self.printandexit_runner(value=5,expected_code=0)
    def test_printandexit_withWARN_returns_expectedTextAndExpectedCode(self):
        '''Given a set of values, it should return the correct exit codes for OK,WARNING,CRITICAL, and also the correct text'''
        self.printandexit_runner(value=8,expected_code=1)
    def test_printandexit_withCRIT_returns_expectedTextAndExpectedCode(self):
        '''Given a set of values, it should return the correct exit codes for OK,WARNING,CRITICAL, and also the correct text'''
        self.printandexit_runner(value=25,expected_code=2)
    def test_getPrevious_shouldReturnWhateverDiskerReturns(self):
        '''getPrevious should initialize a Disker object, and ask for the previous value, and return it'''
        #mock a Disker
        self.mox.StubOutClassWithMocks(check_es_insert,'Disker')
        dummy_disker = check_es_insert.Disker(file='/tmp/check_es_insert')
        #make Disker.getPrevious it return a value
        dummy_disker.getPrevious().AndReturn((5,1338558183))
        #replay the mock
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=1,crit=2)
        result = my_calculator.getPrevious()
        self.assertEqual(result,(5,1338558183))

    def test_getPrevious_DiskerRaisesException_returnsminus2(self):
        '''getCurrent, in case Disker.getPrevious raises an exception, should return -2 as value and 0 as time'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Disker')
        #mock a Disker
        dummy_disker = check_es_insert.Disker(file='/tmp/check_es_insert')
        #make it raise an exception
        dummy_disker.getPrevious().AndRaise(BaseException("Something nasty happened"))
        #replay the mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=1,crit=2)
        result = my_calculator.getPrevious()
        self.assertEqual(result,(-2,0))

    def test_getCurrent_shouldReturnWhateverElasticsearcherReturns(self):
        '''getCurrent should initialize an Elasticsearcher object, and ask for the current value, and return it, along with the current timestamp'''
        #mock an Elasticsearcher
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it return a value
        dummy_elasticsearcher.getCurrent('').AndReturn(7)
        #mock timer()
        self.mox.StubOutWithMock(check_es_insert,"timer")
        check_es_insert.timer().AndReturn(1338558185.54)
        #replay the mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=1,crit=2)
        result = my_calculator.getCurrent()
        self.assertEqual(result,(7,1338558185.54))

    def test_getCurrent_ElasticsearcherRaisesException_returnsminus1(self):
        '''getCurrent, in case Elasticsearcher.__init__ raises an exception, should return -1 as value and 0 as time'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        #mock an Elasticsearcher
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it raise an exception
        dummy_elasticsearcher.getCurrent('').AndRaise(BaseException("Something nasty happened"))
        #replay the mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=1,crit=2)
        result = my_calculator.getCurrent()
        self.assertEqual(result,(-1,0))

    def test_run_shoulddoeverything(self):
        '''This method should go through all the methods'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        #mock an Elasticsearcher
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it return a value
        dummy_elasticsearcher.getCurrent('').AndReturn(7)
        #mock timer()
        self.mox.StubOutWithMock(check_es_insert,"timer")
        check_es_insert.timer().AndReturn(1338558185.54)
        self.mox.StubOutClassWithMocks(check_es_insert,'Disker')
        #mock a Disker
        dummy_disker = check_es_insert.Disker(file='/tmp/check_es_insert')
        #make getPrevious work
        dummy_disker.getPrevious().AndReturn((5,1338558183))
        #make writeCurrent() work
        dummy_disker.writeCurrent(7, 1338558185.54)
        #replay all mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=2,crit=3)
        result = my_calculator.run()
        self.assertEqual(result[1],0)
        self.assertEqual(result[0], "Number of documents inserted per second (index: %s) is %f | 'es_insert'=%f;%d;%d;;" % ('all',0.787402,0.787402,2,3))

    def test_run_writeCurrentThrowsException_shouldExitWithUnknown(self):
        '''If it can't write the current results to the file, it should return UNKNOWN to alert the user'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        #mock an Elasticsearcher
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it return a value
        dummy_elasticsearcher.getCurrent('').AndReturn(7)
        #mock timer()
        self.mox.StubOutWithMock(check_es_insert,"timer")
        check_es_insert.timer().AndReturn(1338558185.54)
        self.mox.StubOutClassWithMocks(check_es_insert,'Disker')
        #mock a Disker
        dummy_disker = check_es_insert.Disker(file='/tmp/check_es_insert')
        #make getPrevious() work
        dummy_disker.getPrevious().AndReturn((5,1338558183))
        #make writeCurrent() raise an exception
        dummy_disker.writeCurrent(7, 1338558185.54).AndRaise(BaseException("Something weird happened"))
        #replay all mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=2,crit=3)
        result = my_calculator.run()
        self.assertEqual(result[1],3)
        self.assertEqual(result[0], "There was an issue writing the current results to file.")

    def test_run_getCurrentReturnsMinus1_shouldntWriteCurrentValuesToFile(self):
        '''If current number of docs can't be retrieved, return UNKNOWN and an error message. Don't try to write -1 to the old file'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        #mock an Elasticsearcher
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it return a value
        dummy_elasticsearcher.getCurrent('').AndRaise(BaseException("Something bad happened"))
        #replay all mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=2,crit=3)
        result = my_calculator.run()
        self.assertEqual(result[1],3)
        self.assertEqual(result[0], "There was an issue getting the status - and number of docs - from Elasticsearch. Check that ES is running and you have pyes installed")

    def test_run_getPreviousReturnsMinus2_shouldReturnUNKNOWNbutWriteCurrentDataIfItCan(self):
        '''If old number of docs can't be retrieved, return UNKNOWN and an error message'''
        self.mox.StubOutClassWithMocks(check_es_insert,'Elasticsearcher')
        #mock an Elasticsearcher
        dummy_elasticsearcher = check_es_insert.Elasticsearcher(address='localhost:9200')
        #make it return a value
        dummy_elasticsearcher.getCurrent('').AndReturn(7)
        #mock timer()
        self.mox.StubOutWithMock(check_es_insert,"timer")
        check_es_insert.timer().AndReturn(1338558185.54)
        self.mox.StubOutClassWithMocks(check_es_insert,'Disker')
        #mock a Disker
        dummy_disker = check_es_insert.Disker(file='/tmp/check_es_insert')
        #make getPrevious raise and exception
        dummy_disker.getPrevious().AndRaise(BaseException("Something bad happened"))
        #make writeCurrent() work
        dummy_disker.writeCurrent(7, 1338558185.54)
        #replay all mocks
        self.mox.ReplayAll()
        #now let's test
        my_calculator=check_es_insert.Calculator(warn=2,crit=3)
        result = my_calculator.run()
        self.assertEqual(result[1],3)
        self.assertEqual(result[0], "There was an issue getting the previous results from file.")

class Elasticsearcher(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
    def tearDown(self):
        #self.mox.VerifyAll()
        self.mox.UnsetStubs()
        self.mox.ResetAll()
    def test_getCurrent_givesSumOfAllDocuments(self):
        '''This should take the dictionary reply of pyes.ES.status() and pull out a sum of num_docs'''
        #mock pyes.ES.status()
        self.mox.StubOutClassWithMocks(pyes,"ES")
        dummyESconn = pyes.ES(['myeshost:12345'])
        dummyESconn.status().AndReturn({"indices" : { "4534" : { "docs" : { "num_docs" : 500000 } } , "4535" : { "docs" : { "num_docs" : 50000 } } } })
        self.mox.ReplayAll()

        #now to test
        my_es = check_es_insert.Elasticsearcher('myeshost:12345')
        result = my_es.getCurrent()
        self.assertEqual(result, 550000)

class Disker(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        self.mox.ResetAll()

    def test_getPrevious_shouldOpenAFileAndReturnTheData(self):
        '''In normal conditions, the file should be like "123 1338558193"'''
        #mock opener()
        self.mox.StubOutWithMock(check_es_insert,"opener")
        #mock a dummy file object
        dummyfile = self.mox.CreateMockAnything()
        #make opener() return our fake
        check_es_insert.opener('/tmp/bla').AndReturn(dummyfile)
        #make readline return what we want
        dummyfile.readline().AndReturn("1234 1338558185.54")
        self.mox.ReplayAll()

        #now let's see if it gets what's in the file
        mydisker=check_es_insert.Disker(file='/tmp/bla')
        result=mydisker.getPrevious()
        self.assertEqual(result,(1234, 1338558185.54))

    def test_writeCurrent_shouldWriteStuffToFile(self):
        '''Give it a value and a time, and it should be written'''
        #mock opener()
        self.mox.StubOutWithMock(check_es_insert,"opener")
        #mock a dummy file object
        dummyfile = self.mox.CreateMockAnything()
        #make opener() return our fake
        check_es_insert.opener('/tmp/bla',"w").AndReturn(dummyfile)
        #make write return what we want
        dummyfile.write("1234 1338558185.540000")
        self.mox.ReplayAll()

        #now let's see if it gets what's in the file
        mydisker=check_es_insert.Disker(file='/tmp/bla')
        result=mydisker.writeCurrent(value=1234,time=1338558185.54)

class Main(unittest.TestCase):
    '''tests for main()'''
    def test_main_returnsWhateverRunReturns(self):
        '''We expect this to create a Calculator, then run the it and print the text and exit with the exit code'''
        m = mox.Mox()
        #mock the argument parser
        m.StubOutWithMock(check_es_insert,"getArgs")
        #expect to return the needed stuff
        check_es_insert.getArgs('Nagios plugin for checking the number of inserts per second in Elasticsearch').AndReturn({ 'critical' : 3, 'warning' : 2, 'address' : 'myhost:1234', 'file' : '/tmp/bla', 'index' : 'articles' })
        #mock a calculator
        m.StubOutClassWithMocks(check_es_insert,'Calculator')
        #mock a Calculator
        dummy_calculator = check_es_insert.Calculator(warn=2, crit=3,myfile='/tmp/bla',myaddress='myhost:1234',index='articles')
        #make run() return foo and 3
        dummy_calculator.run().AndReturn(("foo",3))
        #mock printer()
        m.StubOutWithMock(check_es_insert,"printer")
        #expect to print "foo"
        check_es_insert.printer("foo")
        #mock exiter()
        m.StubOutWithMock(check_es_insert,"exiter")
        #expect to exit with 3
        check_es_insert.exiter(3)
        #replay all the mocks
        m.ReplayAll()
        #now test that stuff
        check_es_insert.main()
        #verify if the mocks were called
        m.VerifyAll()
        #cleanup
        m.UnsetStubs()
        m.ResetAll()

if __name__ == "__main__":
    calculator_tests = unittest.TestLoader().loadTestsFromTestCase(Calculator)
    elasticsearcher_tests = unittest.TestLoader().loadTestsFromTestCase(Elasticsearcher)
    disker_tests = unittest.TestLoader().loadTestsFromTestCase(Disker)
    main_tests = unittest.TestLoader().loadTestsFromTestCase(Main)
    all_tests = unittest.TestSuite([calculator_tests, elasticsearcher_tests, disker_tests,main_tests])
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
