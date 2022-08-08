from random import randint

class BoardException(Exception):                         #классы исключений
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Dot:                                              #класс задания точек
    def __init__(self, x, y):                           #создание класса точка с двумя параметрами - х и у в конструкторе класса
        self.x = x                                      #благодаря магическому методу __init__(инициализация)
        self.y = y

    def __eq__(self, other):                            #метод сравнения объектов друг с другом
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"               #метод наглядного представления точек


class Ship:                                        #класс по заданию кораблей
    def __init__(self, bow, l, o):                 # o - параметр задает ориентацию корабля
        self.bow = bow                             # (0 - вертикальная, 1 - горизонтальная)
        self.l = l                                 # bow - координата носа корабля
        self.o = o                                 # l - длина корабля
        self.lives = l

    @property
    def dots(self):                                #заполнение корабля точками в зависимости от
        ship_dots = []                             #параметров bow, l, o.
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:                                              #класс вызова доски
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0                                   #count - количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)] #field - атрибут содержащий сетку состояний

        self.busy = []                                   #busy - атрибут отвечающий за занятость клетки(корабль/выстрел)
        self.ships = []                                  #ships - список кораблей доски



    def __str__(self):                                           #в данном методе записываем всю нашу доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:                                             #параметр, который показывает нужно ли скрывать корабли на доске
            res = res.replace("■", "O")
        return res

    def out(self, d):                                            #метод определяет находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [                                                 #список near содержит все сдвиги точек
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:                                    #проходим все точки соседствующие с кораблем
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):                                  #метод для размещения корабля

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):                                       #метод выстрела
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []
    def defeat(self):
        return self.count == len(self.ships)



class Player:                                               #класс игрока
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):                                         #класс компьютера/второго игрока
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):                                       #класс ввода данных пользователем
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:                                            #класс игры: создаем доску, расставляем корабли в случайном порядке
    def __init__(self, size=6):                        
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                     board.add_ship(ship)
                     break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой !   ")
        print("-------------------")
        print(" Ввод осуществляется покоординатно в виде: x y  через пробел")
        print(" в начале вводим 'x' - номер строки  ")
        print(" затем вводим 'y' - номер столбца ")
        print()
        print("Желаю победы!")

    def loop(self):
        num = 0
        while True:
            print("*" * 27)
            print("Ваша доска:")
            print(self.us.board)
            print("*" * 27)
            print("Доска соперника:")
            print(self.ai.board)
            if num % 2 == 0:
                print("*" * 27)
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("*" * 27)
                print("Теперь ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("Вы победили соперника!")
                break

            if self.us.board.defeat():
                print("-" * 20)
                print("Соперник выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
