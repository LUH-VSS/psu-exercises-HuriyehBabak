fun concat a b = foldr (fn (curr, acc) => [curr] @ acc) a b;
