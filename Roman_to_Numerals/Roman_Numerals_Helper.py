import roman

class RomanNumerals:

    @staticmethod
    def to_roman(val: int) -> str:
        roman_numbers = {'M': 1000, 'CM': 900, 'D': 500, 'CD': 400,
                         'C': 100, 'XC': 90, 'L': 50, 'XL': 40,
                         'X': 10, 'IX': 9, 'V': 5, 'IV': 4, 'I': 1}
        roman = ''
        for letter, value in roman_numbers.items():
            while val >= value:
                roman += letter
                val -= value
        return roman

    @staticmethod
    def from_roman(roman_num: str) -> int:
        roman_numbers = {'M': 1000, 'CM': 900, 'D': 500, 'CD': 400,
                         'C': 100, 'XC': 90, 'L': 50, 'XL': 40,
                         'X': 10, 'IX': 9, 'V': 5, 'IV': 4, 'I': 1}
        result = 0
        index = 0
        for numeral, integer in roman_numbers.items():
            while roman_num[index:index + len(numeral)] == numeral:
                result += integer
                index += len(numeral)
        return result




num = RomanNumerals()
print(num.to_roman(3548))
print(num.from_roman("MMMDXLVIII"))
