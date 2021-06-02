from typing import List


class Utils:
    @staticmethod
    def print_array(array: List) -> None:
        print_string = '[ '
        for element in array:
            print_string += element.__str__()
            print_string += ', '
        print_string += ' ]'
        print(print_string)
