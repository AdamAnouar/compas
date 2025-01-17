
********************************************************************************
compas.scene
********************************************************************************

.. currentmodule:: compas.scene

.. rst-class:: lead


This package defines scene objects for visualising COMPAS objects.
Every object type is paired with a corresponding scene object type that is capable of visualizing the data of the object.
The scene objects are implemented as pluggables, and automatically switch between plugins depending on the contexct in which they are used.


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    SceneObject
    DataSceneObjectNotRegisteredError
    GeometryObject
    MeshObject
    NetworkObject
    NoSceneObjectContextError
    VolMeshObject


Pluggables
==========

Pluggables are functions that don't have an actual implementation, but receive an implementation from a plugin.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    clear
    redraw
    register_scene_objects



