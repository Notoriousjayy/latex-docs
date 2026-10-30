"""ASCII expression lexer; original learning implementation, not a general compiler."""
from dataclasses import dataclass

MAX_SOURCE = 65536
MAX_INTEGER_DIGITS = 18

class LexError(ValueError):
    def __init__(self, message: str, position: int):
        super().__init__(f"{message} at offset {position}")
        self.position = position

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int

def tokenize(text: str) -> list[Token]:
    if len(text) > MAX_SOURCE:
        raise LexError('source too large', MAX_SOURCE)
    result: list[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in ' \t\n\r':
            i += 1
            continue
        if '0' <= ch <= '9':
            start = i
            while i < len(text) and '0' <= text[i] <= '9':
                i += 1
            if i-start > MAX_INTEGER_DIGITS:
                raise LexError('integer literal too long', start)
            result.append(Token('INT',text[start:i],start,i))
        elif ch in '+-*()/':
            result.append(Token(ch,ch,i,i+1))
            i+=1
        else:
            raise LexError('invalid ASCII expression character',i)
    result.append(Token('EOF','',len(text),len(text)))
    return result
