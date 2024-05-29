use "testing.sml";
open SmlTests;

test("last  [1]", assert_equals_int(1,  last  [1]));
test("last  [1,2,3]", assert_equals_int(3, last [1,2,3]));
test("last  [\"a\",\"b\",\"c\"]", assert_equals_string("c", last ["a", "b", "c"]));
test("last (explode \"Test\")", assert_equals_string("t", Char.toString(last(explode "Test"))));
test("last []", assert_raises(last, [], Empty));

run();

OS.Process.exit(OS.Process.success);
