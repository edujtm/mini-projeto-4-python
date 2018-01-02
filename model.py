
"""
Este modulo possui as classes referente aos dados utilizados no mini-projeto.

As operaçoes realzadas por estas classes fazem alteracoes no banco de dados por meio do
modulo

As classes desse modulo sao:
    -- User
    -- Account
    -- Money
"""

import decimal as dec
from copy import deepcopy
import sys

class User:
    """
    Classe utilizada para guardar informaçoes pessoais de um usuario.
    Existe principalmente para evitar o acumulo de atividades na classe Account.

    Atributos:
        -- fullname -> Nome inteiro do usuario
        -- cpf -> digitos do cpf do usuario.
        -- password -> Senha do usuario.

    Em um caso real, seria utilizado algum tipo de codificacao  para armazenar estas informacoes
    """

    cpflen = 11

    def __init__(self, name, cpf, age, password):
        self.fullname = name
        self.cpf = cpf
        self.password = password
        self.age = age

    def __str__(self):
        result = ''
        result += 'Usuario: ' + self.fullname + '\n'
        result += 'Cpf: ' + self.cpf + '. Formatado: ' + self.formattedCpf() + '\n'
        result += 'Idade: ' + str(self.age) + '\n'
        return result

    def getCpf(self):
        return self._cpf

    def setCpf(self, cpfvalue):
        if len(cpfvalue) != User.cpflen and not cpfvalue.isdigit():
            raise AttributeError('O cpf deve possuir 11 digitos. Digite apenas os numeros.')
        else:
            self._cpf = cpfvalue

    cpf = property(getCpf, setCpf)

    def formattedCpf(self):
        """
            Retorna o cpf no formato NNN.NNN.NNN-NN
        """
        return self.cpf[:3] + '.' + self.cpf[3:6] + '.' + self.cpf[6:9] + '-' + self.cpf[9:]


class Account:
    accountId = 0
    acctlen = 6

    def __init__(self, user, agency_number, balance = 0.0):
        if user.__class__.__name__ != 'User':
            raise AttributeError
        else:
            self.agency_number = agency_number
            self.acct = Account.accountId
            self.user = user
            self.balance = Money(balance)
            Account.accountId += 1

    def __str__(self): pass

    def getAcct(self):
        return self.account_number

    def setAcct(self, value):
        self.account_number = '{0:0^6}'.format(value)

    acct = property(getAcct, setAcct)

    def getBalance(self):
        return self._balance

    def setBalance(self, value):
        if isinstance(value, Money):
            self._balance = value
        else:
            self._balance = Money(value)

    balance = property(getBalance, setBalance)


class Money:

    """
    Adapta um valor decimal para o sistema bancario/monetario. Com fins de formatacao e
    gerenciamento de cedulas.

    Preferi utilizar composicao para value ao inves de heranca pois Decimal possui muitos metodos que nao se relacionam
    com as aplicacoes monetarias.
    """

    banknotes = (2, 5, 10, 20, 50, 100)
    qntoptions = 3

    def __init__(self, value):
        self.value = dec.Decimal(value).quantize(dec.Decimal('.01'), rounding=dec.ROUND_UP)

    def __str__(self):
        sign = '-' if self.value < 0.0 else ''
        pos = abs(self.value)
        whole = Money.commas(int(pos))
        fract = ("{0:.2f}".format(pos))[-2:]
        result = "{0}{1}.{2}".format(sign, whole, fract)
        return result

    def __add__(self, other):
        if isinstance(other, Money): other = other.value
        return Money(self.value + other)

    def __radd__(self, other):
        return Money(self.value + other)

    def __mul__(self, other):
        if isinstance(other, Money): other = other.value
        return Money(self.value * other)

    def __sub__(self, other):
        if isinstance(other, Money): other = other.value
        return Money(self.value - other)

    @staticmethod
    def commas(value):
        """
            Retorna o valor de um numero inteiro value, com separadores a cada 3 digitos.
            Ex: NNN,NNN,NNN
        :param value: Numero inteiro a ser formatado
        :return: String com valor formatado com separador
        """
        digits = str(value)
        assert (digits.isdigit())
        result = ''
        while digits:
            digits, last = digits[:-3], digits[-3:]
            result = (last + ',' + result) if result else last
        return result

    def getOptions(self):
        """
            Obtem as opcoes de cedulas para o valor sacado.

            A quantidade de opcoes e dada de acordo com o valor de Money.qntoptions

        :return: result -> Lista de strings com as opcoes disponiveis
        """
        result = []
        cnt = 0
        size = len(self.banknotes) - 1
        for idx, bknote in enumerate(reversed(self.banknotes)):
            if cnt == Money.qntoptions: break
            if dec.Decimal(bknote) <= self.value:
                notes = self.separate(size-idx)
                text = str(cnt+1) + '. '
                for key in notes:
                    text += str(notes[key]) + (' cedulas de ' if notes[key] != 1 else ' cedula de ') + str(key) + ' / '
                result.append(text)
                cnt += 1
        return result


    def separate(self, pos):
        assert self.value >= 1, 'Nao e possivel fazer saque para valores menores ou igual a 0'
        assert self.value == self.value.to_integral_value(), 'Nao e possivel dar opcoes de cedulas para o valor ' + str(self.value) + '. So e possivel dar opcoes para valores inteiros.'
        result = {}
        temp = deepcopy(self.value)     # Nao tenho certeza se essa e a melhor forma de evitar alteracoes no objeto original
        while temp != 0:
            bknote = self.banknotes[pos]
            qnt = temp // dec.Decimal(bknote)
            temp -= qnt * dec.Decimal(bknote)
            if qnt != 0: result[bknote] = int(qnt)
            pos -= 1
        return result

if __name__ == '__main__':

    def testSeparate(value):
        try:
            print('Testando valor: ' + str(value))
            print(value.separate(4), end='. ')
        except AssertionError:
            print(sys.exc_info()[1])
        else:
            print('Tudo certo...')

    print('testando separate...')
    for value in (99, 999, 3.14, -10):
        testSeparate(Money(value))
    print()

    print('Testando iteracao nas cedulas invertidas invertido...')
    print(list((idx, value) for idx, value in enumerate(reversed(Money.banknotes))))
    size = len(Money.banknotes)-1
    print(list((size-idx, value) for idx, value in enumerate(reversed(Money.banknotes))))
    print()

    print('Testando getOptions...')
    value = Money(1000)
    print('Valor testado: ' + str(value))
    options = value.getOptions()
    for text in options:
        print(text)