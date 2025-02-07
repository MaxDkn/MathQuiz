from random import randint, choice, shuffle, choices
from math import ceil, log10, sin, cos, radians, prod, gcd, lcm
from time import time


def decomposition_prime_factor(n, /) -> list[int]:
    """
    returns the list of prime numbers decomposing a number

    script found at :
    https://www.infinimath.com/espaceeducation/tangenteeducation/articles/TE15/FacteursPremiers.pdf
    and I modify only few lines
    :param n:
    :return:
    """
    result = []

    if n == 0:
        return []
    elif n < 0:
        n = abs(n)
        result.append(-1)
    d = 2
    while n % d == 0:
        result.append(d)
        n //= d

    d = 3
    while d <= n:
        while n % d == 0:
            result.append(d)
            n //= d
        d += 2
    return result


assert decomposition_prime_factor(40) == [2, 2, 2, 5]
assert decomposition_prime_factor(-28) == [-1, 2, 2, 7]


class Questions:
    """
    This object allows you to pool functions that will be used by all the different subjects, such as the function to
     generate a question. All subjects will be child objects of this object.
     """

    def __init__(self, child: object) -> None:
        self.clr = child

    def generate(self) -> dict:
        """
        searches in the functions of the child object, all functions starting with the keyword "q_" and randomly picks a
        question. Then returns the result of this function. This makes it possible to make the link and generate a
        question among all those proposed by the child object.

        :return: dictionary with "question", "answer", "other answer" and "subject" keys
        """
        questions = []
        for attribute_name in dir(self.clr):
            attribute = getattr(self.clr, attribute_name)
            if callable(attribute) and not attribute_name.startswith("__") and attribute_name.startswith('q_'):
                questions.append([attribute, attribute_name])
        if not questions:
            dict_response = {'question': f'({self.clr.__class__.__name__}) No function begin with "q_".',
                             'answer': ''}
        else:
            function, function_name = choice(questions)
            dict_response = function()
            try:
                if dict_response.get('question') is None:
                    dict_response = {
                        'question': f'({self.clr.__class__.__name__} - {function_name}) "question" key is missing.',
                        'answer': ''
                    }
                elif dict_response.get('answer') is None:
                    dict_response = {
                        'question': f'({self.clr.__class__.__name__} - {function_name}) "answer" key is missing.',
                        'answer': ''
                    }
            except AttributeError:
                dict_response = {
                    'question': f'{self.clr.__class__.__name__}().{function_name}() do not return dictionary.',
                    'answer': ''
                }
        dict_response['subject'] = self.clr.__class__.__name__
        dict_response['response_type'] = type(dict_response['answer']).__name__
        return dict_response

    def get_number_of_questions(self) -> int:
        """
        Counts the number of functions starting with the keyword "q_". This is mainly for weighted draws.
        :return: number of different questions the child object has
        """
        count = 0
        for attribute_name in dir(self.clr):
            attribute = getattr(self.clr, attribute_name)
            if callable(attribute) and not attribute_name.startswith("__") and attribute_name.startswith('q_'):
                count += 1
        return count


