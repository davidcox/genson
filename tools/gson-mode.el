; A Combination of Hacks to Provide Syntax Coloring and Indentation for GenSON
; Zak Stone
; 8.7.11

; First, bootstrap with define-generic-mode as described here:
;
; http://emacs-fu.blogspot.com/2010/04/creating-custom-modes-easy-way-with.html
; http://www.emacswiki.org/emacs/GenericMode

(require 'generic-x)

(define-generic-mode 
  'gson-base-mode                 ;; name of the mode to create
  '("#")                          ;; comments start with '!!'
  '("root" "parent" "this"
    "grid" "gaussian" "uniform")  ;; some keywords
  '((":" . 'font-lock-operator)   ;; '=' is an operator
    (";" . 'font-lock-builtin))   ;; ';' is a built-in 
  '("\\.gson_base$")              ;; files for which to activate this mode 
  nil                             ;; other functions to call
  "Syntax-highlighting base mode for GenSON files" 
                                  ;; doc string for this mode
  )


; Next, adapt code from StackOverflow to handle indentation:
;
; http://stackoverflow.com/questions/4158216/emacs-custom-indentation

(define-derived-mode gson-mode gson-base-mode "GenSON"
  "Mode for editing GenSON with indentation."
  (make-local-variable 'gson-indent-offset)
  (set (make-local-variable 'indent-line-function) 'gson-indent-line))

(defvar gson-indent-offset 4
  "*Indentation offset for `gson-mode'.")

(defvar gson-debug nil)

(defun gson-indent-line ()
  "Indent current line for `gson-mode'."
  (interactive)
  (let ((indent-col 0))
    (save-excursion
      (beginning-of-line)
      (condition-case nil
          (while t
            (backward-up-list 1)
            (when (looking-at "[[{]")
	      (if gson-debug
		  (setq old-indent indent-col))
              (setq indent-col (+ indent-col gson-indent-offset))
	      (if gson-debug
		  (message "1st step: old indent %d, curr indent %d"
			   old-indent indent-col))))
	(error nil)))
    (save-excursion
      (if gson-debug
	  (setq old-indent indent-col))
      (back-to-indentation)
      (when (and (looking-at "[]}]") (>= indent-col gson-indent-offset))
        (setq indent-col (- indent-col gson-indent-offset))
	(if gson-debug
	    (message "2nd step: old indent %d, curr indent %d"
		     old-indent indent-col))))
    (indent-line-to indent-col)))

(provide 'gson-mode)