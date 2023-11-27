from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc  # type: ignore

from compas.scene import GeometryObject
from compas.colors import Color
from compas_rhino.conversions import sphere_to_rhino
from compas_rhino.conversions import transformation_to_rhino
from .sceneobject import RhinoSceneObject
from ._helpers import attributes


class SphereObject(RhinoSceneObject, GeometryObject):
    """Sceneobject for drawing sphere shapes.

    Parameters
    ----------
    sphere : :class:`compas.geometry.Sphere`
        A COMPAS sphere.
    **kwargs : dict, optional
        Additional keyword arguments.

    """

    def __init__(self, sphere, **kwargs):
        super(SphereObject, self).__init__(geometry=sphere, **kwargs)

    def draw(self, color=None):
        """Draw the sphere associated with the sceneobject.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the sphere.

        Returns
        -------
        System.Guid
            The GUID of the object created in Rhino.

        """
        color = Color.coerce(color) or self.color
        attr = attributes(name=self.geometry.name, color=color, layer=self.layer)
        geometry = sphere_to_rhino(self.geometry)
        if self.transformation:
            geometry.Transform(transformation_to_rhino(self.transformation))

        return sc.doc.Objects.AddSphere(geometry, attr)
