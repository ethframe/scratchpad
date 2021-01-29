#lang racket
(require redex)

(require pict)
(require file/convertible)


;; A simply typed λ-calculus from
;; Dunfield J., Krishnaswami N. Bidirectional typing
;; //arXiv preprint arXiv:1908.05839. – 2019.

(define-language λ
  (e ::=
     x
     (λ x e)
     (e e)
     ()
     (: e T))
  (T A B C ::=
     unit
     (→ T T))
  (x ::= variable-not-otherwise-mentioned))


;; Typing context

(define-extended-language λ+Γ λ
  (Γ ::=
     ·
     ((: x T) Γ)))


;; Helpers

(define-metafunction λ+Γ
  lookup : Γ x -> T
  [(lookup ((: x T) _) x) T]
  [(lookup (_ Γ) x) (lookup Γ x)]
  [(lookup · x) ,(error 'lookup "not found: ~e" (term x))])


(define-metafunction λ+Γ
  equal-types? : T T -> boolean
  [(equal-types? T T) #t]
  [(equal-types? _ _) #f])


;; Bidirectional typing rules

(define-judgment-form
  λ+Γ
  #:mode (type-⇐ I I I)
  #:contract (type-⇐ Γ e T)
  [(type-⇒ Γ e A)
   (side-condition (equal-types? A B))
   ----------------------------------- sub-⇐
   (type-⇐ Γ e B)]

  [------------------ unit-i-⇐
   (type-⇐ Γ () unit)]

  [(type-⇐ ((: x A_1) Γ) e A_2)
   ------------------------------ →-i-⇐
   (type-⇐ Γ (λ x e) (→ A_1 A_2))])


(define-judgment-form
  λ+Γ
  #:mode (type-⇒ I I O)
  #:contract (type-⇒ Γ e T)
  [------------------------- var-⇒
   (type-⇒ Γ x (lookup Γ x))]

  [(type-⇐ Γ e A)
   -------------------- anno-⇒
   (type-⇒ Γ (: e A) A)]
  
  [(type-⇒ Γ e_1 (→ A B))
   (type-⇐ Γ e_2 A)
   ---------------------- →-e-⇒
   (type-⇒ Γ (e_1 e_2) B)])


;; Test typing

(test-judgment-holds
 (type-⇐ · () unit))

(test-judgment-holds
 (type-⇒
  ((: x (→ unit unit)) ·)
  x
  (→ unit unit)))

(test-judgment-holds
 (type-⇒
  ((: x (→ unit unit)) ·)
  (x ())
  unit))

(test-results)


;; Render everything to file

(with-output-to-file
    "bidir.pdf"
  (lambda ()
    (write-bytes
     (convert (vl-append
               10
               (language->pict λ)
               (language->pict λ+Γ)
               (metafunction->pict lookup #:contract? #t)
               (metafunction->pict equal-types? #:contract? #t)
               (judgment-form->pict type-⇐)
               (judgment-form->pict type-⇒))
              'pdf-bytes))))
