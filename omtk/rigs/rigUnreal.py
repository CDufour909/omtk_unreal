import logging
import pymel.core as pymel
from omtk import constants
from omtk.core import classRig
from omtk.core import className
from omtk.libs import libPymel

log = logging.getLogger("omtk")


class UnrealNomenclature(className.BaseName):
    root_jnt_name = "root"
    scalar_root_name = "scalar_root_jnt"

    def __init__(self, *args, **kwargs):
        super(UnrealNomenclature, self).__init__(*args, **kwargs)


class RigUnreal(classRig.Rig):
    """
    Custom rig implementation in respect to Unreal engine.
    """

    DEFAULT_UPP_AXIS = constants.Axis.z
    LEGACY_ARM_IK_CTRL_ORIENTATION = True
    LEGACY_LEG_IK_CTRL_ORIENTATION = True

    def __init__(self, *args, **kwargs):
        super(RigUnreal, self).__init__(*args, **kwargs)
        self._color_ctrl = True
        self.scene_root = None

    def _get_nomenclature_cls(self):
        """
        :return: Return the UnrealNomenclature class
        """
        return UnrealNomenclature

    def pre_build(self):
        """
        Pre build routine before the rig is build

        :return:
        """
        super(RigUnreal, self).pre_build(create_master_grp=True, create_layer_jnt=True)

        #
        # Create scalar joint to flip export from maya to unreal
        #

        # Build the scene root
        if pymel.objExists(self.nomenclature.scalar_root_name):
            self.scene_root = pymel.PyNode(self.nomenclature.scalar_root_name)
        else:
            self.scene_root = pymel.joint(name=self.nomenclature.scalar_root_name)
            self.scene_root.attr("jointOrientX").set(-90)
            # Setup the scalar root

    def post_build(self):
        """
        Call at the end of the rigging process. Nothing is done in the basic rig class, but certain
        rig definition could need it. Need to be call really at the end to ensure this is the latest
        things applied on the rig
        """
        super(RigUnreal, self).post_build()

        # Try to parent the root joint to the scene root
        if self.scene_root:
            pymel.parent(self.scene_root, world=True)

        if self.grp_jnt:
            self.grp_jnt.setParent(self.scene_root)
        else:
            log.error(
                "Root joint {} could not be found. Rig export for Unreal will fail".format(
                    self.nomenclature.root_jnt_name
                )
            )

    def post_build_module(self, module):
        """
        Additional changes on the different module built for the rig

        :param module: The built module on which we want to do additional changes
        """
        super(RigUnreal, self).post_build_module(module)

        # Allow animators to change the rotate order if needed
        for ctrl in module.get_ctrls():
            if libPymel.is_valid_PyNode(ctrl):
                ctrl.node.rotateOrder.setKeyable(True)

    def _unbuild_nodes(self):
        """
        Unbuild the different created node for the rig

        :return:
        """
        if self.scene_root:
            pymel.parent(self.scene_root, world=True)
        super(RigUnreal, self)._unbuild_nodes()


def register_plugin():
    return RigUnreal