class Algebra(Questions):
    """
    This object is about Algebra question. In fact, only functions starting with "q_" are questions
    """

    def __init__(self):
        super().__init__(self)

    @staticmethod
    def format_value(coefficient: int, variable: str) -> str:
        if coefficient == 0:
            return ''
        sign = '+' if coefficient > 0 else '-'
        if abs(coefficient) == 1:
            if variable == '':
                coefficient = abs(coefficient)
            else:
                coefficient = ''
        return f"{sign}{abs(coefficient) if coefficient else ''}{variable}".strip()

    def format_equation(self, *coefficients: int, shuffle_the_equation: bool = True) -> str:
        """
        returns the writing of a polynomial expanded by taking as input the coefficients
        """
        equation = []
        exponents = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']

        for index, coefficient in enumerate(coefficients):
            exponent = len(coefficients) - 1 - index

            if exponent == 0:
                variable = ''
            elif exponent == 1:
                variable = 'x'
            else:
                variable = 'x'
                for number in str(exponent):
                    variable += exponents[int(number)]

            equation.append(self.format_value(coefficient, variable))

        if shuffle_the_equation:
            shuffle(equation)
        equation = ''.join(equation)
        try:
            equation = equation[1:] if equation[0] == "+" else equation
        #  If there is no number in the input of the function
        except IndexError:
            pass
        return equation

    def q_simple_equation(self, shuffle_the_equation: bool = True, *, a_interval: tuple = (-4, 4),
                          x_interval: tuple = (-10, 10), c_interval: tuple = (-2, 2)) -> dict:
        """
        Asks questions about degree one equation, such as :
        ax + b = c
        where x € [-14; 14]
        and a € [-4; 4]
        and c € [
        :return:
        """
        assert a_interval != (0, 0)
        sentences = ['Quelle est la valeur de x dans {equation}={c}',
                     'Quelle est la solution de {equation}={c}',
                     'Donner l\'antécédent de {c} avec f(x)={equation}']
        a = randint(min(a_interval), max(a_interval))
        while a == 0:
            a = randint(min(a_interval), max(a_interval))
        x = randint(min(x_interval), max(x_interval))
        while x == 0:
            x = randint(min(x_interval), max(x_interval))

        c = randint(min(c_interval), (max(c_interval))) * a
        b = c - a * x
        equation = self.format_equation(a, b, shuffle_the_equation=shuffle_the_equation)
        sentence_chosen = choice(sentences)

        return {'question': sentence_chosen.format(equation=equation, c=c),
                'answer': x}

    def q_give_factorisation_form(self, shuffle_the_equation: bool = True) -> dict:
        sentences = ['Donner la forme factorisé du polynôme f(x)=', 'Exprimer sous forme de produit f(x)=']
        a = randint(-1, 1)
        while a == 0:
            a = randint(-1, 1)
        #  easy root of polynomial equation
        x1 = randint(-1, 1)
        while x1 == 0:
            x1 = randint(-1, 1)
        x2 = choice([randint(-10, -2), randint(2, 10)])
        #  x1, x2 = min(x1, x2), max(x1, x2)
        b = -(x1 + x2) * a
        c = x1 * x2 * a

        expanded_equation = self.format_equation(a, b, c, shuffle_the_equation=shuffle_the_equation)
        factorised_equation = [(f'{self.format_equation(a, 0)[:-1]}(x{self.format_value(-x1, "")})'
                                f'(x{self.format_value(-x2, "")})'),
                               (f'{self.format_equation(a, 0)[:-1]}(x{self.format_value(-x2, "")})'
                                f'(x{self.format_value(-x1, "")})')
                               ]
        sentence_chosen = choice(sentences)
        return {'question': f'{sentence_chosen}{expanded_equation}',
                'answer': factorised_equation[0],
                'others_answers': factorised_equation[1:]}

    def q_calculate_discriminant(self):
        sentences = ['Combien vaut le discriminant dans', 'Calcule le discriminant de l\'équation',
                     'Delta est égal à combien dans']
        a = randint(-2, 2)
        b = randint(-5, 5)
        c = randint(-3, 3)
        while a == 0 or (b == 0 and c == 0):
            a = randint(-2, 2)
            b = randint(-5, 5)
            c = randint(-3, 3)
        equation = self.format_equation(a, b, c)
        delta = b ** 2 - 4 * a * c
        sentence_chosen = choice(sentences)

        return {'question': f'{sentence_chosen} {equation} ?',
                'answer': delta}

    def q_calculate_image(self):
        sentences = ['Combien vaut g({x}) avec g(x)={equation}',
                     'Calcule l\'image de {x} dans l\'équation {equation}=y',
                     'Donner l\'image de {x} avec f(x)={equation}']
        a = randint(-4, 4)
        b = randint(-6, 6)
        c = randint(-10, 10)

        x = randint(-2, 2)
        equation = self.format_equation(a, b, c, shuffle_the_equation=False)
        sentence_chosen = choice(sentences)

        return {'question': sentence_chosen.format(x=x, equation=equation),
                'answer': a * x ** 2 + b * x + c}

    @staticmethod
    def q_simple_calcul():
        sentences = ['Combien font {equation} ?',
                     '{equation}=?']
        if randint(1, 4):
            numbers = [randint(11, 99), 11]
            shuffle(numbers)
            a, b = numbers
        else:
            a = randint(0, 12)
            b = randint(2, 10)
        answer = a * b
        sentence = choice(sentences)
        return {'question': sentence.format(equation=f'{a}x{b}'),
                'answer': answer}


