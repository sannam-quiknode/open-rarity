from typing import TypeVar

K = TypeVar("K", str, int, float, tuple)
L = TypeVar("L")
R = TypeVar("R")
T = TypeVar("T")


def merge(
    left: list[dict[K, L]], right: list[dict[K, R]], key: tuple[K]
) -> list[dict[K, L | R]]:
    """Performs a hash merge of two list of dict data structures. A general assumption
    that the `right` list is shorter in length than the `left` is wise. Duplicated rows
    by key in the `right` are not handled and only the latest value in the list will be
    kept. Duplicate keys across `left` and `right` dictionaries will take the `right`'s
    values.

    Parameters
    ----------
    left : list[dict]
        Data to be joined with
    right : list[dict]
        Data coming into the join
    key : tuple[Hashable]
        Keys to use during merge. Single value keys must have a trailing comma.
        ie: (<key>,)

    Returns
    -------
    list[dict]
        List with merged and joined values from both lists
    """
    right = {tuple((row[k] for k in key)): row for row in right}
    return [lrow | right[tuple((lrow[k] for k in key))] for lrow in left]


def rank_over(
    data: list[dict[K, T]], key: K | tuple[K, K], desc: bool = True
) -> list[dict[K, T | int]]:
    """Simple RANK OVER algorithm. The data will be sorted by the key or tuple of keys
    provided. Ranks are then applied where ties receive the same rank while the next
    'possible' rank will continue to increment as opposed to a DENSE RANK where the next
    rank would be the next literal value.

    Parameters
    ----------
    data : list[dict[K, T]]
        A list of dictionaries to be ranked
    key : K | tuple[K, K]
        A single string value or tuple of strings to use for the ranking decision. All
        keys must exist in every internal dictionary. Tuple keys _should_ work and can
        be passed as ((<value>, <value>),) where the trailing comma is REQUIRED.

    Returns
    -------
    list[dict[str, T]]
        An identical data structure to the passed data with the addition of a 'rank' key
    """
    # TODO: probably should generically validate that the key exists for all rows in data
    key = (key,) if isinstance(key, str) else key

    data = sorted(data, key=lambda row: tuple((row[k] for k in key)), reverse=desc)

    current_rank = 1
    prev_value = None
    for incremental_rank, row in enumerate(data, 1):
        data_index = incremental_rank - 1
        current_value = tuple((row[k] for k in key))

        if current_value == prev_value or incremental_rank == 1:
            data[data_index]["rank"] = current_rank
        else:
            data[data_index]["rank"] = current_rank = incremental_rank
        prev_value = current_value

    return data