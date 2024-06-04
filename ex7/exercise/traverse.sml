datatype 'a tree = empty | node of 'a * 'a tree * 'a tree;

fun traverse (empty) = []
  | traverse (node (value, t1, t2)) = [value] @ traverse t1 @ traverse t2;
