package expressions

import (
	"reflect"
	"testing"
)

func TestParse(t *testing.T) {
	type args struct {
		src string
	}
	tests := []struct {
		name string
		args args
		want Node
	}{
		{"add", args{"a + b + c"}, &Binary{
			Op: "add",
			Lhs: &Binary{
				Op:  "add",
				Lhs: &Term{Kind: "ident", Value: "a"},
				Rhs: &Term{Kind: "ident", Value: "b"},
			},
			Rhs: &Term{Kind: "ident", Value: "c"},
		}},
		{"add_paren", args{"a + (b + c)"}, &Binary{
			Op:  "add",
			Lhs: &Term{Kind: "ident", Value: "a"},
			Rhs: &Binary{
				Op:  "add",
				Lhs: &Term{Kind: "ident", Value: "b"},
				Rhs: &Term{Kind: "ident", Value: "c"},
			},
		}},
		{"mul_add", args{"a * b + c"}, &Binary{
			Op: "add",
			Lhs: &Binary{
				Op:  "mul",
				Lhs: &Term{Kind: "ident", Value: "a"},
				Rhs: &Term{Kind: "ident", Value: "b"},
			},
			Rhs: &Term{Kind: "ident", Value: "c"},
		}},
		{"mul_add_2", args{"a + b * c"}, &Binary{
			Op:  "add",
			Lhs: &Term{Kind: "ident", Value: "a"},
			Rhs: &Binary{
				Op:  "mul",
				Lhs: &Term{Kind: "ident", Value: "b"},
				Rhs: &Term{Kind: "ident", Value: "c"},
			},
		}},
		{"neg_add", args{"-a + b"}, &Binary{
			Op:  "add",
			Lhs: &Unary{Op: "neg", Arg: &Term{Kind: "ident", Value: "a"}},
			Rhs: &Term{Kind: "ident", Value: "b"},
		}},
		{"neg_pow", args{"-a ^ b"}, &Binary{
			Op:  "pow",
			Lhs: &Unary{Op: "neg", Arg: &Term{Kind: "ident", Value: "a"}},
			Rhs: &Term{Kind: "ident", Value: "b"},
		}},
		{"pow_pow", args{"a ^ b ^ c"}, &Binary{
			Op:  "pow",
			Lhs: &Term{Kind: "ident", Value: "a"},
			Rhs: &Binary{
				Op:  "pow",
				Lhs: &Term{Kind: "ident", Value: "b"},
				Rhs: &Term{Kind: "ident", Value: "c"},
			},
		}},
		{"neg_fact", args{"-a!"}, &Unary{
			Op:  "neg",
			Arg: &Unary{Op: "fact", Arg: &Term{Kind: "ident", Value: "a"}},
		}},
		{"neg_fact_2", args{"(-a)!"}, &Unary{
			Op:  "fact",
			Arg: &Unary{Op: "neg", Arg: &Term{Kind: "ident", Value: "a"}},
		}},
		{"neg_neg_pos", args{"--+a"}, &Unary{
			Op: "neg",
			Arg: &Unary{
				Op:  "neg",
				Arg: &Unary{Op: "pos", Arg: &Term{Kind: "ident", Value: "a"}},
			},
		}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Parse(tt.args.src); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Parse() = %v, want %v", got, tt.want)
			}
		})
	}
}
