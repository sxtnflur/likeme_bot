import enum


class MainAspectRation(enum.StrEnum):
    square = enum.auto()
    high_2 = enum.auto()
    wide_1 = enum.auto()

    @classmethod
    def default(cls):
        return cls.wide_1

    def next(self):
        members = list(self.__class__)
        index = members.index(self) + 1
        if index >= len(members):
            return members[0]  # Возвращаем первое значение
        return members[index]

    def get_aspects(self) -> tuple[int, int]:
        data = {
            self.square: (1, 1),
            self.high_2: (3, 4),
            self.wide_1: (4, 3)
        }
        return data.get(self)

    def get_wh(self) -> tuple[int, int]:
        data = {
            self.square: (1080, 1080),
            self.high_2: (810, 1080),
            self.wide_1: (1440, 1080)
        }
        return data.get(self)


class AspectRatio(enum.StrEnum):
    square = enum.auto()

    high_1 = enum.auto()
    high_2 = enum.auto()
    high_3 = enum.auto()
    high_4 = enum.auto()

    wide_1 = enum.auto()
    wide_2 = enum.auto()
    wide_3 = enum.auto()
    wide_4 = enum.auto()

    @staticmethod
    def base_values():
        return MainAspectRation

    def get_wh(self) -> tuple[int, int]:
        data = {
            self.square: (1080, 1080),      # Квадрат - популярный размер для соцсетей
            self.high_1: (720, 1080),       # Портрет - хорош для мобильных устройств
            self.high_2: (810, 1080),       # Вертикальный - оптимален для Instagram
            self.high_3: (864, 1080),       # Вертикальный - популярен в Facebook
            self.high_4: (608, 1080),       # Stories/Reels - полный вертикальный формат
            self.wide_1: (1440, 1080),      # Горизонтальный - классический формат
            self.wide_2: (1350, 1080),      # Горизонтальный - немного шире
            self.wide_3: (1920, 1080),      # Wide - Full HD стандарт
            self.wide_4: (2520, 1080)       # Ultra Wide - кинематографический формат
        }
        return data.get(self)

    def get_aspects(self) -> tuple[int, int]:
        data = {
            self.square: (1, 1),

            self.high_1: (2, 3),
            self.high_2: (3, 4),
            self.high_3: (4, 5),
            self.high_4: (9, 16),

            self.wide_1: (4, 3),
            self.wide_2: (5, 4),
            self.wide_3: (16, 9),
            self.wide_4: (21, 9)
        }
        return data.get(self)

    @classmethod
    def default(cls):
        return cls.wide_1

    def next(self):
        members = list(self.__class__)
        index = members.index(self) + 1
        if index >= len(members):
            return members[0]  # Возвращаем первое значение
        return members[index]