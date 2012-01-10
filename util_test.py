#!/usr/bin/python
"""Unit tests for util.py.
"""

__author__ = ['Ryan Barrett <bridgy@ryanb.org>']

import datetime
import unittest

import testutil
import util
from util import KeyNameModel, Handler

from google.appengine.ext import db


class UtilTest(testutil.ModelsTest):

  def test_reduce_url(self):
    for url in ('http://a.org/b/c?d=e&f=g', 'https://a.org/b/c',
                'http://a.org/b/c/', 'http://a.org/b/c'):
      self.assertEqual('a.org/b/c', util.reduce_url(url))

    self.assertEqual('a.org', util.reduce_url('http://a.org/'))
    self.assertEqual('a.org', util.reduce_url('http://a.org'))
    self.assertEqual('asdf', util.reduce_url('asdf'))

  def test_favicon_for_url(self):
    for url in ('http://a.org/b/c?d=e&f=g', 'https://a.org/b/c', 'http://a.org/'):
      self.assertEqual('http://a.org/favicon.ico', util.favicon_for_url(url))

  def test_make_poll_task_name(self):
    # microseconds should be dropped
    source = testutil.FakeSource.new(
      None, last_polled=datetime.datetime.utcfromtimestamp(0.1))
    expected_task_name = str(source.key()) + '_1970-01-01-00-00-00'
    self.assertEqual(expected_task_name, util.make_poll_task_name(source))


class KeyNameModelTest(testutil.TestbedTest):

  def test_constructor(self):
    # with key name is ok
    entity = KeyNameModel(key_name='x')
    entity.save()
    db.get(entity.key())

    # without key name is not ok
    self.assertRaises(AssertionError, KeyNameModel)


class HandlerTest(testutil.HandlerTest):

  def _test_redirect(self, uri, messages, expected_location):
    self.handler.messages = messages
    self.handler.redirect(uri)
    self.assertEqual(302, self.response.status)
    self.assertEqual('http://HOST' + expected_location,
                     self.response.headers['Location'])

  def test_redirect(self):
    self._test_redirect('/', [], '/')

  def test_redirect_with_messages(self):
    self._test_redirect('/', ['foo', 'bar'], '/?msg=foo&msg=bar')

  def test_redirect_with_query_params_and_messages(self):
    self._test_redirect('/?x=y', [], '/?x=y')

  def test_redirect_with_query_params_and_messages(self):
    self._test_redirect('/?x=y&msg=baz', ['foo', 'bar'],
                        '/?x=y&msg=baz&msg=foo&msg=bar')
