from __future__ import annotations
from data_structures.referential_array import ArrayR
from data_structures.abstract_hash_table import HashTable
from typing import TypeVar

V = TypeVar('V')


class LazyDoubleTable(HashTable[str, V]):
    """
    Lazy Double Table uses double hashing to resolve collisions, and implements lazy deletion.
    """
    TABLE_SIZES = (
    5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869)
    HASH_BASE = 31
    HASH_BASE2 = 37  # Different base for hash2
    SENTINEL = "__DELETED__"  # Sentinel marker

    def __init__(self, sizes=None) -> None:
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.__size_index = 0
        self.__array: ArrayR[tuple[str, V]] = ArrayR(self.TABLE_SIZES[self.__size_index])
        self.__length = 0

    @property
    def table_size(self) -> int:
        return len(self.__array)

    def __len__(self) -> int:
        return self.__length

    def keys(self) -> ArrayR[str]:
        """
        Returns all keys in the hash table, ignoring sentinel markers.
        :complexity: O(N) where N is the table size.
        """
        res = ArrayR(self.__length)
        i = 0
        for x in range(self.table_size):
            if self.__array[x] is not None and self.__array[x] != (self.SENTINEL, None):
                res[i] = self.__array[x][0]
                i += 1
        return res

    def values(self) -> ArrayR[V]:
        """
        Returns all values in the hash table, ignoring sentinel markers.
        :complexity: O(N) where N is the table size.
        """
        res = ArrayR(self.__length)
        i = 0
        for x in range(self.table_size):
            if self.__array[x] is not None and self.__array[x] != (self.SENTINEL, None):
                res[i] = self.__array[x][1]
                i += 1
        return res

    def __contains__(self, key: str) -> bool:
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: str) -> V:
        position = self.__hashy_probe(key, False)
        return self.__array[position][1]

    def is_empty(self) -> bool:
        return self.__length == 0

    def __str__(self) -> str:
        result = ""
        for item in self.__array:
            if item is not None and item != (self.SENTINEL, None):
                (key, value) = item
                result += "(" + str(key) + "," + str(value) + ")\n"
        return result

    def hash(self, key: str) -> int:
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def gcd(self, a: int, b: int) -> int:
        """
        Calculate the Greatest Common Divisor of a and b using Euclidean algorithm.
        :param a: First integer.
        :param b: Second integer.
        :return: GCD of a and b.
        """
        while b:
            a, b = b, a % b
        return a

    def hash2(self, key: str) -> int:
        """
        Used to determine the step size for our hash table.
        Complexity:
            Best Case Complexity: O(K), where K is the length of the key.
            Worst Case Complexity: O(K), where K is the length of the key.
        """
        value = 0
        a = 27183
        for i in range(len(key) - 1, -1, -1):
            value = (ord(key[i]) + a * value) % self.table_size
            a = a * self.HASH_BASE2 % (self.table_size - 1)

        step = (value % (self.table_size - 1)) + 1
        while self.gcd(step, self.table_size) != 1:
            step = (step + 1) % (self.table_size - 1) or 1
        return step

    def __hashy_probe(self, key: str, is_insert: bool) -> int:
        """
        Find the correct position for this key in the hash table using hashy probing.
        Raises:
            KeyError: When the key is not in the table, but is_insert is False.
            RuntimeError: When a table is full and cannot be inserted.
        Complexity:
            Best Case Complexity: O(K), when the initial position is empty or matches the key.
            Worst Case Complexity: O(N * K), when we need to probe the entire table.
            N is the table size, K is the length of the key.
        """
        position = self.hash(key)
        step = self.hash2(key)
        first_deleted = None

        for _ in range(self.table_size):
            current = self.__array[position]
            if current is None:
                if is_insert:
                    return position if first_deleted is None else first_deleted
                raise KeyError(key)
            elif current == (self.SENTINEL, None):
                if first_deleted is None:
                    first_deleted = position
                if not is_insert:
                    position = (position + step) % self.table_size
                    continue
            elif current[0] == key:
                return position
            position = (position + step) % self.table_size

        if is_insert and first_deleted is not None:
            return first_deleted
        raise RuntimeError("Table is full!")

    def __setitem__(self, key: str, data: V) -> None:
        """
        Set a (key, value) pair in our hash table.
        Complexity:
            Best Case Complexity: O(K), when the initial position is empty.
            Worst Case Complexity: O(N * K + N^2 * K), when rehashing is needed.
            N is the table size, K is the length of the key.
        """
        position = self.__hashy_probe(key, True)

        if self.__array[position] is None or self.__array[position] == (self.SENTINEL, None):
            self.__length += 1

        self.__array[position] = (key, data)

        if self.__length > (self.table_size * 2) // 3:
            self.__rehash()

    def __delitem__(self, key: str) -> None:
        """
        Deletes a (key, value) pair in our hash table.
        Complexity:
            Best Case Complexity: O(K), when the key is found at the initial position.
            Worst Case Complexity: O(N * K), when we need to probe the entire table.
            N is the table size, K is the length of the key.
        """
        position = self.__hashy_probe(key, False)
        self.__array[position] = (self.SENTINEL, None)
        self.__length -= 1

    def __rehash(self) -> None:
        """
        Need to resize table and reinsert all values
        Complexity:
            Best Case Complexity: O(N * K), when all items insert with minimal probing.
            Worst Case Complexity: O(N^2 * K), when all items require maximum probing.
            N is the number of items, K is the length of the key.
        """
        old_array = self.__array
        self.__size_index += 1
        if self.__size_index == len(self.TABLE_SIZES):
            return
        self.__array = ArrayR(self.TABLE_SIZES[self.__size_index])
        self.__length = 0

        for item in old_array:
            if item is not None and item != (self.SENTINEL, None):
                key, value = item
                self[key] = value