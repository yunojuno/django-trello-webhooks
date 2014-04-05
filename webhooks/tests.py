# # -*- coding: utf-8 -*-
# from django.test import TestCase

# from core.models import Parent, Child, Unrelated


# class CascadeDeleteTests(TestCase):

#     def setUp(self):
#         self.parent = Parent(name="Joe")
#         self.parent.save()
#         self.child = Child(name="John-Boy", parent=self.parent)
#         self.child.save()

#     def test_delete_child(self):
#         """Delete the child object only."""
#         self.child.delete()
#         # confirm that child has been deleted
#         self.assertTrue(Parent.objects.exists())
#         self.assertFalse(Child.objects.exists())

#     def test_delete_parent_cascades(self):
#         """Call the parent.delete() method."""
#         self.parent.delete()
#         # confirm that child has been deleted has been deleted
#         self.assertFalse(Parent.objects.exists())
#         self.assertFalse(Child.objects.exists())

#     def test_delete_parent_cascade_multiple(self):
#         """Call the parent.delete() method with many children."""
#         Child(name=u"Bob", parent=self.parent).save()
#         Child(name=u"Gob", parent=self.parent).save()
#         Child(name=u"Lob", parent=self.parent).save()
#         self.parent.delete()
#         # confirm that child has been deleted has been deleted
#         self.assertFalse(Parent.objects.exists())
#         self.assertFalse(Child.objects.exists())

#     def test_delete_parent_child_fail(self):
#         """Call the parent.delete() and fail on a child delete."""
#         Child(name=u"Bob", parent=self.parent).save()
#         Child(name=u"Gob", parent=self.parent).save()
#         Child(name=u"Lob", parent=self.parent).save()
#         Child(name=u"Job", parent=self.parent).save()
#         self.assertRaises(Exception, self.parent.delete)
#         # confirm that nothing has been deleted
#         self.assertTrue(Parent.objects.exists())
#         self.assertEqual(Child.objects.count(), 5)

#     def test_delete_parent_parent_fail(self):
#         """Call the parent.delete() and fail on parent deletion."""
#         self.parent.name=u"Job"
#         self.parent.save()
#         self.assertRaises(Exception, self.parent.delete)
#         # confirm that nothing has been deleted
#         self.assertTrue(Parent.objects.exists())
#         self.assertEqual(Child.objects.count(), 1)

#     def test_delete_everything(self):
#         """Call the parent.delete() and fail on parent deletion."""
#         Child(name="Baby", parent=self.parent).save()
#         Unrelated(name="Igor").save()
#         self.parent.delete()
#         # confirm that everything has been deleted.
#         self.assertFalse(Parent.objects.exists())
#         self.assertFalse(Child.objects.exists())
#         self.assertFalse(Unrelated.objects.exists())

#     def test_delete_everything_fail(self):
#         """Call the parent.delete() and fail on parent deletion."""
#         Child(name="Baby", parent=self.parent).save()
#         Child(name="Job", parent=self.parent).save()
#         Unrelated(name="Igor").save()
#         self.assertRaises(Exception, self.parent.delete)
#         # confirm that everything has been deleted.
#         self.assertTrue(Parent.objects.exists())
#         self.assertTrue(Child.objects.exists())
#         self.assertTrue(Unrelated.objects.exists())
