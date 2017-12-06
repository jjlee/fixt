import itertools

import fixt

from unittest import TestCase


class TestFactory(TestCase):

    def make_factory(self):
        return fixt.Factory(self.addCleanup, self)

    def make_factory_with_fixture_and_child_factory(self, make_fixture):
        factory = self.make_factory()

        def make_factory_maker(makers):
            def maker(factory):
                return factory.make_child_factory(makers)
            return maker

        def make_makers():
            return [('spam', make_fixture)]

        factory.add_maker('spam', make_fixture)
        makers = [('spam', make_fixture)]
        factory.add_maker('child', make_factory_maker(makers))
        return factory

    def test_namespace(self):
        factory = self.make_factory_with_fixture_and_child_factory(
            lambda factory: 'spam'
        )
        child = factory.child
        self.assertEqual(type(child), fixt.Factory)
        self.assertIs(child, factory.child)
        self.assertEqual(child.spam, 'spam')

    def test_namespace_called_once(self):
        counter = itertools.count()
        factory = self.make_factory_with_fixture_and_child_factory(
            lambda factory: next(counter)
        )
        self.assertEqual(factory.child.spam, 0)
        self.assertEqual(factory.child.spam, 0)

    def test_namespace_partial_copy_has_no_hidden_state(self):
        # An earlier implementation had a special top-level Factory which had
        # state that would still be there even after a partial copy that
        # did not explicitly request that it be copied
        factory = self.make_factory()
        counter = itertools.count()
        factory.add_maker(
            'products',
            lambda factory: factory.make_child_factory(
                [('product', lambda factory: next(counter))]
            )
        )
        def make_order(factory):
            return 'order for product ' + str(factory.products.product)
        factory.add_maker(
            'sales',
            lambda factory: factory.make_child_factory([('so', make_order)])
        )
        so = factory.sales.so
        new_factory = factory.partial_copy([])
        new_so = new_factory.sales.so
        self.assertEqual(so, 'order for product 0')
        self.assertEqual(new_so, 'order for product 1')

    def test_cross_namespace_partial_copy(self):
        # .partial_copy involving two makers in different namespaces
        # (products. and sales.).  sales.so depends on product.product.
        factory = self.make_factory()
        product_counter = itertools.count()
        so_counter = itertools.count()
        def make_product(factory):
            return next(product_counter)
        factory.add_maker(
            'products',
            lambda factory: factory.make_child_factory(
                [('product', make_product)]
            )
        )
        def make_order(factory):
            return 'order %d for product %d' % (
                next(so_counter),
                factory.products.product
            )
        factory.add_maker(
            'sales',
            lambda factory: factory.make_child_factory([('so', make_order)])
        )
        so = factory.sales.so
        new_factory = factory.partial_copy(['products.product'])
        new_so = new_factory.sales.so
        # Only the product was copied
        self.assertEqual(so, 'order 0 for product 0')
        self.assertEqual(new_so, 'order 1 for product 0')

    def test_namespace_partial_copy(self):
        # It is possible to copy an entire namespace.  This is implemented in
        # exactly the same way as for non-Factory fixtures.
        factory = self.make_factory()
        grommet_counter = itertools.count()
        flange_counter = itertools.count()
        def make_factory_maker(makers):
            def maker(factory):
                return factory.make_child_factory(makers)
            return maker
        def make_grommet(factory):
            return next(grommet_counter)
        factory.add_maker(
            'widgets',
            make_factory_maker([
                (
                    'doodads',
                    make_factory_maker([('grommet', make_grommet)])
                )
            ])
        )
        def make_flange(factory):
            return 'flange %d for grommet %d' % (
                next(flange_counter),
                factory.widgets.doodads.grommet
            )
        factory.add_maker(
            'spam',
            make_factory_maker([('flange', make_flange)])
        )
        flange = factory.spam.flange
        new_factory = factory.partial_copy(['widgets'])
        new_flange = new_factory.spam.flange
        # The grommet was copied because it is a descendant of widgets (via
        # doodads: factory.widgets.doodads.grommet)
        self.assertEqual(flange, 'flange 0 for grommet 0')
        self.assertEqual(new_flange, 'flange 1 for grommet 0')

    def test_maker_not_added(self):
        factory = self.make_factory()
        self.assertRaises(AttributeError, getattr, factory, 'bob')

    def test_maker_called(self):
        factory = self.make_factory()
        factory.add_maker('bob', lambda factory: 'Bob')
        self.assertEqual(factory.bob, 'Bob')

    def test_maker_called_once(self):
        factory = self.make_factory()
        counter = itertools.count()
        factory.add_maker('bob', lambda factory: next(counter))
        self.assertEqual(factory.bob, 0)
        self.assertEqual(factory.bob, 0)

    def test_dependency(self):
        # This is not really a feature of fixt, but it is its main use case.
        factory = self.make_factory()
        factory.add_maker('bob', lambda factory: factory.alice + ' and Bob')
        factory.add_maker('alice', lambda factory: 'Alice')
        # Creating bob creates its dependency, alice, too.
        self.assertEqual(factory.bob, 'Alice and Bob')
        self.assertIn('alice', factory._made)
        self.assertIn('bob', factory._made)
        self.assertEqual(factory.alice, 'Alice')

    def test_set(self):
        factory = self.make_factory()
        factory.add_maker('bob', lambda factory: 'Bob')
        factory.set('bob', 'Alice')
        self.assertEqual(factory.bob, 'Alice')

    def test_set_already_made_object(self):
        factory = self.make_factory()
        factory.add_maker('bob', lambda factory: 'Bob')
        factory.bob
        with self.assertRaises(ValueError):
            factory.set('bob', 'Alice')

    def test_add_already_added_maker(self):
        factory = self.make_factory()
        factory.add_maker('bob', lambda factory: 'Bob')
        with self.assertRaises(ValueError):
            factory.add_maker('bob', lambda factory: 'Bob')

    def test_set_unknown_object(self):
        factory = self.make_factory()
        self.assertRaises(ValueError, factory.set, 'bob', 'Alice')

    def test_set_does_not_support_dotted_names(self):
        factory = self.make_factory_with_fixture_and_child_factory(
            lambda factory: 'Bob'
        )
        # Dotted names have no special meaning for .set(), so we get ValueError
        # because there is no maker whose name is 'child.spam' (with a literal
        # dot as opposed to dot used as namespace syntax)
        with self.assertRaises(ValueError):
            factory.set('child.spam', 'Alice')

    def test_helper_add_constant(self):
        factory = self.make_factory()
        helper = fixt.MakerSetHelper()
        helper.add_constant('db_name', 'my-db')
        for name, maker in helper.makers:
            factory.add_maker(name, maker)
        self.assertEqual(factory.db_name, 'my-db')

    def test_cannot_setattr_for_maker_name(self):
        factory = self.make_factory()
        factory.add_maker('spam', lambda f: 'spam')
        with self.assertRaises(AttributeError):
            factory.spam = 'ham'
