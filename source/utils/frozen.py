#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Frozen:
    def __init__(self):
        self._frozen = False

    def freeze(self):
        self._frozen = True

    def __setattr__(self, key: str, value):
        if getattr(self, '_frozen', False) is True:
            has_attr = hasattr(self, key)
            if has_attr:
                super().__setattr__(key, value)
            else:
                raise AssertionError('Frozen')
        else:
            super().__setattr__(key, value)