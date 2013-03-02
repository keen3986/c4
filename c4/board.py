from itertools import chain

import numpy as np

from c4.tables import rev_segments, all_segments


PLAYER1 = 1
PLAYER2 = 2
DRAW = 0
COMPUTE = -1


class WrongMoveError(Exception):
    pass


class Board(object):
    def __init__(self, pos=None, stm=PLAYER1, end=COMPUTE, cols=8, rows=7):
        if pos is None:
            pos = np.zeros((cols, rows), dtype=int)
        self._pos = pos
        self._stm = stm
        if end == COMPUTE:
            self._end = self._check_end(pos)
        else:
            self._end = end
        
    @property
    def end(self):
        return self._end

    @property
    def stm(self):
        return self._stm

    @classmethod
    def _check_end(cls, pos):
        for seg in cls.segments(pos):
            if (seg == PLAYER1).all():
                return PLAYER1
            elif (seg == PLAYER2).all():
                return PLAYER2

        if (pos == 0).any():
            return None
        else:
            return DRAW

    @classmethod
    def _check_end_around(cls, pos, r, c, side):
        for seg in cls.segments_around(pos, r, c):
            if (seg == side).all():
                return side

        if (pos == 0).any():
            return None
        else:
            return DRAW
        
    @classmethod
    def linear_segments(cls, line):
        for x in range(len(line) - 3):
            yield line[x:x+4]

    @classmethod
    def segments(cls, pos):
        if isinstance(pos, Board):
            for x in cls.segments(pos._pos):
                yield x
        else:
            pos = pos.flatten()
            for x in pos[all_segments]:
                yield x

    @classmethod
    def segments_around(cls, pos, r, c):
        if isinstance(pos, Board):
            for x in cls.segments_around(pos._pos, r, c):
                yield x
        else:
            idx = c * pos.shape[1] + r
            pos = pos.flatten()
            for seg in rev_segments[idx]:
                yield pos[seg]

    def __str__(self):
        disc = {
            0: ' ',
            1: 'X',
            2: 'O'
            }

        s = []
        for row in reversed(self._pos.transpose()):
            s.append(' | '.join(disc[x] for x in row))
        s.append(' | '.join('-'*8))
        s.append(' | '.join(map(str, range(1, 9))))
        s = ['| ' + x + ' |' for x in s]
        s = [i + ' ' + x for i, x in zip('ABCDEFG  ', s)]
        s = '\n'.join(s)

        if self._end is DRAW:
            s += '\n<<< Game over: draw' % [self._end]
        elif self._end is not None:
            s += '\n<<< Game over: %s win' % disc[self._end]
        else:
            s += '\n<<< Move to %s' % disc[self._stm]
        return s

    def move(self, m):
        if not (0 <= m < 8):
            raise ValueError(m)

        pos = self._pos.copy()

        r = pos[m].argmin()
        if pos[m][r] != 0:
            raise WrongMoveError('Full Column')
        pos[m][r] = self._stm
        end = self._check_end_around(pos, r, m, self._stm)
        stm = PLAYER1 if self._stm != PLAYER1 else PLAYER2
        return Board(pos, stm, end)

    def freerow(self, m):
        r = self._pos[m].argmin()
        if self._pos[m][r] != 0:
            return None
        return r

    def moves(self):
        return np.flatnonzero(self._pos[:, -1] == 0)

    def hashkey(self):
        """Generates an hashkey

        Returns a tuple (key, flip)
        flip is True if it returned the key of the symmetric Board.

        """
        k1 = 0
        k2 = 0

        for x in self._pos.flat:
            k1 *= 3
            k1 += int(x)
            assert k1 >= 0

        for x in self._pos[::-1].flat:
            k2 *= 3
            k2 += int(x)
            assert k2 >= 0

        if k2 < k1:
            return k2, True
        else:
            return k1, False
