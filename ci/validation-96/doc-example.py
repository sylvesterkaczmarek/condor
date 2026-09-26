import condor as co
from condor.backend import operators as ops

class Sum(co.ExplicitSystem):
    x = input()
    y = input()
    output.total = x + y

result = Sum(x=2, y=3)
substitutions = result.input.dict_of()
evaluated = ops.substitute(Sum.total.backend_repr, substitutions)
import numpy as np
assert np.asarray(evaluated).item() == 5
assert result.input.dict_of("name") == {"x": 2, "y": 3}
print("API documentation example passed")
