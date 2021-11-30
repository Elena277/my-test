from random import randint
from time import sleep


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете за пределы доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, dir):
        self.bow = bow
        self.length = length
        self.dir = dir
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.dir == 0:
                cur_x += i
            elif self.dir == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["o"]*size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = "   | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.field):
            res += f"\n{i+1}  | " + " | ".join(row) + " | "

        if self.hid:
            res = res.replace("■", "o")
        return res

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shoot(d):
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


class Player:
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


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"\nХод компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coord = input("Ваш ход: ").split()

            if len(coord) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = coord

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempt = 0

        for length in lens:
            while True:
                attempt += 1
                if attempt > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("---------------------------")
        print("       Приветствуем вас     ")
        print("           в игре          ")
        print("          МОРСКОЙ БОЙ      ")
        print("---------------------------")
        print("      формат ввода: x y    ")
        print("       x - номер строки    ")
        print("       y - номер столбца   ")

    def loop(self):
        num_chod = 0
        while True:
            print("-" * 28)
            print("Ваша доска:")
            print(self.us.board)
            print("-" * 28)
            print("-" * 28)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 28)
            if num_chod % 2 == 0:
                print("Вы ходите!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                for s in "...":
                    print(s, end=" ")
                    sleep(0.5)
                repeat = self.ai.move()
            if repeat:
                num_chod -= 1

            if self.ai.board.count == 7:
                print("-" * 28)
                print("Вы выиграли!\nДоска компьютера:")
                print(self.ai.board)
                break

            if self.us.board.count == 7:
                print("-" * 28)
                print("Компьютер выиграл!\nВаша доска:")
                print(self.us.board)
                break
            num_chod += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
