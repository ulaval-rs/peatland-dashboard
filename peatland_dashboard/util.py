from typing import List, Union


def round_values(v: Union[List[float], float], decimals=4) -> Union[List[float], float]:
    if isinstance(v, float):
        return round(v, decimals)

    return [round(n, decimals) for n in v]