class Arithmetic(Questions):
    def __init__(self):
        super().__init__(self)

    @staticmethod
    def prime_number_interval(min_number: int = 5, max_number: int = 50) -> list[int]:
        """
        Return all prime number in the interval [min_number ; max_number]
        :param min_number:
        :param max_number:
        :return: list of all prime number in the interval
        """

        #  Algorithm that we saw in math last year
        def is_prime(n: int) -> bool:
            #  First check if the number is lower or equal than 1
            if n <= 1:
                return False
            #  We check if we can divide our number by all numbers between 2 and sqrt(n)+1
            #  2 because every number can be divided by 1, and sqrt(n)+1 because no one number
            #  greater can divide n, don't need to search more
            for i in range(2, int(n ** 0.5) + 1):
                #  If we can divide, this is not a prime number
                if n % i == 0:
                    return False
            #  else, this is a prime number
            return True

        # All prime number in the interval
        prime_numbers = [num for num in range(min_number, max_number + 1) if is_prime(num)]

        return prime_numbers

    def generate_friendly_number(self, length: int = 4) -> int:
        prime_number = self.prime_number_interval(2, 7)
        weight = [length - index for index in range(length)]

        list_number_chosen = choices(prime_number, weights=weight, k=randint(2, 3))
        number = 1
        for i in list_number_chosen:
            number *= i
        return number

    @staticmethod
    def q_perfect_square(min_number: int = 5, max_number: int = 12) -> dict[str, bool]:
        """
        Ask if a number is a perfect square or not, so the answer is a boolean.
        Generate a number in the interval [min_number**2 ; max_number**2]

        :param min_number: The lower square number that can be chosen, but this number is squared (i**2)
        :rtype: int
        :param max_number: The greatest square number that can be chosen, but this number is squared (i**2)
        :rtype: int

        :return: dictionary with "question" and "answer" keys
        """

        perfect_square = [number ** 2 for number in range(min_number, max_number + 1)]
        is_perfect_square = choice([True, False])
        if is_perfect_square:
            number_generated = choice(perfect_square)
        else:
            number_generated = randint(min_number ** 2, max_number ** 2)
            while number_generated in perfect_square:
                number_generated = randint(min_number ** 2, max_number ** 2)

        return {'question': f'Le nombre {number_generated} est-il un carré parfait ? (Oui/Non)',
                'answer': is_perfect_square}

    def q_greatest_lower_common_divisor_multiple(self) -> dict[str, int]:
        discipline: tuple = choice([('plus grand diviseur commun', gcd), ('plus petit multiple commun', lcm)])
        n1 = self.generate_friendly_number()
        n2 = self.generate_friendly_number()

        answer: int = discipline[1](n1, n2)
        return {'question': f'Quel est le {discipline[0]} de {min(n1, n2)} et {max(n1, n2)} ?',
                'answer': answer}

    def q_prime_number(self, min_number: int = 10, max_number: int = 40) -> dict[str, bool]:
        """
        Ask if a number is a prime number or not, the answer is also a boolean.
        Generate a number in the interval [min_number ; max_number]

        :param min_number: The lowest number that can be chosen
        :rtype: int
        :param max_number: The greatest number that can be chosen
        :rtype: int

        :return: dictionary with "question" and "answer" keys
        """

        prime_number = self.prime_number_interval(min_number, max_number)
        is_prime = choice([True, False])
        if is_prime:
            number_generated = choice(prime_number)
        else:
            number_generated = randint(min_number, max_number)
            while number_generated in prime_number or number_generated % 2 == 0:
                number_generated = randint(min_number, max_number)

        return {'question': f'{number_generated} est-il un nombre premier ? (Oui/Non)',
                'answer': is_prime}

    @staticmethod
    def q_convert_bin_to_dec(min_number: int = 5, max_number: int = 32) -> dict[str, int]:
        number = randint(min_number, max_number)
        return {'question': f'Convertis le nombre binaire {str(bin(number))[2:]} en décimal',
                'answer': number}

    @staticmethod
    def q_is_divisible_by_a_number(min_number: int = 100, max_number: int = 10000) -> dict[str, bool]:
        #  numbers for which we know the divisibility criteria
        list_divisible = [3, 5, 6, 10]
        is_divisible = choice([True, False])

        k = choice(list_divisible)

        if is_divisible:
            final_number = k * randint(int(min_number / k), int(max_number / k))
        else:
            final_number = randint(min_number, max_number)
            while final_number % k == 0:
                final_number = randint(min_number, max_number)

        return {'question': f'Est-ce que {final_number} est divisible par {k} ? (Oui/Non)',
                'answer': is_divisible}


