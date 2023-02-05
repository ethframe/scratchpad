package expressions

import (
	"errors"
	"regexp"
)

type Node interface {
	isNode()
}

type node struct{}

func (node) isNode() {}

type Binary struct {
	node
	Op       string
	Lhs, Rhs Node
}

type Unary struct {
	node
	Op  string
	Arg Node
}

type Term struct {
	node
	Kind  string
	Value string
}

var tokens = regexp.MustCompile(`(?P<ident>[a-zA-Z_][a-zA-Z_0-9]*)|(?P<num>[0-9]+)|(?P<op>[+\-*/()!^])|[ \n\r\t]+`)
var eof = Token{Kind: "eof"}

type NudParser func(*Lexer) (Node, error)
type LedParser func(*Lexer, Node) (Node, error)

func prefix(op string, bp int) NudParser {
	return func(l *Lexer) (Node, error) {
		expr, err := parseExpr(l, bp)
		if err != nil {
			return nil, err
		}
		return &Unary{Op: op, Arg: expr}, nil
	}
}

func closedDrop(bp int, end string) NudParser {
	return func(l *Lexer) (Node, error) {
		expr, err := parseUntil(l, bp, Token{"op", end})
		if err != nil {
			return nil, err
		}
		l.Advance()
		return expr, nil
	}
}

func infix(op string, rbp int) LedParser {
	return func(l *Lexer, expr Node) (Node, error) {
		rhs, err := parseExpr(l, rbp)
		if err != nil {
			return nil, err
		}
		return &Binary{Op: op, Lhs: expr, Rhs: rhs}, nil
	}
}

func infixLeft(op string, bp int) LedParser {
	return infix(op, bp+1)
}

func infixRight(op string, bp int) LedParser {
	return infix(op, bp)
}

func postfix(lbp int, op string) LedParser {
	return func(l *Lexer, expr Node) (Node, error) {
		return &Unary{Op: op, Arg: expr}, nil
	}
}

var nud map[string]NudParser
var led map[string]LedParser
var lbp map[string]int

func init() {
	nud = map[string]NudParser{
		"+": prefix("pos", 5),
		"-": prefix("neg", 5),
		"(": closedDrop(0, ")"),
	}
	led = map[string]LedParser{
		"+": infixLeft("add", 0),
		"-": infixLeft("sub", 0),
		"*": infixLeft("mul", 2),
		"/": infixLeft("div", 2),
		"^": infixRight("pow", 4),
		"!": postfix(6, "fact"),
	}
	lbp = map[string]int{
		"+": 0, "-": 0,
		"*": 2, "/": 2,
		"^": 4,
		"!": 6,
	}
}

func parsePrim(lexer *Lexer, tok Token) (Node, error) {
	switch tok.Kind {
	case "ident", "num":
		lexer.Advance()
		return &Term{Kind: tok.Kind, Value: tok.Value}, nil
	}
	return nil, errors.New("Unexpected token")
}

func parseExpr(lexer *Lexer, bp int) (Node, error) {
	var expr Node
	var err error
	tok := lexer.Peek()
	if tok.Kind == "op" {
		if parseNud := nud[tok.Value]; parseNud != nil {
			lexer.Advance()
			expr, err = parseNud(lexer)
		} else {
			expr, err = parsePrim(lexer, tok)
		}
	} else {
		expr, err = parsePrim(lexer, tok)
	}
	if err != nil {
		return nil, err
	}
	tok = lexer.Peek()
	for tok.Kind == "op" {
		parseLed := led[tok.Value]
		if parseLed == nil || lbp[tok.Value] < bp {
			break
		}
		lexer.Advance()
		expr, err = parseLed(lexer, expr)
		if err != nil {
			return nil, err
		}
		tok = lexer.Peek()
	}
	return expr, nil
}

func Parse(src string) (Node, error) {
	lexer := NewLexer([]byte(src), tokens, eof)
	return parseUntil(lexer, 0, eof)
}

func parseUntil(lexer *Lexer, bp int, tok Token) (Node, error) {
	expr, err := parseExpr(lexer, bp)
	if err != nil {
		return nil, err
	}
	if lexer.Peek() != tok {
		return nil, errors.New("Unexpected token")
	}
	return expr, nil
}
