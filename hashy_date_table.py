from __future__ import annotations
from data_structures.hash_table_linear_probing import LinearProbeTable


class HashyDateTable(LinearProbeTable[str]):
    """
    HashyDateTable assumed the keys are strings representing dates, and therefore tries to
    produce a balanced, uniform distribution of keys across the table.

    Conflicts are resolved using Linear Probing.

    All values will also be strings.
    """

    def __init__(self) -> None:
        """
        Initialise the Hash Table with with increments of 366 as the table size.
        This means, initially we will have 366 slots, once they are full, we will have 4 * 366 slots, and so on.

        No complexity is required for this function.
        Do not make any changes to this function.
        """
        LinearProbeTable.__init__(self, (366, 4 * 366, 16 * 366))

    def hash(self, key: str) -> int:
        """
        Hash a key for insert/retrieve/update into the hashtable.
        The key will always be exactly 10 characters long and can be any of these formats, but nothing else:
        - DD/MM/YYYY
        - DD-MM-YYYY
        - YYYY/MM/DD
        - YYYY-MM-DD

        The function assumes the dates will always be valid i.e. the input will never be something like 66/14/2020.

        Complexity:
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        # Determine delimiter and parse date
        delimiter = '/' if '/' in key else '-'
        parts = key.split(delimiter)

        # Parse based on format (assuming consistent format per table use)
        year = int(parts[0]) if len(parts[0]) == 4 else int(parts[2])  # YYYY or last part for DD formats
        if len(parts[0]) == 4:  # YYYY/MM/DD or YYYY-MM-DD
            month = int(parts[1])
            day = int(parts[2])
        else:  # DD/MM/YYYY or DD-MM-YYYY
            month = int(parts[1])
            day = int(parts[0])

        # Calculate day of year (1-366)
        days_in_month = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)  # Changed to tuple
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            # Replace the 28 with 29 for leap year (since tuple is immutable, create a new tuple)
            days_in_month = days_in_month[:2] + (29,) + days_in_month[3:]
        day_of_year = day
        for m in range(1, month):
            day_of_year += days_in_month[m]

        # Determine c (number of years based on table size)
        table_size = self.table_size
        c = table_size // 366

        # Map year to [0, c-1] range (normalize to 1970 as base)
        base_year = 1970
        year_index = (year - base_year) % c

        # Combine year index and day of year to get hash value
        hash_value = (year_index * 366 + (day_of_year - 1)) % table_size

        return hash_value