use "testing.sml";
open SmlTests;

test("prepend 0 [1,2,3]", assert_equals_int_list([0,1,2,3], prepend 0 [1,2,3]));
test("prepend 42 []", assert_equals_int_list( [42], prepend 42 []));
test("prepend \"a\" [\"b\",\"c\"]", assert_equals_string_list(["a","b","c"], prepend "a" ["b","c"]));
test("prepend true [false]", assert_equals_bool_list([true, false], prepend true [false]));
test("prepend 10 nil", assert_equals_int_list([10], prepend 10 nil));

run();

OS.Process.exit(OS.Process.success);
