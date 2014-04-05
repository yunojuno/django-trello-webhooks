Django Cascade Delete
=====================

Test Django project used to explore transaction handling in model deletions.

There has been some discussion within the YunoJuno development team about
the use of signals within the Django model ORM framework, whether it's
good practice, or even safe to rely on, when processing side-effects.

The primary use case is the cascading deletion of models, and how this is
handled internally by the Django ORM. An initial investigation of the [Django
source](https://github.com/django/django/blob/master/django/db/models/deletion.py#L242)
suggested that when calling the `delete` method of a top-level object 
(one that is a parent of a child object), the child's `delete` method
is never called, but its `pre_delete` and `post_delete` signals are:

```python
def delete(self):
    [...]
    # send pre_delete signals
    for model, obj in self.instances_with_model():
        [...]
        signals.pre_delete.send([...])

    [...]

    # delete instances
    for model, instances in six.iteritems(self.data):
        query = sql.DeleteQuery(model)
        [...]
        for obj in instances:
            signals.post_delete.send([...])
    [...]
```

The open question is where to put code that needs to run when an object is
deleted, but not directly (i.e. as part of a cascade). For instance, if
you need to delete other objects, that are *not* part of the implicit
cascade delete, should you put that code into the child model's `delete`
method, or in a signal receiver?

This project is a test app used to explore this in more detail.

It consists of a simple Django app with two models - Parent, and Child.
The Child model has a ForeignKey relationship to the Parent model. There
are `pre_delete` and `post_delete` signal receive handlers for both models.

In both `pre_delete` handlers, if the `name` attribute of the model is "Job"
an exception is raised. This is used to force the rollback of any containing
transactions, so that, in theory, if you call `parent.delete()` on a Parent
object that has a Child object with `name=="Job"`, the entire transaction
will rollback to its original state.

In addition to the test coverage, each method contains verbose logging
that can be used to highlight the methods being run at any time.

The suggested test verbosity is '2', e.g.

```bash
$ python manage.py test --verbosity=2
```

##Spoiler

This is the output from calling `delete` on an object with three child objects:

```python
>>> parent = Parent(name=u"Fred")
>>> parent.save()
>>> Child(name=u"Bob", parent=parent).save()
>>> Child(name=u"Gob", parent=parent).save()
>>> Child(name=u"Lob", parent=parent).save()
>>> parent.delete()
DEBUG Enter Parent.delete() method.
DEBUG Deleting Child: Bob.  # pre_delete signal
DEBUG Deleting Child: Gob.
DEBUG Deleting Child: Lob.
DEBUG Deleting Parent: Fred.
DEBUG Deleted Child: Lob.  # post_delete signal
DEBUG Deleted Child: Gob.
DEBUG Deleted Child: Bob.
DEBUG Deleted Parent: Fred.
DEBUG Exit Parent.delete() method.
```

This confirms the observations from the source code above:

* Child objects' `pre_delete` signals are fired
* The Child objects' `delete` methods are **not** called
* Child objects' `post_delete` signales are fired
* Parent signals are fired *after* related child signals

##Django Source

The Django source is freely available on [Github](https://github.com/django/django/), and the relevant code for the ORM cascade `delete` is in the [django.db.models.deletion.Collector](https://github.com/django/django/blob/master/django/db/models/deletion.py#L242) class.


##Prerequisites

There is a `requirements.txt` file that contains the project dependencies.

**NB** `psycopg2` is only required when running the tests agains a Postgres
database - which is recommended because of the transactional support (given
that that is the whole point of the project). However, you can run the tests
against SQLite if you wish (database settings just need to the uncommented).
