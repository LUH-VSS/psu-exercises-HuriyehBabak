fun
    last [] = raise Empty
  | last [head] = head
  | last (head::tail) = last tail;
