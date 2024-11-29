# Шифр Виженера - это классический шифр, первоначально разработанный
# итальянским криптографом Джованом Баттистой Беллазо и опубликованный
# в 1553 году. Он назван в честь более позднего французского криптографа
# Блеза де Виженера, который разработал более надежный шифр с автоматическим
# ключом (шифр, который включает текстовое сообщение в ключ).

# Этот шифр прост для понимания и реализации, но пережил
# три столетия попыток взлома, за что получил
# прозвище "le chiffre indéchiffrable" или "неразборчивый шифр".

# Из Википедии:
#
# Шифр Виженера - это метод шифрования алфавитного текста с
# использованием серии различных шифров Цезаря, основанных на буквах ключевого слова.
# Это простая форма многоалфавитной замены.
#
# . . .
#
# В шифре Цезаря каждая буква алфавита сдвигается на некоторое количество позиций;
# например, в шифре Цезаря со сдвигом 3 A станет D, B станет E, Y станет B и так далее.
# Шифр Виженера состоит из нескольких последовательно расположенных шифров
# Цезаря с разными значениями сдвига.


# Предположим, что ключ повторяется на протяжении всего текста, символ за символом.
# Обратите внимание, что в некоторых реализациях ключ повторяется над символами только
# в том случае, если они являются частью алфавита - в данном случае это не так.
#
# Сдвиг получается путем применения сдвига Цезаря к символу с соответствующим индексом
# ключа в алфавите.

# Визуальное представление:
#
# "мой секретный код, который я хочу защитить" // сообщение
# "passwordpasswordpasswordpassword" // ключ
#
# Напишите класс, который, получив ключ и алфавит, может быть использован
# для кодирования и декодирования из шифра Виженера.
#
# Пример
# : var alphabet = 'abcdefghijklmnopqrstuvwxyz';
# var key = 'пароль';
#
# // создает вспомогательный шифр с заменой каждой буквы
# // по соответствующему символу в ключе
# var c = new VigenèreCipher(key, alphabet);
#
# c.encode('codewars'); // returns 'rovwsoiv'
# c.decode('laxxhsj');  // returns 'waffles'
#
# Любой символ, которого нет в алфавите, должен быть оставлен как есть. Например (как показано выше):
#


class VigenereCipher(object):
    def __init__(self, key, alphabet):
        self.alphabet = list(alphabet)
        self.key = [alphabet.index(i) for i in key]

    def encode(self, text):
        encoded_message = ''
        for i in range(len(text)):
            if text[i] in self.alphabet:
                m_j = self.alphabet.index(text[i])
                k_j = self.key[i % len(self.key)]
                c_j = (m_j + k_j) % len(self.alphabet)
                encoded_message += self.alphabet[c_j]
            else:
                encoded_message += text[i]
        return encoded_message

    def decode(self, text):
        decode_message = ''
        for i in range(len(text)):
            if text[i] in self.alphabet:
                c_j = self.alphabet.index(text[i])
                k_j = self.key[i % len(self.key)]
                m_j = (c_j - k_j) % len(self.alphabet)
                decode_message += self.alphabet[m_j]
            else:
                decode_message += text[i]
        return decode_message


c = VigenereCipher('password', 'abcdefghijklmnopqrstuvwxyz')

print(c.encode("xt'k s ovzii cahdsi!"))      # "xt'k s ovzii cahdsi!" должно быть равно "xt'k o vwixl qzswej!"
print(c.decode("it's w ziruw qhaaqs!"))     # "it's w ziruw qhaaqs!" должно быть равно "it's a shift cipher!"
