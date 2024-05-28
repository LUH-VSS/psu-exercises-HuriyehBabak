use "testing.sml";
open SmlTests;

test("factorial 0", assert_equals_int(1, factorial 0)); 
test("factorial 1", assert_equals_int(1, factorial 1));
test("factorial 2", assert_equals_int(2, factorial 2));
test("factorial 3", assert_equals_int(6, factorial 3));
test("factorial 4", assert_equals_int(24, factorial 4));
test("factorial 5", assert_equals_int(120, factorial 5));
test("factorial 6", assert_equals_int(720, factorial 6));
test("factorial 7", assert_equals_int(5040, factorial 7));
test("factorial 8", assert_equals_int(40320, factorial 8));
test("factorial 9", assert_equals_int(362880, factorial 9));
test("factorial 10", assert_equals_int(3628800, factorial 10));

run();

OS.Process.exit(OS.Process.success);
