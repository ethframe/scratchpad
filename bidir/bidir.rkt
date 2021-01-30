#lang racket
(require redex)

(require pict)
(require file/convertible)


;; A simply typed λ-calculus from
;; Dunfield J., Krishnaswami N. Bidirectional typing
;; //arXiv preprint arXiv:1908.05839. – 2019.

(define-language λ
  (e x
     (λ x e)
     (e e)
     ()
     (e : T))
  ((T A B C) unit
             (T → T))
  (x variable-not-otherwise-mentioned))


;; Typing context

(define-extended-language λ+Γ λ
  (Γ ((x T) ...)))


;; Helpers

(define-metafunction λ+Γ
  lookup : Γ x -> T
  [(lookup ((x_o _) ... (x T) _ ...) x)
   T
   (side-condition (not (member (term x) (term (x_o ...)))))]
  [(lookup _ x) ,(error 'lookup "not found: ~e" (term x))])

(define-metafunction λ+Γ
  extend : Γ (x T) ... -> Γ
  [(extend ((x_Γ T_Γ) ...) (x T) ...) ((x T) ... (x_Γ T_Γ) ...)])

(define-metafunction λ+Γ
  equal-types? : T T -> boolean
  [(equal-types? T T) #t]
  [(equal-types? _ _) #f])


;; Bidirectional typing rules

(define-judgment-form
  λ+Γ
  #:mode (check I I I)
  #:contract (check Γ e T)
  [(synth Γ e A)
   (side-condition (equal-types? A B))
   ----------------------------------- sub-⇐
   (check Γ e B)]

  [------------------ unit-i-⇐
   (check Γ () unit)]

  [(check (extend Γ (x A_1)) e A_2)
   -------------------------------- →-i-⇐
   (check Γ (λ x e) (A_1 → A_2))])


(define-judgment-form
  λ+Γ
  #:mode (synth I I O)
  #:contract (synth Γ e T)
  [------------------------ var-⇒
   (synth Γ x (lookup Γ x))]

  [(check Γ e A)
   ------------------- anno-⇒
   (synth Γ (e : A) A)]
  
  [(synth Γ e_1 (A → B))
   (check Γ e_2 A)
   --------------------- →-e-⇒
   (synth Γ (e_1 e_2) B)])


;; Test typing

(test-judgment-holds
 (check () () unit))

(test-judgment-holds
 (synth
  ((x (unit → unit)))
  x
  (unit → unit)))

(test-judgment-holds
 (synth
  ((x (unit → unit)))
  (x ())
  unit))

(test-results)


;; Render everything to file

(define rendered
  (vl-append
   10
   (language->pict λ)
   (language->pict λ+Γ)
   (metafunction->pict lookup #:contract? #t)
   (metafunction->pict extend #:contract? #t)
   (metafunction->pict equal-types? #:contract? #t)
   (judgment-form->pict check)
   (judgment-form->pict synth)))

(with-output-to-file
    "bidir.pdf"
  (lambda ()
    (write-bytes
     (convert rendered 'pdf-bytes))))
