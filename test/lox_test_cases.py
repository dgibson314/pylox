LOX_FUNCTIONS_EXPECTED_VALUES = [
    ("""
     print 2 + 2;
     """,
     ['4']),

    ("""
     print "hello world!";
     """,
     ['"hello world!"']),

    ("""
     var a = 0;
     var b = 1;
     {
       print a;
       print b;
       var c = 2;
       print c;
     }
     """,
     ['0', '1', '2']
    ),

    ("""
     fun count(n) {
       if (n > 1) count(n - 1);
       print n;
     }
     count(3);
     """,
     ['1', '2', '3']
    )
]


