((python-mode . ((eglot-server-programs    . ((python-mode "~/Software/Python/anaconda3/envs/twaml/bin/pyls")))
                 (company-backends         . (company-capf))
                 (python-shell-interpreter . "~/Software/Python/anaconda3/envs/twaml/bin/python")
                 (eval . (add-hook 'before-save-hook #'eglot-format-buffer))
                 ;;(py-shell-name . "~/Software/Python/anaconda3/envs/twaml/bin/python")
                 ;;(py-ipython-command . "~/Software/Python/anaconda3/envs/twaml/bin/ipython")
                 )))
