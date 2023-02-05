package expressions

import (
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

type NudParser func(*Lexer) Node
type LedParser func(*Lexer, Node) Node

func prefix(op string, bp int) NudParser {
	return func(l *Lexer) Node {
		return &Unary{Op: op, Arg: parseExpr(l, bp)}
	}
}

func closedDrop(bp int, end string) NudParser {
	return func(l *Lexer) Node {
		expr := parseUntil(l, bp, Token{"op", end})
		l.Advance()
		return expr
	}
}

func infix(op string, rbp int) LedParser {
	return func(l *Lexer, expr Node) Node {
		return &Binary{Op: op, Lhs: expr, Rhs: parseExpr(l, rbp)}
	}
}

func infixLeft(op string, bp int) LedParser {
	return infix(op, bp+1)
}

func infixRight(op string, bp int) LedParser {
	return infix(op, bp)
}

func postfix(lbp int, op string) LedParser {
	return func(l *Lexer, expr Node) Node {
		return &Unary{Op: op, Arg: expr}
	}
}

var nud map[string]func(*Lexer) Node
var led map[string]func(*Lexer, Node) Node
var lbp map[string]int

func init() {
	nud = map[string]func(*Lexer) Node{
		"+": prefix("pos", 5),
		"-": prefix("neg", 5),
		"(": closedDrop(0, ")"),
	}
	led = map[string]func(*Lexer, Node) Node{
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

func parsePrim(lexer *Lexer, tok Token) Node {
	switch tok.Kind {
	case "ident", "num":
		lexer.Advance()
		return &Term{Kind: tok.Kind, Value: tok.Value}
	}
	panic("Unexpected token")
}

func parseExpr(lexer *Lexer, bp int) Node {
	var expr Node
	tok := lexer.Peek()
	if tok.Kind == "op" {
		if parseNud := nud[tok.Value]; parseNud != nil {
			lexer.Advance()
			expr = parseNud(lexer)
		} else {
			expr = parsePrim(lexer, tok)
		}
	} else {
		expr = parsePrim(lexer, tok)
	}
	tok = lexer.Peek()
	for tok.Kind == "op" {
		parseLed := led[tok.Value]
		if parseLed == nil || lbp[tok.Value] < bp {
			break
		}
		lexer.Advance()
		expr = parseLed(lexer, expr)
		tok = lexer.Peek()
	}
	return expr
}

func Parse(src string) Node {
	lexer := NewLexer([]byte(src), tokens, eof)
	return parseUntil(lexer, 0, eof)
}

func parseUntil(l *Lexer, bp int, tok Token) Node {
	expr := parseExpr(l, bp)
	if l.Peek() != tok {
		panic("Unexpected token")
	}
	return expr
}
