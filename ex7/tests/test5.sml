use "testing.sml";
open SmlTests;

test("traverse empty", assert_equals_int_list([], traverse empty));

test("traverse (node(100, empty, empty))", assert_equals_int_list([100], traverse (node(100, empty, empty))));

test("traverse (node(100, empty, node(200, empty, empty)))", assert_equals_int_list([100, 200], traverse (node(100, empty, node(200, empty, empty)))));

test("traverse (node(100, node(200, node(300, node(400, empty, empty), empty), empty), node(500, empty, empty)))", assert_equals_int_list([100, 200, 300, 400, 500], traverse (node(100, node(200, node(300, node(400, empty, empty), empty), empty), node(500, empty, empty)))));

test("traverse (node(10, node(20, empty, node(30, empty, empty)), node(40, empty, node(50, empty, empty))))", assert_equals_int_list([10, 20, 30, 40, 50], traverse (node(10, node(20, empty, node(30, empty, empty)), node(40, empty, node(50, empty, empty))))));

test("traverse (node(1,node(2,node(3,empty,node(4,empty,empty)),empty),node(5,empty,empty)))", assert_equals_int_list([1,2,3,4,5], traverse (node(1,node(2,node(3,empty,node(4,empty,empty)),empty),node(5,empty,empty)))));

test("traverse (node(\"a\", node(\"b\", empty, node(\"c\", empty, empty)), node(\"d\", empty, empty)))", assert_equals_string_list(["a","b","c","d"], traverse (node("a", node("b", empty, node("c", empty, empty)), node("d", empty, empty)))));


run();

OS.Process.exit(OS.Process.success);