class Geometry(Questions):
    prefix = {
        'shapes': {
            'pent': 5,
            'hex': 6,
            'oct': 8,
            'dec': 10,
        },
        'units': ["kilo", "hecto", "deca", "", "deci", "centi", "milli"]}

    def __init__(self):
        super().__init__(self)

    @staticmethod
    def format_le_before_word(determiner: str, word_after: str):
        assert determiner == 'le' or determiner == 'la'
        for i in word_after:
            if i == 'h':
                pass
            elif i in ['a', 'e', 'i', 'o', 'u', 'y']:
                return 'l\''
            else:
                return determiner + " "

    @staticmethod
    def pythagorean_triplet(interval: tuple = (1, 13)):
        assert min(interval) > 0
        result = []
        for i in range(min(interval), max(interval) + 1):
            for j in range(min(interval), max(interval) + 1):
                if int((i ** 2 + j ** 2) ** 0.5) == (i ** 2 + j ** 2) ** 0.5 and int((i ** 2 + j ** 2) ** 0.5) <= max(
                        interval):
                    is_new_triplet = True
                    for triplet in result:
                        if min(triplet) == min(i, j) and max(triplet) == int((i ** 2 + j ** 2) ** 0.5):
                            is_new_triplet = False
                    if is_new_triplet:
                        result.append((i, j, int((i ** 2 + j ** 2) ** 0.5)))
        return result

    def q_how_many_side(self):
        sentences = ['Combien de côté un {polygone_prefix}agone possède t\'il ?',
                     'Un {polygone_prefix}agone, c\'est un polygone à comien de coté ?',
                     'Nombre de coté d\'un {polygone_prefix}agone ?']
        sentence_chosen: str = choice(sentences)
        prefix = choice(list(self.prefix['shapes']))
        return {'question': sentence_chosen.format(polygone_prefix=prefix),
                'answer': self.prefix['shapes'][prefix]}

    @staticmethod
    def q_angles_sum():
        interrogative_word = ['Trouve', 'Détermine', 'Quelle est', 'Calcule']
        sentence = '{0} la sommes des angles d\'un {1}'
        geometric_shapes_with_angles = [('triangle', ['180°', '180', 'pi']),
                                        ('carré', ['360°', '360', '2pi', '2*pi']),
                                        ('pentagone', ['540°', '540', '3pi', '3*pi'])]
        shape_chosen = choice(geometric_shapes_with_angles)
        question = sentence.format(choice(interrogative_word), shape_chosen[0])
        return {'question': question,
                'answer': shape_chosen[1][0],
                'others_answers': shape_chosen[1][1:]}

    def q_triangle_nature(self, triangle_side_value_interval: tuple = (3, 10)):
        assert min(triangle_side_value_interval) > 0
        assert abs(max(triangle_side_value_interval) - min(triangle_side_value_interval)) >= 2
        assert min(triangle_side_value_interval) != max(triangle_side_value_interval)

        def generate_random_side(value_interval: tuple = triangle_side_value_interval, /):
            return (randint(min(value_interval), max(value_interval)),
                    randint(min(value_interval), max(value_interval)),
                    randint(min(value_interval), max(value_interval)))

        sentences = ['Est-ce que le triangle de coté {c1}, {c2} et {c3} est {triangle_type} ?',
                     'Les côtés {c1}, {c2} et {c3} permettent-ils de former un triangle {triangle_type} ?',
                     'Un triangle de côtés {c1}, {c2} et {c3} peut-il être {triangle_type} ?']

        is_a_particular_triangle = choice([True, False])
        triangle_type = choice(['isocèle', 'rectangle', 'équilateral'])

        sentence_chosen: str = choice(sentences)
        if triangle_type == 'équilateral':
            if is_a_particular_triangle:
                c1 = randint(min(triangle_side_value_interval), max(triangle_side_value_interval))
                c2 = c3 = c1
            else:
                c1, c2, c3 = generate_random_side()
                while c1 == c2 == c3:
                    c1, c2, c3 = generate_random_side()
        elif triangle_type == 'isocèle':
            if is_a_particular_triangle:
                c1 = randint(min(triangle_side_value_interval), max(triangle_side_value_interval))
                c2 = randint(min(triangle_side_value_interval), max(triangle_side_value_interval))
                while c1 == c2:
                    c2 = randint(min(triangle_side_value_interval), max(triangle_side_value_interval))
                c3 = choice([c1, c2])
            else:
                c1, c2, c3 = generate_random_side()
                while c1 == c2 or c2 == c3 or c1 == c3:
                    c1, c2, c3 = generate_random_side()
        elif triangle_type == 'rectangle':
            if is_a_particular_triangle:
                try:
                    c1, c2, c3 = choice(self.pythagorean_triplet(interval=triangle_side_value_interval))
                except IndexError:
                    c1, c2, c3 = generate_random_side()
                    is_a_particular_triangle = False
                    while c1 == c2 or c2 == c3 or c3 == c1:
                        c1, c2, c3 = generate_random_side()

                side_value = [c1, c2, c3]
                shuffle(side_value)
                c1, c2, c3 = side_value
            else:
                c1, c2, c3 = generate_random_side()
                a, b, c = sorted([c1, c2, c3])
                while a ** 2 + b ** 2 == c ** 2:
                    c1, c2, c3 = generate_random_side()
                    a, b, c = sorted([c1, c2, c3])
        else:
            c1, c2, c3 = generate_random_side()

        return {'question': sentence_chosen.format(c1=c1, c2=c2, c3=c3, triangle_type=triangle_type),
                'answer': is_a_particular_triangle}

    @staticmethod
    def generate_area_or_volume_value(product_interval: tuple, /, number_of_value: int = 2):
        prime_values = []
        """ generate n value whose product is included in a defined interval

        :param number_of_value: choose how many value will be returns
        :param product_interval:
        :return: n value in a tuple
        """
        min_product, max_product = product_interval
        for i in range(min_product, max_product + 1):
            prime_value_result = decomposition_prime_factor(i)
            if len(prime_value_result) >= number_of_value:
                prime_values.append(prime_value_result)
        chosen = choice(prime_values)
        return chosen

    @staticmethod
    def separate_in_two_list(list_of_values: list):
        length = len(list_of_values)
        assert length >= 2
        shuffle(list(list_of_values))
        split = (randint(2, length - 1) if length != 2 else 2) - 1
        return list_of_values[split:], list_of_values[:split]

    @staticmethod
    def prod(iterable: list or tuple):
        result = 1
        for i in iterable:
            result *= i
        return result

    def q_volume(self, result_interval: tuple = (4, 60)):
        sentences = [
            'Quel est {determiner1}{area_or_volume} {determiner2}{shape} de base {b}{unit}{exponent} et de hauteur '
            '{h}{unit} ?',
            'Si la base fait {b}{unit}{exponent} et la hauteur {h}{unit}, quel est {determiner1}{area_or_volume} '
            '{determiner2}{shape} ?',
            'Si un {shape} a une base de {b}{unit}{exponent} et une hauteur de {h}{unit}, quel est {determiner1}'
            '{area_or_volume} ?'
        ]

        sentence_chosen = choice(sentences)
        unit = choice(['dam', 'm', 'dm', 'cm', 'mm'])

        shapes = {
            'volume': {
                'pyramide': lambda b, h: b * h / 3,
                'parallélépipède rectangle': lambda b, h: b * h
            },
            'aire': {
                'triangle': lambda b, h: b * h / 2,
                'rectangle': lambda b, h: b * h,
                'trapèze': lambda b, h: b * h,

            }
        }
        area_or_volume = choice(list(shapes))
        shape_chosen = choice(list(shapes[area_or_volume]))
        determiner1 = self.format_le_before_word('le', area_or_volume)
        determiner2 = f'de {self.format_le_before_word("la", shape_chosen)}' if shape_chosen == 'pyramide' else 'du '
        if shape_chosen == 'pyramide':
            min_value, max_value = result_interval
            base, height = self.separate_in_two_list(
                self.generate_area_or_volume_value((min_value // 3, max_value // 3))
            )
            if choice([True, False]):
                base += [3]
            else:
                height += [3]
        elif shape_chosen == 'triangle':
            min_value, max_value = result_interval
            base, height = self.separate_in_two_list(
                self.generate_area_or_volume_value((min_value // 2, max_value // 2))
            )
            if choice([True, False]):
                base += [2]
            else:
                height += [2]
        else:
            base, height = self.separate_in_two_list(
                self.generate_area_or_volume_value(result_interval)
            )
        base = self.prod(base)
        height = self.prod(height)
        #  We can put "int" because the values generated makes only integers, not float.
        volume = int(shapes[area_or_volume][shape_chosen](base, height))
        exponent = "²" if unit else ""
        return {'question': sentence_chosen.format(determiner1=determiner1, area_or_volume=area_or_volume,
                                                   shape=shape_chosen,
                                                   b=base, h=height, unit=(" " + unit if unit != "" else unit),
                                                   exponent=exponent,
                                                   determiner2=determiner2),
                'answer': f'{volume}{unit}{"^3" if unit != "" else ""}',
                'others_answers': [f'{volume}{unit}{"**3" if unit != "" else ""}',
                                   f'{volume}{unit}{"³" if unit != "" else ""}']}

    @staticmethod
    def write_number(number: int or str):
        result = ""
        number = str(number)
        if "." in number:
            part1, part2 = number.split(".")
        else:
            part1, part2 = number, ""
        for index, n in enumerate(part1):
            result += n
            if (len(part1) - 1 - index) % 3 == 0 and len(part1) - 1 - index != 0:
                result += " "
        if part2 != "":
            result += "."
        for index, n in enumerate(part2):
            result += n
            if (index + 1) % 3 == 0 and len(part2) - 1 - index != 0:
                result += " "
        return result

    def q_convert_unit(self, answer_interval: tuple = (1, 100)):
        assert len(answer_interval) == 2 and [min(answer_interval), max(answer_interval)] == list(answer_interval) and \
               min(answer_interval) > -1
        assert isinstance(answer_interval[0], int) and isinstance(answer_interval[1], int)

        units_type = choice(['mètres', 'litres', 'grammes'])

        sentences = ['Convertis {number} {unit1} en {unit2}.',
                     '{number} {unit1} font combien de {unit2} ?',
                     'Quel est la longueur d\'une droite de {number} {unit1} en {unit2} ?']
        unit1_index = randint(0, len(self.prefix['units']) - 1)
        unit2_index = randint(0, len(self.prefix['units']) - 1)
        while unit1_index == unit2_index:
            unit2_index = randint(0, len(self.prefix['units']) - 1)
        unit1 = self.prefix['units'][unit1_index] + units_type
        unit2 = self.prefix['units'][unit2_index] + units_type
        comma_unit = unit2_index - unit1_index

        number_length = randint(ceil(log10(min(answer_interval))), ceil(log10(max(answer_interval))))
        while number_length == 0:
            number_length = randint(ceil(log10(min(answer_interval))), ceil(log10(max(answer_interval))))

        def generate_number(length):
            #  I want to have the same chance to generate a two-length number as a one-length number so :
            result = 0
            for i in range(length):
                if i == 0 or i == length - 1:
                    result += randint(1, 9) * 10 ** i
                else:
                    if choice([True, False]):
                        result += randint(1, 9) * 10 ** i
            return result

        answer = generate_number(number_length)
        while answer < min(answer_interval) or answer > max(answer_interval):
            answer = generate_number(number_length)

        number = answer / 10 ** comma_unit
        if number == int(number):
            number = int(number)
        sentence = choice(sentences)

        return {'question': sentence.format(number=self.write_number(number), unit1=unit1, unit2=unit2),
                'answer': answer, 'others_answers': f"{answer}{unit2}"}


class Trigonometry(Questions):
    pi = 'π'  # or 'pi' if 'π' doesn't work on the terminal
    angles_base = {
        'value': {
            'radian': ['0', f'{pi}/6', f'{pi}/4', f'{pi}/3'],
            'degree': ['0°', '30°', '45°', '60°'],
        },
        'result': {
            'cos': [1, 3 ** 0.5 / 2, 2 ** 0.5 / 2, 0.5],
            'sin': [0, 0.5, 2 ** 0.5 / 2, 3 ** 0.5 / 2]
        }
    }
    relation = {
        'cosinus': 'adjacent/hypothénuse',
        'sinus': 'opposé/hypothénuse',
        'tangente': 'opposé/adjacent'
    }

    def __init__(self):
        super().__init__(self)
        self.angles = self.get_extended_angles(start=-4, stop=4)

    def convert_degree_into_radian(self, degree: str):
        result: str = ''
        value = int(degree[:-1])

        #  simplification :
        prime_factor_value = decomposition_prime_factor(value)
        prime_factor_180 = [2, 2, 3, 3, 5]
        to_remove = []
        for value in prime_factor_value:
            if value in prime_factor_180:
                prime_factor_180.remove(value)
                to_remove.append(value)
        if not to_remove:
            return '0'
        for item_to_remove in to_remove:
            prime_factor_value.remove(item_to_remove)
        product = prod(prime_factor_value)
        if abs(product) == 1:
            result += f'{"-" if product < 0 else ""}{self.pi}'
        else:
            result += f'{product}{self.pi}'
        product2 = prod(prime_factor_180)
        if product2 == 1:
            pass
        else:
            result += f'/{product2}'

        return result

    @staticmethod
    def add_angles(angle_degree: str, delta_in_degree: int):
        value = int(angle_degree[:-1])
        value += delta_in_degree
        value = str(value) + '°'
        return value

    def get_extended_angles(self, *, start: int = -2, stop: int = 2):
        data = {'value': {'radian': [], 'degree': []},
                'result': {'cos': [], 'sin': []}}
        for i in range(start, stop):
            for value in self.angles_base['value']['degree']:
                new_angle = self.add_angles(value, 90 * i)
                data['value']['degree'].append(new_angle)
                data['value']['radian'].append(self.convert_degree_into_radian(new_angle))
                data['result']['cos'].append(round(cos(radians(int(new_angle[:-1]))), 5))
                data['result']['sin'].append(round(sin(radians(int(new_angle[:-1]))), 5))

        new_angle = f'{90 * stop}°'
        data['value']['degree'].append(new_angle)
        data['value']['radian'].append(self.convert_degree_into_radian(new_angle))
        data['result']['cos'].append(round(cos(radians(int(new_angle[:-1]))), 5))
        data['result']['sin'].append(round(sin(radians(int(new_angle[:-1]))), 5))
        return data

    def get_random_values(self):
        trigo_function_chosen = choice(list(self.angles['result']))
        options = []
        for index, result in enumerate(self.angles['result'][trigo_function_chosen]):
            if result == round(result, 2):
                options.append((index, result))
        index_chosen, result_chosen = choice(options)
        value = self.angles['value'][choice(list(self.angles['value']))][index_chosen]
        if int(result_chosen) == result_chosen:
            result_chosen = int(result_chosen)
        return trigo_function_chosen, value, result_chosen

    def q_trigo_formula(self):
        sentences = [
            'Dans un rectangle, {determinant} {trigo_function} est-il le rapport entre l\'{side1} et l\'{side2} ?',
            '{determinant} {trigo_function} d’un angle est-il l\'{side1} sur l’{side2} ?',
            'Dans un rectangle, {determinant} {trigo_function} est-il égal à l\'{side1}/l\'{side2} ?'
        ]
        trigo_function = choice(list(self.relation))
        result = choice([True, False])
        if result:
            side1, side2 = self.relation[trigo_function].split("/")
        else:
            while True:
                possibilities = []
                for i in self.relation:
                    side1, side2 = self.relation[i].split("/")
                    if side1 not in possibilities:
                        possibilities.append(side1)
                    if side2 not in possibilities:
                        possibilities.append(side2)
                side1 = choice(possibilities)
                possibilities.remove(side1)
                side2 = choice(possibilities)
                #  Check if it's unfortunately the good result.
                if [side1, side2] != self.relation[trigo_function].split('/'):
                    break

        sentence = choice(sentences)
        determinant = 'le' if trigo_function in ['sinus', 'cosinus'] else 'la'
        return {'question': sentence.format(determinant=determinant, trigo_function=trigo_function,
                                            side1=side1, side2=side2),
                'answer': result}

    def q_found_value(self):
        sentences = ['Quelle est la valeur de {trigo_function}({value}) ?',
                     'Quelle valeur doit-on attribuer à {trigo_function}({value}) ?',
                     'Quel est le résultat de {trigo_function}({value}) dans l’unité cercle ?']
        trigo_function, value, result = self.get_random_values()

        sentence = choice(sentences).format(trigo_function=trigo_function, value=value)
        return {'question': sentence,
                'answer': result, 'others_answers': ['1/2' if result == 0.5 else None]}

    def q_is_the_same_value(self):
        sentences = ['{angle1} est-il confondu avec {angle2} dans le cerle trigonométrique ?',
                     '{angle1} et {angle2} ont-ils la même position sur le cercle trigo ?',
                     'Peut-on superposer {angle1} et {angle2} dans le cercle trigo d\'unité 1 ?']
        angle1 = choice(self.angles_base['value']['degree'])
        answer = choice([True, False])
        k = randint(-1, 1)
        while k == 0:
            k = randint(-1, 1)
        if answer:
            angle2 = self.add_angles(angle1, 360 * k)
        else:
            while True:
                angle2 = choice(self.angles_base['value']['degree'])
                if angle1 != angle2:
                    break
        angles = [angle1, angle2]
        shuffle(angles)
        angle1, angle2 = angles
        if choice([True, False]):
            angle1 = self.convert_degree_into_radian(angle1)

        if choice([True, False]):
            angle2 = self.convert_degree_into_radian(angle2)

        sentence = choice(sentences)
        return {'question': sentence.format(angle1=angle1, angle2=angle2),
                'answer': answer}

    def q_convert_value_into_degree_or_radian(self):
        sentences = ['{value} {unit1} correspond à quelle valeur en {unit2} ?',
                     'Combien de {unit2} représente {value} {unit1} ?',
                     '{value} {unit1} donne combien en {unit2} ?',
                     'Quelle est l’équivalence exacte en {unit2} de {value} {unit1} ?']

        degree_value = choice(self.angles['value']['degree'])
        radian_value = self.convert_degree_into_radian(degree_value)
        values = [(degree_value, 'degrés'), (radian_value, 'radians')]
        shuffle(values)

        value, unit1 = values[0]
        answer, unit2 = values[1]
        sentence = choice(sentences)
        others_answers = []
        if unit2 == 'radians':
            others_answers.append(answer.replace(self.pi, "pi"))
            others_answers.append(answer.replace("pi", "π"))
        elif unit2 == 'degrés':
            others_answers.append(value[:-1])
        return {'question': sentence.format(value=value, unit1=unit1, unit2=unit2),
                'answer': answer, 'others_answers': others_answers}


def generate_question(subjects: list[str] = '*') -> dict:
    """
    This is the main function that will be called everytime.

    Take randomly a question in the subject that is in the parameters.
    In fact, this function don't do complicated things, it's just a link
    with the others functions in each math discipline.

    :param subjects: Trigonometry, Arithmetic, Geometry, Algebra or all of these ("*")
    :rtype subjects: list of str or just a str ("*")
    :return: The question, his correct answer and the subject that was chosen.
    """
    #  I link "manually" word with the function that generate question about the math discipline.
    #  The value in front of the key is function but not called yet.
    #  I could have called the functions, but it's to optimise, I will call only if it's chosen
    all_subjects = {'Trigonometry': Trigonometry(),
                    'Arithmetic': Arithmetic(),
                    'Geometry': Geometry(),
                    'Algebra': Algebra()}

    subjects = [subject for subject in subjects if subject in all_subjects.keys()]

    if not subjects:
        subjects = list(all_subjects)
    k = [all_subjects[subject_name].get_number_of_questions() for subject_name in subjects]
    random_subject = choices(subjects, weights=k)[0]

    #  returns a dictionary with the following keys "question" ; "answer" ; "subject"
    return all_subjects[random_subject].generate()


def verify_answer(question_data, answer):
    is_correct = False
    if isinstance(question_data['answer'], bool):
        if isinstance(answer, str):
            return (answer == 'oui' or answer == 'yes' or
                    answer == '1' or answer == 'true')

    if isinstance(question_data['answer'], bool) or isinstance(question_data['answer'], str):
        if answer == question_data['answer']:
            is_correct = True
    elif isinstance(question_data['answer'], int):
        if answer == str(question_data['answer']):
            is_correct = True

    if not is_correct:
        others_good_answers = question_data.get('others_answers')
        if others_good_answers:

            for other_good_answer in others_good_answers:
                if answer == other_good_answer:
                    is_correct = True
                    break

    return is_correct


def calculate_score(score_details: dict, /) -> tuple[int, int]:
    score, total = 0, 0
    for subject in score_details:
        if 'time' not in subject:
            score, total = score + score_details[subject]['correct'], total + score_details[subject]['total']
    return score, total


def format_time(*, score_details: dict = None, time_to_draw: int = None):
    if score_details:
        duration = round(abs(score_details['start time'] - score_details['end time']), 2)
    elif time_to_draw:
        duration = time_to_draw
    else:
        raise "score_details or time cannot be empty"
    return (f'{int(duration // 60) if duration >= 60 else ""}{"min" * (duration >= 60)}'
            f'{" " * (duration % 60 != 0 and duration >= 60)}{round(duration % 60, 1) if duration % 60 != 0 else ""}'
            f'{"s" * (duration % 60 != 0)}')


def draw_score(score_details: dict, /, *, draw_score_details: bool = False):
    score_details['end time'] = time()
    score, total = calculate_score(score_details)
    try:
        score_sentence = f'Votre score est de {int((score / total) * 100)}% ({score}/{total})'
    except ZeroDivisionError:
        return
    score_sentence_length = len(score_sentence)
    print("".center(score_sentence_length, '─').center(60))
    print(score_sentence.center(60))
    print("".center(score_sentence_length, '─').center(60))
    if draw_score_details:
        for subject in score_details:
            if 'time' not in subject:
                print(f'    {subject}:  {score_details[subject]["correct"]}/{score_details[subject]["total"]}')
    print(format_time(score_details=score_details).center(score_sentence_length - 10, '─').center(60))
    print()


def ask_question(question_data: dict, /, column_index: int = None):
    question_data = question_data
    text = (f'{((str(column_index + 1) + "-") if isinstance(column_index, int) else " ").ljust(4, " ")}'
            f'{question_data["question"]}')
    user_response = input(text.ljust(59, ' ') + ' > ').lower().replace(" ", "")
    return user_response


def several_questions_mode(number_of_questions: int = 40, /, subjects: list[str] = '*',
                           draw_score_details: bool = True) -> None:
    score_details_dict = {subject: {'correct': 0, 'total': 0} for subject in subjects}
    score_details_dict['start time'] = time()

    for i in range(number_of_questions):
        question_generated = generate_question(subjects=subjects)

        try:
            user_response = ask_question(question_generated, column_index=i)
            if user_response in ['stop', 'quit', 'exit', 'break']:
                print()
                break
        except KeyboardInterrupt:
            print()
            break
        else:
            score_details_dict[question_generated['subject']]['total'] += 1

        is_correct = verify_answer(question_generated, user_response)

        if is_correct:
            score_details_dict[question_generated['subject']]['correct'] += 1
        else:
            try:
                input(f'La réponse attendu était {str(question_generated["answer"])}'.rjust(59))
            except KeyboardInterrupt:
                print()

    draw_score(score_details_dict, draw_score_details=draw_score_details)


def run(*, display_title: bool = True, number_of_questions_per_series: int = 8) -> None:
    subject = [('Algèbre', 'Algebra'), ('Trigonométrie', 'Trigonometry'),
               ('Geométrie', 'Geometry'), ('Arithmétique', 'Arithmetic')]

    total_length = sum([len(french_name) + 5 for french_name, english_name in subject])

    presentation_message = f"""
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ▄▄▄▄███▄▄▄▄      ▄████████     ███        ▄█    █▄        ████████▄   ███    █▄   ▄█   ▄███████▄   │
│▄██▀▀▀███▀▀▀██▄   ███    ███ ▀█████████▄   ███    ███       ███    ███  ███    ███ ███  ██▀     ▄██  │
│███   ███   ███   ███    ███    ▀███▀▀██   ███    ███       ███    ███  ███    ███ ███▌       ▄███▀  │
│███   ███   ███   ███    ███     ███   ▀  ▄███▄▄▄▄███▄▄     ███    ███  ███    ███ ███▌  ▀█▀▄███▀▄▄  │
│███   ███   ███ ▀███████████     ███     ▀▀███▀▀▀▀███▀      ███    ███  ███    ███ ███▌   ▄███▀   ▀  │
│███   ███   ███   ███    ███     ███       ███    ███       ███    ███  ███    ███ ███  ▄███▀        │
│███   ███   ███   ███    ███     ███       ███    ███       ███  ▀ ███  ███    ███ ███  ███▄     ▄█  │
│ ▀█   ███   █▀    ███    █▀     ▄████▀     ███    █▀         ▀██████▀▄█ ████████▀  █▀    ▀████████▀  │
├{'─' * total_length}┬{'─' * (100 - total_length)}┘
│""" if display_title else f"┌{'─' * total_length}┐\n│"

    for i, value in enumerate(subject):
        french_name, _ = value
        presentation_message += f" {i + 1} {french_name}  "
    presentation_message += (f"| Entrez les index des matières à "
                             f"\n└{'─' * total_length}┘ exclure, sinon [ENTER] pour tout.")
    print(presentation_message)

    running = True
    while running:
        try:
            user_input = input('index: '.rjust(64, ' '))
            if user_input in ['quit', 'exit', 'stop']:
                break
            subject_chosen = []
            for i, value in enumerate(subject):
                _, english_name = value
                if str(i + 1) not in user_input:
                    subject_chosen.append(english_name)

        except KeyboardInterrupt:
            print()
            print('└' + '  Au revoir  '.center(101, "─") + '┘')
            break

        several_questions_mode(number_of_questions_per_series, subjects=subject_chosen)


def test(*, iteration_number: int = 1_000) -> None:
    """
    function to test if everything is working. actually, it only generates a lot of questions,
    but we can see if a function bug or not.
    :param iteration_number:
    :return:
    """
    for _ in range(iteration_number):
        data = generate_question()
        if not data.get('questions') or not data.get('answer') or not data.get('subject'):
            raise 'Erreur : ' + data

    print("Algebra : ", Algebra().get_number_of_questions(), 'kind of questions')
    print("Geometry : ", Geometry().get_number_of_questions(), 'kind of questions')
    print("Arithmetic : ", Arithmetic().get_number_of_questions(), 'kind of questions')
    print("Trigonometry : ", Trigonometry().get_number_of_questions(), 'kind of questions')


if __name__ == '__main__':
    #  test()
    run(display_title=False, number_of_questions_per_series=20)