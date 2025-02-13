"""
Main.py | Max DECKMYN | NSI QUIZ

NB:
I'll put all my text, variable etc... in English because this is the better way to have a readable and
maintainable script, It's possible that I do English mistake because I'm not excellent at it and I don't
want to use translation too much. BUT the questions and answers are in French because the users that we'll play
to my quiz are French.
I will split the quiz in a different subject, one for each object.
All questions return a dictionary with everytime the following keys:
    question: text
    suggested_answer: list of text, integer or boolean values
    index_answer: integer
    subject: text
This is a MCQ (QCM in French), so answer is A, B, C, or D (actually it depends on the number of suggested answer) and
suggested answer is a list of several possible answers

My Personal To Do List:
  Currently
  - Algebra, (q_calculate_image): rework on the suggestions answers because the function is really complicated
  but doesn't work very well, so I have to re-think about that.
  - Only four kinds of questions, I can do more...

  Target
  - Timer to calculate score
  - See where are the mistake at the end of the quiz
  - Show correction (I mean, the way to resolve a question)

  Goal
  - use a graphical engine in the terminal to use color and funnier functionality
  - create better test, but I don't see how I can do that

"""
from tqdm import tqdm
from typing import Optional, Union
from random import randint, choice, shuffle, choices, random
from math import ceil, sin, cos, radians, prod, gcd, lcm, floor, log10


pi = 'π'  # or 'pi' if 'π' doesn't work
sqrt = '√({number})'  # or 'sqrt({number})' if it doesn't draw on the terminal


class Latex:
    pi = '\\pi'
    sqrt = '\\sqrt{{{n}}}'  # sqrt.format(number=6) returns \sqrt{6} and this is the latex format
    frac = "\\frac{{{a}}}{{{b}}}"
    degree = '^\\circ'
    times = "\\times"
    delta = "\\Delta"
    in_set = "\\in"
    Z = "\\mathbb{Z}"
    cos = "\\cos"
    sin = "\\sin"


