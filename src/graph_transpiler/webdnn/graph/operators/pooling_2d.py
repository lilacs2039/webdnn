from typing import Optional, Tuple

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.util import console


class Pooling2D(Operator):
    """Pooling2D(name, ksize, stride, padding)

    Spatial pooling base operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    Signature

        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)

    def __call__(self, x: Variable):
        self.append_input("x", x)
        return self.exec()

    def exec(self):
        x = self.inputs["x"]
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] + 2 * self.PH + self.SH - self.KH - 1) // self.SH + 1
        W2 = (x_shape_dict[Axis.W] + 2 * self.PW + self.SW - self.KW - 1) // self.SW + 1
        C2 = x_shape_dict[Axis.C]
        if ((x_shape_dict[Axis.H] + 2 * self.PH - self.KH) % self.SH != 0) or \
            ((x_shape_dict[Axis.W] + 2 * self.PW - self.KW) % self.SW != 0):
            # https://github.com/fchollet/keras/issues/5090#issuecomment-279495401
            console.warning(
                "[Pooling2D] Performing pooling with parameters which causes edge is ignored. " +
                "Which edge (left / right) is ignored is different on frameworks," +
                " so slightly different result will be generated.")

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_output("y", y)

        for axis in x.order.axes:
            if axis == Axis.H or axis == Axis.W:
                continue

            self.attributes.add(Tensorwise(self, axis))

        return y,

    @property
    def ksize(self) -> Tuple[int, int]:
        return self.parameters["ksize"]

    @property
    def stride(self) -> Tuple[int, int]:
        return self.parameters["stride"]

    @property
    def padding(self) -> Tuple[int, int]:
        return self.parameters["padding"]

    @property
    def KH(self) -> int:
        return self.ksize[0]

    @property
    def KW(self) -> int:
        return self.ksize[1]

    @property
    def SH(self) -> int:
        return self.stride[0]

    @property
    def SW(self) -> int:
        return self.stride[1]

    @property
    def PH(self) -> int:
        return self.padding[0]

    @property
    def PW(self) -> int:
        return self.padding[1]
