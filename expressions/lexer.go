package expressions

import "regexp"

type Token struct {
	Kind  string
	Value string
}

type Lexer struct {
	src   []byte
	re    *regexp.Regexp
	token Token
	eof   Token
}

func NewLexer(src []byte, re *regexp.Regexp, eof Token) *Lexer {
	l := &Lexer{src, re, eof, eof}
	l.advance()
	return l
}

func (l *Lexer) advance() bool {
	names := l.re.SubexpNames()[1:]
	for len(l.src) > 0 {
		sub := l.re.FindSubmatch(l.src)
		if len(sub) == 0 {
			return false
		}
		tl := len(sub[0])
		if tl == 0 {
			return false
		}
		l.src = l.src[tl:]
		for i, val := range sub[1:] {
			if val != nil {
				kind := names[i]
				if kind == "" {
					break
				}
				l.token.Kind = kind
				l.token.Value = string(val)
				return true
			}
		}
	}
	return false
}

func (l Lexer) Peek() Token {
	return l.token
}

func (l *Lexer) Advance() Token {
	if !l.advance() {
		l.token = l.eof
	}
	return l.token
}