def decomposition_prime_factor(n: int) -> list[int]:
    """
    script found at :
    https://www.infinimath.com/espaceeducation/tangenteeducation/articles/TE15/FacteursPremiers.pdf
    and I modify only a few lines
    :param n: number
    :type; int
    :return: returns the list of prime numbers decomposing a number (n)
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


assert decomposition_prime_factor(42) == [2, 3, 7]
assert decomposition_prime_factor(-28) == [-1, 2, 2, 7]
assert decomposition_prime_factor(0) == []


def convert_value_to_latex(value: Union[int, str, float], center: bool = False):
    """
    returns the latex format for a single value
    """
    return f'${"$" if center else ""}{value}{"$" if center else ""}$'


assert convert_value_to_latex(5) == "$5$"
assert convert_value_to_latex("f(x)=5x+2", center=True) == "$$f(x)=5x+2$$"


def convert_degree_into_radian(degree: str, latex: bool = False) -> str:
    """
    return the radian value of a degree angle
    :param latex: true or false, if we want to work with the latex format
    :param degree: have to end with "°"
    :return: radian value of the angle
    """
    result: str = ''
    if latex:
        if degree.endswith(Latex.degree):
            value = int(degree[:-len(Latex.degree)])
        else:
            raise ValueError(f'The argument "degree" has to end with the following characters "{Latex.degree}".'
                             f' (degree={degree})')
    else:
        if degree.endswith('°'):
            value = int(degree[:-1])
        else:
            raise ValueError(f'The argument "degree" has to end by "°". (degree={degree})')
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
    sign = "-" if product < 0 else ""
    #  case where the product is 1 ou -1, we don't draw 1π or -1π but just π or -π
    if abs(product) == 1:
        a = Latex.pi if latex else pi
    else:
        a = f"{abs(product)}{Latex.pi if latex else pi}"
    b = prod(prime_factor_180)
    if b == 1:
        return f"{sign}{a}"
    else:
        if latex:
            return f"{sign}{Latex.frac.format(a=a, b=b)}"
        else:
            return f"{sign}{a}/{b}"


assert convert_degree_into_radian("-50^\\circ", latex=True) == "-\\frac{5\\pi}{18}"
assert convert_degree_into_radian("-45°", latex=False) == f"-{pi}/4"


def generate_number_without_value(interval: tuple = (-10, 10), *, forbidden_value: Union[int, list] = 0) -> int:
    """
    generates a random number from an interval without a specific value. if you don't want to remove value from
    the interval, you just have to put a forbidden value that is not into the interval.

    :return: int from the interval
    """
    value = randint(min(interval), max(interval))
    if isinstance(forbidden_value, list) or isinstance(forbidden_value, tuple):
        #  Check if the forbidden values are the only possibilities
        #  (this is hard to understand but trust me, easy to make)
        assert not set([i for i in range(min(interval), max(interval) + 1)]).issubset(set(forbidden_value))

        while value in forbidden_value:
            value = randint(min(interval), max(interval))
    elif isinstance(forbidden_value, int):
        #  We check if the forbidden value is not the only possibilities to the random choice
        assert not ((min(interval) == forbidden_value) and (max(interval) == forbidden_value))
        while value == forbidden_value:
            value = randint(min(interval), max(interval))
    return value


def shuffle_a_list(list_of_values: list) -> list:
    new_list = list_of_values.copy()
    shuffle(new_list)
    return new_list


class QuestionsMCQ:
    """
    This object allows you to pool functions that will be used by all the different subjects, such as the function to
     generate a question. All subjects will be child objects of this object.
     """

    def __init__(self, children_object: object):
        self.children_object = children_object
        self.children_object_name = self.children_object.__class__.__name__
        self.number_of_questions = self.get_number_of_questions()

    def generate(self, shuffle_true_or_false_answer: bool = False) -> dict:
        """
        Searches in the functions of the child object, all functions starting with the keyword "q_" and randomly picks a
        question. Then returns the result of this function. This makes it possible to make the link and generate a
        question among all those proposed by the child object.

        :return: Dictionary with "question", "suggested_answer", "answer" and "subject" keyword
        """
        questions_function = []
        #  list of all functions of the child object
        for function_name in dir(self.children_object):
            if function_name.startswith('q_'):
                #  if this is a function that starts with the keyword "q_", we add the instance of the function
                #  in the list where we'll randomly choose a function and called it
                questions_function.append(getattr(self.children_object, function_name))
        if not questions_function:
            raise ValueError(f"No function that begin by the keyword \"q_\" in the {self.children_object_name} object.")
        #  We randomly chose a question
        function_chosen = choice(questions_function)
        #  And call this function to get the question_data
        response: dict = function_chosen()

        if shuffle_true_or_false_answer:
            #  If this is a True or False answer, there are only two elements in the suggested answer list
            if len(response['suggested_answer']) == 2:
                answer = response['suggested_answer'][response['index_answer']]
                response['suggested_answer'] = shuffle_a_list(response['suggested_answer'])
                response['index_answer'] = response['suggested_answer'].index(answer)

        #  Then we add the subject key
        response['subject'] = self.children_object_name
        response['question_name'] = function_chosen.__name__[1:]  #  remove "q_"

        return response

    def get_number_of_questions(self) -> int:
        """
        Counts the number of functions starting with the keyword "q_". This is mainly for weighted draws.
        :return: Number of different questions the child object has
        """
        count = 0
        for attribute_name in dir(self.children_object):
            if attribute_name.startswith('q_'):
                count += 1
        return count


#  I split the questions in four math disciplines: Algebra, Arithmetic, Geometry and Trigonometry, so four objects


class Algebra(QuestionsMCQ):
    def __init__(self, latex: bool = False):
        super().__init__(self)
        self.latex: bool = latex

    @staticmethod
    def format_value(coefficient: int, variable: str = "") -> str:
        """
        This function takes the coefficient and the variable of a value, and returns the better way to write the value
        in a math equation.

        :param coefficient: The coefficient before the variable, e.g., "2x²" => "2"
        :param variable: the variable of the value, e.g., 5x³ => x³
        :return: the readable way to write a value in math equations, e.g., "-1x⁴" => "-x⁴"
        """
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
        Returns the writing of a polynomial expanded by taking as input the coefficients.
        Actually, this is a kind of format_value() but for a whole equation
        """
        equation = []
        #  only used if latex format is disable.
        exponents = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']

        for index, coefficient in enumerate(coefficients):
            exponent = len(coefficients) - 1 - index

            if exponent == 0:
                variable = ''
            elif exponent == 1:
                variable = 'x'
            else:
                variable = 'x'
                if self.latex:
                    variable += f"^{exponent}"
                else:
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

    #  Starting questions. I put many arguments in the function, but they are not required.
    #  This is only to manage the "settings" of a question.
    def q_calculate_antecedent(self, shuffle_the_equation: bool = True, *, a_interval: tuple = (-4, 4),
                               c_interval: tuple = (-2, 2), x_interval: tuple = (-10, 10)) -> dict:
        """
        Ask the user to found the antecedent of a first degree's function (it's the same as resolve an equation)
        """

        #  Check if arguments are valid (in this case, if a_interval is equal to (0, 0))
        assert a_interval != (0, 0)

        #  l means latex_format (If latex is equal to true, we add $$ in math formula)
        sentences = ['Quelle est la valeur de {l}x{l} dans {l}{equation}={c}{l} ?',
                     'Quelle est la solution de {l}{equation}={c}{l} ?',
                     'Donner l\'antécédent de {l}{c}{l} avec {l}f(x)={equation}{l}.']
        #  We randomly took a coefficient before the x
        a = generate_number_without_value(a_interval)
        x = generate_number_without_value(x_interval)
        c = generate_number_without_value(c_interval) * a

        b = int(c - a * x)  # We can put the int method because we know It can't be a float value (c and a*x are int)

        #  I generate others bad answers
        values = [x, int(-(c + b) / a)]  # Same here, we can put int because the result is always int
        # (c+b is k*a with k and an integers)
        if int(a * c + b) != x and a * c + b != -(c + b) / a:
            values.append(int(a * c + b))  # This value is to trap the user if he confuses image and antecedent
        else:
            generated_value = generate_number_without_value(x_interval, forbidden_value=values)
            values.append(generated_value)
        values.append(generate_number_without_value(x_interval, forbidden_value=values))
        values = shuffle_a_list(values)

        equation = self.format_equation(a, b, shuffle_the_equation=shuffle_the_equation)
        return {'question': choice(sentences).format(equation=equation, c=c, l="$" if self.latex else ""),
                'index_answer': values.index(x),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_calculate_image(self, shuffle_the_equation: bool = True, *, a_interval: tuple = (-4, 4),
                          b_interval: tuple = (-6, 6), c_interval: tuple = (-10, 10), x_interval: tuple = (-2, 2)):
        """
        ask user to calculate the image of a number, in first or second degrees equations
        """
        #  Check if the intervals are in the good order (e.g., [5, -5] is not correct but [-5, 5] is)
        assert a_interval == (min(a_interval), max(a_interval)) and b_interval == (min(b_interval), max(b_interval))
        assert c_interval == (min(c_interval), max(c_interval)) and x_interval == (min(x_interval), max(x_interval))

        sentences = ['Combien vaut {l}g({x}){l} avec {l}g(x)={equation}{l} ?',
                     'Calcule l\'image de {l}{x}{l} dans l\'équation {l}{equation}=y{l}.',
                     'Donner l\'image de {l}{x}{l} avec {l}f(x)={equation}{l}.']
        #  I do that to have 1 in 2 a chance to get a first degree equation
        a = choice([0, generate_number_without_value(a_interval)])
        b = generate_number_without_value(b_interval)
        c = randint(*c_interval)

        x = randint(*x_interval)
        answer = a * x ** 2 + b * x + c
        equation: str = self.format_equation(a, b, c, shuffle_the_equation=shuffle_the_equation)
        values = [answer]
        if a == 0:
            min_value = min(b * min(x_interval) + c, b * max(x_interval) + c)
            max_value = max(b * min(x_interval) + c, b * max(x_interval) + c)
        else:
            if min(x_interval) <= -b / (2 * a) <= max(x_interval):
                if a < 0:
                    max_value = ceil(- (b ** 2 - 4 * a * c) / 4 * a)
                    min_value = min(a * min(x_interval) ** 2 + b * min(x_interval) + c,
                                    a * max(x_interval) ** 2 + b * max(x_interval) + c)
                else:
                    max_value = max(a * min(x_interval) ** 2 + b * min(x_interval) + c,
                                    a * max(x_interval) ** 2 + b * max(x_interval) + c)
                    min_value = ceil(- (b ** 2 - 4 * a * c) / 4 * a)
            else:
                max_value = max(a * min(x_interval) ** 2 + b * min(x_interval) + c,
                                a * max(x_interval) ** 2 + b * max(x_interval) + c)
                min_value = min(a * min(x_interval) ** 2 + b * min(x_interval) + c,
                                a * max(x_interval) ** 2 + b * max(x_interval) + c)

        for _ in range(3):
            try:
                values.append(int(generate_number_without_value((min_value, max_value), forbidden_value=values)))
            except AssertionError:
                values.append(
                    int(generate_number_without_value((min_value - 4, max_value + 4), forbidden_value=values)))
        values = shuffle_a_list(values)
        return {'question': choice(sentences).format(equation=equation, x=x, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_give_factorisation_form(self, shuffle_the_equation: bool = True) -> dict:
        """
        Ask user to found which equation is the factorization form of the polynomial equation.
        E.g., -x²+5x-4 => -(x-1)(x-4)
        :param shuffle_the_equation: if we want to make this problem easier, we just have to turn off this arg
        :return: Dictionary with the classic keys
        """
        sentences = ['Quelle est la forme factorisée du polynôme {l}{equation}=y{l}.',
                     'Donner sous forme de produit {l}f(x)={equation}{l}.']
        factored_equation = '{a}(x{x1})(x{x2})'
        a = generate_number_without_value((-2, 2))
        #  easy root of polynomial equation
        x1 = generate_number_without_value((-1, 2))
        x2 = generate_number_without_value((-10, 10), forbidden_value=[i for i in range(-2, 3)])

        b = -(x1 + x2) * a
        c = x1 * x2 * a

        equation = self.format_equation(a, b, c, shuffle_the_equation=shuffle_the_equation)
        a_format = self.format_equation(a, 0)[:-1]
        x1_format, x2_format = shuffle_a_list([self.format_value(-x1), self.format_value(-x2)])

        answer = factored_equation.format(a=a_format, x1=x1_format, x2=x2_format)

        values = [answer]
        #  Create fake values
        a_format = self.format_equation(a * choice([1, -1]), 0)[:-1]
        fake_x1, fake_x2 = shuffle_a_list([x1, b // (a * x1)])
        x1_format, x2_format = shuffle_a_list([self.format_value(fake_x1), self.format_value(fake_x2)])
        values.append(factored_equation.format(a=a_format, x1=x1_format, x2=x2_format))

        a_format = self.format_equation(a * choice([1, -1]), 0)[:-1]
        fake_x1, fake_x2 = shuffle_a_list([x1, x2])
        x1_format, x2_format = self.format_value(-fake_x1), self.format_value(fake_x2)
        values.append(factored_equation.format(a=a_format, x1=x1_format, x2=x2_format))

        a_format = self.format_equation(a, 0)[:-1]
        fake_x1, fake_x2 = shuffle_a_list([x1, b // (a * x1)])
        x1_format, x2_format = self.format_value(-fake_x1), self.format_value(fake_x2)
        values.append(factored_equation.format(a=a_format, x1=x1_format, x2=x2_format))

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(equation=equation, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_calculate_discriminant(self, shuffle_the_equation: bool = True, a_interval: tuple = (-4, 4),
                                 b_interval: tuple = (-6, 6), c_interval: tuple = (-4, 4)) -> dict:
        """
        Generates a question asking to calculate the discriminant of a quadratic equation.
        E.g., -x² + 5x - 4 => Δ = 5² - 4×(-1)×(-4) = 9

        :param shuffle_the_equation: If enabled, the equation may be rearranged to increase difficulty.
        :param a_interval: Range of possible values for coefficient a, excluding 0.
        :param b_interval: Range of possible values for coefficient b.
        :param c_interval: Range of possible values for coefficient c.
        :return: A dictionary containing:
            - 'question': The formatted question statement.
            - 'index_answer': The index of the correct answer in the list of choices.
            - 'suggested_answer': A list of possible answers, formatted in LaTeX if enabled.
        """
        sentences = ['Combien vaut le discriminant de {l}{equation}{l}',
                     'Calcule {l}{delta}{l} dans l\'équation {l}{equation}{l}',
                     'Le {l}{delta}{l} est égal à combien dans l\'equation {l}{equation}{l}']

        a = generate_number_without_value(a_interval, forbidden_value=0)
        b = generate_number_without_value(b_interval)
        c = generate_number_without_value(c_interval)
        #  To review this because I'm not sure at all ...
        equation = self.format_equation(a, b, c, shuffle_the_equation=shuffle_the_equation)

        possible_interval = (-4 * max(max(a, c) * max(a, c), min(a, c) * min(a, c)),
                             max(abs(min(b_interval)), abs(max(b_interval))) ** 2 + 4 * max(a_interval) * max(c_interval)
                             )
        answer = b**2 - 4 * a * c
        values = [answer]
        if answer != a**2 - 4 * b * c:
            values.append(a**2 - 4 * b * c)
        for _ in range(4 - len(values)):
            values.append(generate_number_without_value(possible_interval, forbidden_value=values))

        return {'question': choice(sentences).format(equation=equation, l="$" if self.latex else "",
                                                     delta=Latex.delta if self.latex else "delta"),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_calcul_product(self, multiplication_tables_interval: tuple = (6, 12),
                         odds_for_11: Optional[float] = 1 / 6) -> dict:
        """
        generates a question about multiplication tables, and offers several answers.
        I try to make the other answers consistent.
        :return: dictionary with the classic keys
        """
        assert odds_for_11 is None or 0 < odds_for_11 < 1
        sentences = ['Quel est le produit de {l}{n1}{l} par {l}{n2}{l} ?',
                     'Combien font {l}{n1}{times}{n2}{l} ?',
                     '{l}{n1}{times}{n2}=?{l}']
        table = range(min(multiplication_tables_interval), max(multiplication_tables_interval))
        #  There is a technique to calculate the 11 multiplication tables
        if 11 in table and odds_for_11 is not None:
            weights = []
            for i in table:
                weights.append(odds_for_11 if i == 11 else (1 - odds_for_11) / len(table))
        else:
            weights = [i / len(table) for i in table]

        n1 = choices(table, weights=weights)[0]
        if n1 == 11:
            #  that why numbers are older if it's the 11 multiplication tables
            n2 = randint(12, 99)
        else:
            n2 = choice(table)

        answer = n1 * n2

        values = [answer]
        count = ['', '', '']
        for _ in count:
            if n1 == 11:
                fake_n1 = n1
                fake_n2 = generate_number_without_value((12, 99), forbidden_value=n2)
            else:
                fake_n1 = generate_number_without_value(multiplication_tables_interval, forbidden_value=n1)
                fake_n2 = generate_number_without_value(multiplication_tables_interval)
            #  It's a bit slapped together, but it's just to say that we don't want the same value twice.
            if fake_n1 * fake_n2 in values:
                count.append('')
            else:
                values.append(fake_n1 * fake_n2)

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(n1=n1, n2=n2, l="$" if self.latex else "",
                                                     times=Latex.times if self.latex else "x"),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }


class Arithmetic(QuestionsMCQ):
    def __init__(self, latex: bool = False):
        super().__init__(self)
        self.latex = latex

    @staticmethod
    def all_prime_number_of_an_interval(interval: tuple = (5, 50)) -> list[int]:
        """
        return all prime numbers in the interval
        """
        #  Check if the interval arg is just a tuple (or list) of two elements, sorted.
        assert interval == (min(interval), max(interval))

        #  Algorithm that we saw in math last year8
        def is_prime(n: int) -> bool:
            """
            say if the number is a prime number or not
            """
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

        # All prime numbers in the interval
        prime_numbers = [num for num in range(min(interval), max(interval) + 1) if is_prime(num)]

        return prime_numbers

    def q_perfect_square(self, interval: tuple = (25, 196)) -> dict:
        """
        ask if a number is a perfect square or not, the answer is True or False.
        """
        sentences = ['Le nombre {l}{number_generated}{l} est-il un carré parfait ?',
                     '{l}{number_generated}{l} est-il le carré d\'un nombre entier ?',
                     'Peut-on écrire {l}{number_generated}{l} comme {l}k{sqrt}{l} avec {l}k {definition_domain}{l} ?']
        #  list of the perfect square in the interval
        perfect_square = [number ** 2 for number in range(floor(min(interval) ** 0.5), ceil(max(interval) ** 0.5) + 1)]
        #  I always shuffle but actually it is not necessary
        values = [True, False]
        #  This line decides if the answer is True or False
        is_perfect_square = choice(values)

        if is_perfect_square:
            #  If the answer is a perfect square, we chose one from the perfect square list
            number_generated = choice(perfect_square)
        else:
            #  else we chose a number in this interval that is not a perfect square
            number_generated = generate_number_without_value(interval, forbidden_value=perfect_square)

        return {'question': choice(sentences).format(number_generated=number_generated, l="$" if self.latex else "",
                                                     sqrt='^2' if self.latex else "²",
                                                     definition_domain=f"{Latex.in_set} {Latex.Z}" if self.latex
                                                     else "un entier"),
                'suggested_answer': values,
                'index_answer': values.index(is_perfect_square)}

    def q_prime_number(self, interval: tuple = (10, 40)) -> dict:
        """
        ask if a number is a prime number or not.
        """
        sentences = ['{l}{number_generated}{l} est-il divisible uniquement par {l}1{l} et lui-même ?',
                     'Peut-on dire que {l}{number_generated}{l} est un nombre premier ?',
                     'Est-ce que {l}{number_generated}{l} est considéré comme un nombre premier ?']

        prime_number = self.all_prime_number_of_an_interval(interval)
        values = [True, False]
        is_prime = choice(values)
        if is_prime:
            number_generated = choice(prime_number)
        else:
            number_generated = generate_number_without_value(interval, forbidden_value=prime_number)
            #  We don't want a pair number because this is too easy to see it's not a prime number
            while number_generated % 2 == 0 and number_generated != 2:
                number_generated = generate_number_without_value(interval, forbidden_value=prime_number)

        return {'question': choice(sentences).format(number_generated=number_generated, l="$" if self.latex else ""),
                'suggested_answer': values,
                'index_answer': values.index(is_prime)}

    def q_greatest_lower_common_divisor_multiple(self, interval: tuple = (20, 40),
                                                 solution_interval: tuple = (2, 6)) -> dict:
        """
        ask the greatest common divisor or the lower common multiple of two numbers and suggest several solutions.
        :param interval: interval of the two numbers
        :param solution_interval: to generate "friendly" numbers, I generate number which
        has a common number into this interval
        """
        #  Check if the interval is a tuple of two numbers, sorted.
        assert interval == (min(interval), max(interval))
        sentences = ['Trouve le {gcd_or_lcm} entre {l}{n1}{l} et {l}{n2}{l}.',
                     'Calcule le {gcd_or_lcm} des nombres {l}{n1}{l} et {l}{n2}{l}.',
                     'Quel est le {gcd_or_lcm} de {l}{n1}{l} et {l}{n2}{l} ?']
        gcd_or_lcm = choice([[choice(['plus grand diviseur commmun', 'PGCD']), gcd],
                             [choice(['plus petit mutliple commmun', 'PPCM']), lcm]])
        k = generate_number_without_value(solution_interval)  # can't take 0, you will see why

        n1 = randint(min(interval) // k, max(interval) // k)
        n2 = generate_number_without_value((min(interval) // k, max(interval) // k), forbidden_value=n1)

        answer = gcd_or_lcm[1](n1, n2)
        values = [answer]

        count = 0
        while len(values) < 4:
            count += 1
            #  Generate other values
            fake_n1 = randint(min(interval) // k, max(interval) // k)
            fake_n2 = generate_number_without_value((min(interval) // k, max(interval) // k), forbidden_value=fake_n1)
            fake_value = gcd_or_lcm[1](fake_n1, fake_n2)
            if fake_value not in values:
                values.append(fake_value)
            elif count > 10:
                values.append(generate_number_without_value((min(values), max(values) + 4), forbidden_value=values))

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(gcd_or_lcm=gcd_or_lcm[0], n1=n1, n2=n2,
                                                     l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_is_divisible_by_a_number(self, interval: tuple = (100, 10_000),
                                   divisors: tuple = (3, 5, 6, 7, 9, 10, 15)) -> dict:
        """
        ask if a number is divisible by another one, using the divisible rules with specific numbers.
        The rule for the number 7 is not famous, but I know the trick :
        take a number
        546 => 6*2= 12  multiply by 2 the last digit.
            => 54 - 12 = 42  remove the result to the rest of the number
        7 can divide 42 so 7 can also divide 546.
        Another exemple:
        6793 => 3*2 = 6
             => 679 - 6 = 673
             673 => 3*2 = 6
                 => 67 - 6 = 61
        61 is not a multiple of 7, so 6793 too.

        :param interval: interval of the numbers generated.
        :param divisors: the numbers for which we can ask if a number is divisible by that one
        :return:
        """
        sentences = ['Le nombre {l}{k}{l} divise-t-il {l}{final_number}{l} ?',
                     '{l}{k}{l} peut-il diviser {l}{final_number}{l} sans laisser de reste ?',
                     '{l}{final_number}{l} est-il divisible par {l}{k}{l} ?']

        values = [True, False]
        is_divisible = choice(values)

        k = choice(divisors)
        if is_divisible:
            #  divide the interval by k, then multiply by k to be sure to have a multiple of k
            final_number = k * randint(min(interval) // k, max(interval) // k)
        else:
            final_number = randint(min(interval), max(interval))
            #  We search for a number that k cannot divide
            while final_number % k == 0:
                final_number = randint(min(interval), max(interval))

        return {'question': choice(sentences).format(final_number=final_number, k=k, l="$" if self.latex else ""),
                'suggested_answer': values,
                'index_answer': values.index(is_divisible)}

    def q_convert_bin_to_dec(self, interval: tuple = (5, 32)) -> dict:
        """
        Ask to convert a binary number to a decimal number
        :param interval: the interval of the values that can be asked
        :return:
        """
        sentences = ["Transforme le nombre {l}{number}{base}{l}{base_text} en nombre décimal.",
                     "Exprime {l}{number}{base}{l}{base_text} en base {l}10{l}.",
                     "Convertis {l}{number}{l} du binaire vers le décimal."]
        value = randint(*interval)
        
        values = [value]
        for _ in range(4 - len(values)):
            values.append(generate_number_without_value(interval, forbidden_value=values))
        answer = str(bin(value))[2:]

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(number=answer, l="$" if self.latex else "",
                                                     base="_2" if self.latex else "",
                                                     base_text="" if self.latex else " binaire"),
                'index_answer': values.index(value),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]}


class Geometry(QuestionsMCQ):

    def __init__(self, latex: bool = False):
        super().__init__(self)
        self.latex = latex
        self.prefix = {
                'shapes': {
                    'pent': 5,
                    'hex': 6,
                    'oct': 8,
                    'dec': 10,
                },
                'units': ["kilo", "hecto", "deca", "", "deci", "centi", "milli"]}
        self.degree = f"{Latex.degree}" if latex else "°"
        self.geometric_shapes_with_their_angles = {
            'triangle': (f'180{self.degree}', convert_degree_into_radian(f'180{self.degree}', latex=latex)),
            'carré': (f'360{self.degree}', convert_degree_into_radian(f'360{self.degree}', latex=latex)),
            'pentagone': (f'540{self.degree}', convert_degree_into_radian(f'540{self.degree}', latex=latex))
        }

    @staticmethod
    def pythagorean_triplet(interval: tuple = (1, 13)) -> list:
        """
        return all the pythagorean triplet in the range "interval".
        all values in the tuples are under the maximum of the interval.
        :param interval:
        :return: list of tuple of three items
        """
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
                    if is_new_triplet:  # append only if there isn't already this tuple
                        result.append((i, j, int((i ** 2 + j ** 2) ** 0.5)))
        return result

    @staticmethod
    def format_number(number: Union[int, float]) -> str:
        """
        Formats a number to remove unnecessary decimals or converts scientific notation to standard form.

        :param number: The number to format.
        :return: A string representing the formatted number.
        """
        if "e" in str(number):  # Handle scientific notation
            return "{:.10f}".format(number).rstrip("0").rstrip(".")
        elif isinstance(number, float):
            # Remove .0 for whole numbers
            if number.is_integer():
                return str(int(number))
            # Use a fixed number of decimal places, avoiding artifacts
            return "{:.10g}".format(number).rstrip("0").rstrip(".")

        return str(number)

    def convert_value_unit(self, source_value: Union[int, float], source_prefix: str, target_prefix: str) -> float:
        """
        Convert a value from one unit prefix to another.

        :param source_value: The numerical value to convert.
        :param source_prefix: The prefix of the source unit (e.g., 'milli', 'kilo').
        :param target_prefix: The prefix of the target unit (e.g., '', 'mega').
        :return: The converted value.
        """
        assert source_prefix in self.prefix['units'] and target_prefix in self.prefix['units']
        delta = self.prefix['units'].index(target_prefix) - self.prefix['units'].index(source_prefix)
        return source_value * 10 ** delta

    def q_how_many_side(self) -> dict:
        sentences = ['Combien de côté un {l}{polygone_prefix}agone{l} possède t\'il ?',
                     'Un {l}{polygone_prefix}agone{l}, c\'est un polygone à combien de coté ?',
                     'Quel est le nombre de coté d\'un {l}{polygone_prefix}agone{l} ?']

        prefix = choice(list(self.prefix['shapes']))
        answer = self.prefix['shapes'][prefix]
        values = [answer]

        min_value = min(list(self.prefix['shapes'].values()))
        max_value = max(list(self.prefix['shapes'].values()))
        for _ in range(3):
            values.append(generate_number_without_value((min_value, max_value), forbidden_value=values))

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(polygone_prefix=prefix, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]}

    def q_angles_sum(self) -> dict:
        """
         Creates a multiple-choice question about the sum of angles of a geometric shape.
        """
        sentences = ['Quelle est la sommes des angles d\'un {l}{shape}{l}',
                     'Quel est le résultat de l’addition des angles d’un {l}{shape}{l} ?',
                     'Que vaut la somme des angles d’un {l}{shape}{l} ?']
        shape_chosen = choice(list(self.geometric_shapes_with_their_angles))
        answer = choice(self.geometric_shapes_with_their_angles[shape_chosen])

        values = [answer]

        #  Generate fake values
        while len(values) < 4:
            fake_shape = choice(list(self.geometric_shapes_with_their_angles))
            if fake_shape == shape_chosen:
                continue
            fake_value = choice(list(self.geometric_shapes_with_their_angles[fake_shape]))
            if fake_value in values:
                continue
            values.append(fake_value)

        values = shuffle_a_list(values)

        return {'question': choice(sentences).format(shape=shape_chosen, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]
                }

    def q_triangle_nature(self, interval: tuple = (3, 10), shuffle_answers: bool = True) -> dict:
        """
        Generates a multiple-choice question to determine the type of triangle based on its sides.

        :param interval: A tuple specifying the range of possible side lengths (default is (3, 10)).
        :param shuffle_answers: If True, shuffle the order of the suggested answers (default is True).
        """
        assert interval == (min(interval), max(interval))
        sentences = ['Détermine la nature du triangle aux côtés {l}{a}{l}, {l}{b}{l}, et {l}{c}{l}.',
                     'À quelle catégorie appartient le triangle avec des côtés de {l}{a}{l}, {l}{b}{l} et {l}{c}{l} ?',
                     'Identifie la nature du triangle ayant pour côtés {l}{a}{l}, {l}{b}{l}, et {l}{c}{l}.']
        values = ['rectangle', 'isocèle', 'équilatéral', 'quelconque']
        if shuffle_answers:
            values = shuffle_a_list(values)
        answer = choice(values)

        if answer == 'rectangle':
            side = list(choice(self.pythagorean_triplet(interval)))
        else:
            side: list = [randint(*interval)]
            if answer == 'équilatéral':
                side *= 3
            else:
                side.append(generate_number_without_value(interval, forbidden_value=side))
                if answer == 'isocèle':
                    side.append(choice(side))
                else:
                    new_side = generate_number_without_value(interval, forbidden_value=side)
                    side.append(new_side)
                    side.sort()
                    while side[0] ** 2 + side[1] ** 2 == side[2] ** 2:
                        side.remove(new_side)

                        new_side = generate_number_without_value(interval, forbidden_value=side)
                        side.append(new_side)
                        side = side.sort()

        a, b, c = shuffle_a_list(side)

        return {'question': choice(sentences).format(a=a, b=b, c=c, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]}

    def q_convert_unit(self) -> dict:
        """
        generates a question for converting a value between units with proper formatting.
        """
        unit_range = (0, len(self.prefix['units']) - 1)
        sentences = ['Convertis {l}{source_value}{l} {l}{source_unit}{l} en {l}{target_unit}{l}.',
                     '{l}{source_value}{l} {l}{source_unit}{l} font combien de {l}{target_unit}{l} ?',
                     'Transforme {l}{source_value}{l} {l}{source_unit}{l} en {l}{target_unit}{l}.']
        unit = choice(['grammes', 'litres', 'mètres'])

        source_value = round(random() * 10, 1)
        #  first, we manipulate index, because this is the easier way to generate random prefix
        source_unit_index = randint(*unit_range)
        answer_index = generate_number_without_value(unit_range, forbidden_value=source_unit_index)
        unit_index_of_fake_value = []

        for _ in range(3):
            #  Generate 3 others different values
            unit_index_of_fake_value.append(
                generate_number_without_value(
                    unit_range,
                    forbidden_value=[source_unit_index, answer_index, *unit_index_of_fake_value])
            )

        #  we've got all prefix indexes to generate new values, so now we transform index into values with their units.
        source_prefix = self.prefix['units'][source_unit_index]
        answer_prefix = self.prefix['units'][answer_index]
        latex = '$' if self.latex else ''

        answer = (f"{latex}{self.format_number(self.convert_value_unit(source_value, source_prefix, answer_prefix))}{latex}"
                  + f" {latex}{answer_prefix}{unit}{latex}")
        values = [answer]
        for fake_value_index in unit_index_of_fake_value:
            fake_target_prefix = self.prefix['units'][fake_value_index]
            fake_value = self.convert_value_unit(source_value, source_prefix, fake_target_prefix)
            latex = '$' if self.latex else ''
            fake_value = f"{latex}{self.format_number(fake_value)}{latex}" + f" {latex}{answer_prefix}{unit}{latex}"
            values.append(fake_value)

        values = shuffle_a_list(values)
        source_unit = source_prefix + unit
        target_unit = answer_prefix + unit
        return {'question': choice(sentences).format(source_value=source_value, source_unit=source_unit,
                                                     target_unit=target_unit, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': values}


class Trigonometry(QuestionsMCQ):
    def __init__(self, latex: bool = False):
        super().__init__(self)
        self.latex = latex
        self.values_into_str = {0: "0",
                       0.5: f"{Latex.frac.format(a=1, b=2)}" if self.latex else "1/2",
                       0.707: f"{Latex.frac.format(a=Latex.sqrt.format(n=2), b=2)}" if self.latex else f'{sqrt.format(number=2)}/2',
                       0.866: f"{Latex.frac.format(a=Latex.sqrt.format(n=3), b=2)}" if self.latex else f'{sqrt.format(number=3)}/2',
                       1: '1'}
        self.relation = {
            'cosinus': 'adjacent/hypothénuse',
            'sinus': 'opposé/hypothénuse',
            'tangente': 'opposé/adjacent'
        }

        #  "base" angle that we are supposed to know and from which, we can find all the others
        self.degree = f"{Latex.degree}" if latex else "°"
        self.angles_base = [f'0{self.degree}', f'30{self.degree}', f'45{self.degree}', f'60{self.degree}']
        self.angles = self.get_extended_angles(start=-4, stop=4)


    def get_extended_angles(self, *, start: int = -2, stop: int = 2) -> list[str]:
        """
        Generate a list of extended angles by adding multiples of 90° to base angles.
        Angles by default are only the base angles, this function extended it
        :param start: Starting multiplier for 90° (inclusive).
        :param stop: Ending multiplier for 90° (exclusive).
        :return: A list of angles as strings, angles in degrees
        """
        new_angles = []
        for i in range(start, stop):
            for value in self.angles_base:
                new_angle: str = self.add_angles(value, 90 * i)
                new_angles.append(new_angle)

        new_angles.append(f'{90 * stop}{self.degree}')
        return new_angles

    def add_angles(self, angle_degree: str, delta_in_degree: int):
        value = int(angle_degree[:-len(self.degree)])
        value += delta_in_degree
        value = str(value) + self.degree
        return value

    def q_trigo_formula(self):
        sentences = [
            'Dans un triangle rectangle, {determinant} {l}{trigo_function}{l} est-il le rapport entre l\'{l}{side1}{l} et l\'{l}{side2}{l} ?',
            '{determinant} {l}{trigo_function}{l} d\'un angle est-il égal au rappport {l}{frac}{l} ?'
        ]
        trigo_function = choice(list(self.relation))
        values = [True, False]
        result = choice(values)
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
                                            l="$" if self.latex else "", frac=Latex.frac.format(a=side1, b=side2) if self.latex else f"{side1}/{side2}",
                                            side1=side1, side2=side2),
                'index_answer': values.index(result),
                'suggested_answer': values}

    def q_found_value(self) -> dict:
        """
        Generates a question about the value of a trigonometric function for a given angle.
        """
        sentences = ['Quelle est la valeur de {l}{trigo_function}({value}){l} ?',
                     'Quelle valeur doit-on attribuer à {l}{trigo_function}({value}){l} ?',
                     'Quel est le résultat de {l}{trigo_function}({value}){l} dans l’unité cercle ?']
        # Select a trigonometric function and its string representation
        trigo_function = choice([(cos, Latex.cos if self.latex else 'cos'), (sin, Latex.sin if self.latex else 'sin')])
        value = choice(self.angles)
        answer = round(trigo_function[0](radians(int(value[:-len(self.degree)]))), 3)
        if answer < 0:
            answer = "-" + self.values_into_str[abs(answer)]
        else:
            answer = self.values_into_str[answer]
        #  can ask in radian
        if choice([True, False]):
            value = convert_degree_into_radian(value, latex=self.latex)

        values = [answer]
        while len(values) < 4:
            fake_value = choice(self.angles)
            fake_value = round(trigo_function[0](radians(int(fake_value[:-len(self.degree)]))), 3)
            if fake_value < 0:
                fake_value = "-" + self.values_into_str[abs(fake_value)]
            else:
                fake_value = self.values_into_str[fake_value]
            if fake_value in values:  # Avoid duplicates
                continue
            values.append(fake_value)

        return {'question': choice(sentences).format(trigo_function=trigo_function[1], value=value, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]}

    def q_is_the_same_value(self) -> dict:
        """
            Generates a question about whether two angles are equivalent on the unit circle.
        """
        sentences = ['{l}{angle1}{l} est-il confondu avec {l}{angle2}{l} dans le cerle trigonométrique ?',
                     '{l}{angle1}{l} et {l}{angle2}{l} ont-ils la même position sur le cercle trigo ?',
                     'Peut-on superposer {l}{angle1}{l} et {l}{angle2}{l} dans le cercle trigo d\'unité 1 ?']
        angle1 = choice(self.angles)
        values = [True, False]
        answer = choice(values)
        k = randint(-1, 1)
        while k == 0:
            k = randint(-1, 1)
        if answer:
            angle2 = self.add_angles(angle1, 360 * k)
        else:
            while True:
                angle2 = choice(self.angles)
                if angle1 != angle2:
                    break
        angles = [angle1, angle2]
        shuffle(angles)
        angle1, angle2 = angles
        if choice([True, False]):
            angle1 = convert_degree_into_radian(angle1, latex=self.latex)

        if choice([True, False]):
            angle2 = convert_degree_into_radian(angle2, latex=self.latex)

        sentence = choice(sentences)
        return {'question': sentence.format(angle1=angle1, angle2=angle2, l="$" if self.latex else ""),
                'index_answer': values.index(answer),
                'suggested_answer': values}

    def q_convert_value_into_degree_or_radian(self, **kwargs):
        """
        Generates a question about converting a value between degrees and radians.

        Process:
        - Generate 4 pairs of equivalent values (in degrees and radians).
        - Randomly choose whether to present the value in degrees or radians.
        - Randomly determine the correct answer from the pairs.
        - Convert the remaining values into the appropriate unit (degrees or radians).

        """
        sentences = ['{l}{value}{l} correspond à quelle valeur en {l}{unit_target}{l} ?',
                     'Combien de {l}{unit_target}{l} représente {l}{value}{l} ?',
                     '{l}{value}{l} donne combien en {l}{unit_target}{l} ?',
                     'Quelle est l’équivalence exacte en {l}{unit_target}{l} de {l}{value}{l} ?']

        couple_values = []
        while len(couple_values) < 4:
            new_value = choice(self.get_extended_angles())
            new_value = (new_value, convert_degree_into_radian(new_value, latex=self.latex))
            if new_value not in couple_values:
                couple_values.append(new_value)
        degree_or_radian = randint(0, 1)  # Chose if radian or degree
        #  Chose an answer (currently, this is a couple of values)
        couple_values = shuffle_a_list(couple_values)
        answer = choice(couple_values)
        #  Get the index of the good answer
        answer_index = -1
        for i, item in enumerate(couple_values):
            if item == answer:
                answer_index = i
                break

        answer = answer[degree_or_radian]
        values = []
        for couple_value in couple_values:
            values.append(couple_value[1 - degree_or_radian])

        unit_target = ('degrés', 'radians')[1 - degree_or_radian]

        return {'question': choice(sentences).format(value=answer, unit_target=unit_target, l="$" if self.latex else ""),
                'index_answer': answer_index,
                'suggested_answer': [convert_value_to_latex(value) if self.latex else value for value in values]}


def generate_mcq_question(subjects: Union[list[str], str] = '*', *, latex: bool = False) -> dict:
    """
    This is the main function that will be called everytime.

    Take randomly a question in the subject that is in the parameters.
    In fact, this function doesn't do complicated things; it's just a link
    with the other functions in each math discipline.

    :param subjects: Trigonometry, Arithmetic, Geometry, Algebra or all of these ("*")
    :rtype subjects: list of str or just a str ("*")
    :param latex: If the response is in the latex formula format
    :rtype latex: boolean value, if true, it returns a latex string value
    :return: The question in text, the suggestions answer, the index of the good answer and the subject that was chosen.
    """
    #  I link "manually" word with the function that generate question about the math discipline.
    all_subjects = {
        'Arithmetic': Arithmetic(latex=latex),
        'Trigonometry': Trigonometry(latex=latex),
        'Geometry': Geometry(latex=latex),
        'Algebra': Algebra(latex=latex)
    }
    subjects = [subject for subject in subjects if subject in all_subjects]
    if not subjects:
        subjects = list(all_subjects)
    k = [all_subjects[subject_name].get_number_of_questions() for subject_name in subjects]
    random_subject = choices(subjects, weights=k)[0]

    #  returns the dictionary with the following keys "question", "suggested_answer", "index_answer" and "subject"
    return all_subjects[random_subject].generate()


def calculate_score(metaData: dict, *, a1: int = 2, a2: int = 100):
    """Calculate the score based on the provided metaData."""
    assert metaData.get('answers') is not None
    score = 0
    for answer in metaData["answers"].values():
        score += int(answer["correct_answer"]) * (1 / log10(answer['timeTaken'] + a1)) * a2
    return round(score, 2)


def run(number_of_questions: Optional[int] = None, subjects: Union[list[str], str] = '*'):
    marge = 3 * " "
    score = 0
    letters = 'ABCD'
    input('Bienvenue! appuyez sur entrer pour commencer le quiz !')
    if not number_of_questions:
        number_of_questions = input('Combien de questions voulez-vous ? : ')
        while not number_of_questions.isdigit():
            print('Je n\'ai pas compris.')
            number_of_questions = input('Combien de questions voulez-vous ? : ')
        number_of_questions = int(number_of_questions)

    for _ in range(number_of_questions):
        #  Here we can choose the discipline we want to train
        question_data = generate_mcq_question(subjects=subjects)
        print("".ljust(len(question_data['question']), "─"))
        #  Draw the question
        print(f"({question_data['subject']}) - " + question_data['question'])
        #  Draw the suggestions
        for i, suggested_answer in enumerate(question_data['suggested_answer']):
            print(marge + f'{letters[i]}. {suggested_answer}')

        user_response = input(marge + 'Votre réponse : ').upper().strip()
        try:
            user_response_index = letters.index(user_response)
        except ValueError:
            user_response_index = -1
        if user_response_index == question_data['index_answer']:
            #  Draw anything because it's correct.
            score += 1
        else:
            print(f"Et non, la réponse était la lettre {letters[question_data['index_answer']]}.  "
                  f"{question_data['suggested_answer'][question_data['index_answer']]}...")
    print(f'Votre score est de {score} bonne réponse, soit {int(score / number_of_questions * 100)}% de réussite')


def simple_test():
    stats = {}
    for _ in tqdm(range(15_000)):
        data = generate_mcq_question("*", latex=True)
        #  print(data)
        for important_key in ["question", "suggested_answer", "index_answer"]:
            if important_key not in data.keys():
                raise ValueError(f"The '{important_key}' key is missing in the {data['question_name']} function.")

    #  print('Everything is correct.')


if __name__ == '__main__':
    simple_test()
