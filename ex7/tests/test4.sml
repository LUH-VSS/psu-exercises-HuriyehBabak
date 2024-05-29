use "testing.sml";
open SmlTests;

test("concat [\"a\",\"b\",\"c\"] [\"d\",\"e\",\"f\"]", assert_equals_string_list(["d", "e", "f", "a", "b", "c"], concat ["a","b","c"] ["d","e","f"]));
test("concat [3,4] [1,2]", assert_equals_int_list([1,2,3,4], concat [3,4] [1,2]));
test("concat [] [1]", assert_equals_int_list([1], concat [] [1]));
test("concat [1] []", assert_equals_int_list([1], concat [1] []));
test("concat [] []", assert_equals_int_list([], concat [] []));

run();

OS.Process.exit(OS.Process.success);
