#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Frozen:
    def __init__(self):
        self._frozen = False

    def freeze(self):
        self._frozen = True

    def __setattr__(self, key: str, value):
        if getattr(self, '_frozen', False) is True:
            attr = getattr(self, key)
            if attr is not None:
                super().__setattr__(key, value)
            else:
                raise AssertionError('Frozen')
        else:
            super().__setattr__(key, value)